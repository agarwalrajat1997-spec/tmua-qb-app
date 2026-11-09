-- Run against a migrated test database. Every fixture is rolled back; no mail is sent.
begin;
set local plpgsql.check_asserts = on;
do $test$
declare
  suffix text := replace(gen_random_uuid()::text, '-', '');
  email_new text := 'new-' || suffix || '@example.invalid';
  email_used text := 'used-' || suffix || '@example.invalid';
  email_long text := 'long-' || suffix || '@example.invalid';
  email_permanent text := 'permanent-' || suffix || '@example.invalid';
  email_unapproved text := 'unapproved-' || suffix || '@example.invalid';
  first_trial record;
  result record;
  access_row public.student_access;
  marker_at timestamptz := now() - interval '1 minute';
begin
  assert not (select prosecdef from pg_proc where oid = 'public.grant_amc_free_trial(text,text)'::regprocedure),
    'Grant must use invoker privileges';
  assert not (select prosecdef from pg_proc where oid = 'public.mark_amc_trial_started_email_sent(text)'::regprocedure),
    'Email marker must use invoker privileges';
  assert (select relrowsecurity from pg_class where oid = 'public.amc_free_trials'::regclass),
    'Trial metadata must have RLS enabled';
  assert not has_function_privilege('anon', 'public.grant_amc_free_trial(text,text)', 'EXECUTE'),
    'Anonymous callers cannot grant trials directly';
  assert not has_function_privilege('authenticated', 'public.grant_amc_free_trial(text,text)', 'EXECUTE'),
    'Signed-in callers cannot grant trials directly';
  assert has_function_privilege('service_role', 'public.grant_amc_free_trial(text,text)', 'EXECUTE'),
    'Server service role can grant trials';

  select * into strict first_trial from public.grant_amc_free_trial('  ' || upper(email_new) || '  ', '  Example Student  ');
  assert first_trial.out_status = 'trial_started', 'First request starts the trial';
  assert first_trial.out_email = email_new, 'Email normalization is stable';
  assert first_trial.out_student_name = 'Example Student', 'Name is trimmed';
  assert first_trial.out_expires_at - first_trial.out_started_at = interval '48 hours', 'Trial lasts exactly 48 hours';
  select * into strict access_row from public.student_access where lower(email) = email_new;
  assert access_row.product = 'amc-question-bank', 'Only the AMC entitlement is added';
  assert access_row.approved and access_row.expires_at = first_trial.out_expires_at, 'AMC is approved with matching expiry';
  assert access_row.access_source = 'amc_free_trial', 'Trial entitlement is identifiable';

  select * into strict result from public.grant_amc_free_trial(upper(email_new), 'Changed Name');
  assert result.out_status = 'trial_already_active', 'Repeat request is idempotent';
  assert result.out_started_at = first_trial.out_started_at and result.out_expires_at = first_trial.out_expires_at,
    'Repeat requests cannot extend the trial';
  assert (select count(*) from public.amc_free_trials where email = email_new) = 1, 'One trial per normalized email';
  assert (select count(*) from public.student_access where lower(email) = email_new) = 1, 'No duplicate or other-program grants';

  update public.amc_free_trials set started_email_sent_at = marker_at where email = email_new;
  perform public.mark_amc_trial_started_email_sent(' ' || upper(email_new) || ' ');
  assert (select started_email_sent_at from public.amc_free_trials where email = email_new) = marker_at,
    'Resend markers preserve the first successful email time';

  insert into public.amc_free_trials(email, started_at, expires_at, status)
  values (email_used, now() - interval '72 hours', now() - interval '24 hours', 'expired');
  select * into strict result from public.grant_amc_free_trial(email_used, 'Used Trial');
  assert result.out_status = 'trial_already_used', 'Expired trials cannot restart';
  assert not exists(select 1 from public.student_access where lower(email) = email_used),
    'Expired request does not grant access';

  insert into public.student_access(email, product, approved, expires_at, access_source, student_name)
  values (upper(email_long), 'amc-question-bank', true, now() + interval '30 days', 'paid_fixture', 'Paid Student');
  perform public.grant_amc_free_trial(email_long, 'Trial Name');
  select * into strict access_row from public.student_access where lower(email) = email_long;
  assert access_row.approved and access_row.expires_at = now() + interval '30 days', 'Longer paid access is preserved';
  assert access_row.access_source = 'paid_fixture' and access_row.student_name = 'Paid Student', 'Paid source/name are preserved';

  insert into public.student_access(email, product, approved, expires_at, access_source, student_name)
  values (email_permanent, 'amc-question-bank', true, null, 'paid_permanent_fixture', 'Permanent Student');
  insert into public.student_access(email, product, approved, expires_at, access_source)
  values (email_permanent, 'tmua-question-bank', true, now() + interval '90 days', 'other_program_fixture');
  perform public.grant_amc_free_trial(email_permanent, 'Trial Name');
  select * into strict access_row from public.student_access where email = email_permanent and product = 'amc-question-bank';
  assert access_row.approved and access_row.expires_at is null, 'Permanent paid access stays permanent';
  assert access_row.access_source = 'paid_permanent_fixture' and access_row.student_name = 'Permanent Student',
    'Permanent paid metadata is preserved';
  assert (select access_source = 'other_program_fixture' and expires_at = now() + interval '90 days'
    from public.student_access where email = email_permanent and product = 'tmua-question-bank'),
    'Other programme access is untouched';

  insert into public.student_access(email, product, approved, expires_at, access_source)
  values (email_unapproved, 'amc-question-bank', false, null, 'unapproved_fixture');
  select * into strict result from public.grant_amc_free_trial(email_unapproved, null);
  select * into strict access_row from public.student_access where email = email_unapproved;
  assert access_row.approved and access_row.expires_at = result.out_expires_at,
    'Unapproved null-expiry access becomes a finite trial, never permanent';

  select * into strict result from public.grant_amc_free_trial('not-an-email', null);
  assert result.out_status = 'invalid_email', 'Invalid email is rejected';
  assert not exists(select 1 from public.amc_free_trials where email = 'not-an-email'), 'Invalid input makes no trial';
end;
$test$;
rollback;
