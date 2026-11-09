-- Integration tests for the live grant functions. No auth accounts or emails.
-- Every synthetic row is rolled back; run after shared_lifetime_free_trials.
begin;
set local statement_timeout = '30s';
set local role service_role;

do $$
declare
  programme text;
  other_programme text;
  email_address text;
  first_result record;
  next_result record;
  before_access jsonb;
  after_access jsonb;
  product_name text;
  mode text;
  test_expiry timestamptz;
  legacy_results jsonb;
begin
  foreach programme in array array['tmua', 'esat', 'ib'] loop
    email_address := 'lifetime-qa-' || programme || '@example.invalid';
    assert not exists(select 1 from trial_private.email_trial_claims where email = email_address),
      'Fixture already exists: use an isolated test transaction';

    execute format('select * from public.grant_%s_free_trial($1,$2)', programme)
      into first_result using '  ' || upper(email_address) || '  ', 'Trial QA';
    assert first_result.out_status = 'trial_started', 'First trial did not start';
    assert first_result.out_email = email_address, 'Email was not normalized';
    assert first_result.out_expires_at = first_result.out_started_at + interval '48 hours',
      'Trial length changed';
    select jsonb_agg(to_jsonb(sa) order by sa.product) into before_access
      from public.student_access sa where lower(sa.email) = email_address;

    execute format('select * from public.grant_%s_free_trial($1,$2)', programme)
      into next_result using upper(email_address), 'Different name';
    assert next_result.out_status = 'trial_already_active', 'Active retry failed';
    assert next_result.out_started_at = first_result.out_started_at
      and next_result.out_expires_at = first_result.out_expires_at, 'Active retry reset dates';

    foreach other_programme in array array['tmua', 'esat', 'ib'] loop
      if other_programme <> programme then
        execute format('select * from public.grant_%s_free_trial($1,$2)', other_programme)
          into next_result using ' ' || upper(email_address) || ' ', 'Trial QA';
        assert next_result.out_status = 'trial_already_used', 'Cross-portal repeat was allowed';
      end if;
    end loop;
    select jsonb_agg(to_jsonb(sa) order by sa.product) into after_access
      from public.student_access sa where lower(sa.email) = email_address;
    assert before_access = after_access, 'Repeat changed access';
    assert (select count(*) from trial_private.email_trial_claims where email = email_address) = 1,
      'Email has multiple claims';

    -- Email delivery metadata and ended statuses must remain writable.
    execute format('update public.%s_free_trials set updated_at = now(), started_email_sent_at = now() where email = $1', programme)
      using email_address;
    begin
      execute format('update public.%s_free_trials set expires_at = expires_at + interval ''1 day'' where email = $1', programme)
        using email_address;
      raise exception 'Date reset was allowed';
    exception when check_violation then null;
    end;
    begin
      execute format('update public.%s_free_trials set email = $1 where email = $2', programme)
        using 'changed-' || email_address, email_address;
      raise exception 'Email transfer was allowed';
    exception when check_violation then null;
    end;

    execute format('delete from public.%s_free_trials where email = $1', programme) using email_address;
    delete from public.student_access where email = email_address;
    execute format('select * from public.grant_%s_free_trial($1,$2)', programme)
      into next_result using email_address, 'Trial QA';
    assert next_result.out_status = 'trial_already_used', 'Deleting old records restored eligibility';
    assert not exists(select 1 from public.student_access where email = email_address),
      'Denied restart recreated access';
    begin
      execute format('insert into public.%s_free_trials (email,started_at,expires_at) values ($1,now(),now()+interval ''48 hours'')', programme)
        using email_address;
      raise exception 'Direct history insertion bypassed lifetime rule';
    exception when unique_violation then null;
    end;

    -- An expired claim is refused on every portal, without changing access.
    email_address := 'lifetime-qa-expired-' || programme || '@example.invalid';
    execute format('insert into public.%s_free_trials (email,started_at,expires_at,status) values ($1,now()-interval ''3 days'',now()-interval ''1 day'',''expired'')', programme)
      using email_address;
    foreach other_programme in array array['tmua', 'esat', 'ib'] loop
      execute format('select * from public.grant_%s_free_trial($1,$2)', other_programme)
        into next_result using email_address, 'Trial QA';
      assert next_result.out_status = 'trial_already_used', 'Expired repeat was allowed';
    end loop;

    -- Permanent, long-lived, and near-expiry paid access stay byte-for-byte intact.
    foreach mode in array array['permanent', 'long', 'short'] loop
      email_address := 'lifetime-qa-paid-' || programme || '-' || mode || '@example.invalid';
      product_name := case programme when 'tmua' then 'tmua-question-bank'
        when 'esat' then 'esat-question-bank' else 'ib-portal' end;
      test_expiry := case mode when 'permanent' then null when 'long' then now() + interval '30 days'
        else now() + interval '1 hour' end;
      insert into public.student_access (email,product,approved,expires_at,access_source,student_name)
        values (email_address,product_name,true,test_expiry,'stripe','Paid Student');
      select to_jsonb(sa) into before_access from public.student_access sa
        where email = email_address and product = product_name;
      execute format('select * from public.grant_%s_free_trial($1,$2)', programme)
        into next_result using email_address, 'Trial QA';
      assert next_result.out_status = 'trial_started', 'Eligible paid email did not claim first trial';
      select to_jsonb(sa) into after_access from public.student_access sa
        where email = email_address and product = product_name;
      assert before_access = after_access, 'Paid access was modified';
    end loop;
  end loop;

  -- Both TMUA overloads share one history and preserve the legacy response shape.
  email_address := 'lifetime-qa-legacy@example.invalid';
  select jsonb_agg(to_jsonb(g) order by out_product) into legacy_results
    from public.grant_tmua_free_trial(email_address) g;
  assert jsonb_array_length(legacy_results) = 2, 'Legacy return shape changed';
  assert legacy_results->0->>'out_status' = 'trial_started'
    and legacy_results->1->>'out_status' = 'trial_started', 'Legacy first grant failed';
  select * into next_result from public.grant_tmua_free_trial(upper(email_address), 'QA');
  assert next_result.out_status = 'trial_already_active', 'Legacy and modern history diverged';
  select * into next_result from public.grant_esat_free_trial(email_address, 'QA');
  assert next_result.out_status = 'trial_already_used', 'Legacy grant bypassed cross-portal restriction';
  assert not exists(select 1 from public.tmua_free_trial_claims where email = email_address),
    'Legacy wrapper created an independent grant';

  email_address := 'lifetime-qa-old-legacy@example.invalid';
  insert into public.tmua_free_trial_claims (email,trial_started_at,trial_expires_at)
    values (email_address,now()-interval '3 days',now()-interval '1 day');
  select * into next_result from public.grant_tmua_free_trial(email_address, 'QA');
  assert next_result.out_status = 'trial_already_used', 'Old legacy history was ignored';
  select * into next_result from public.grant_ib_free_trial(email_address, 'QA');
  assert next_result.out_status = 'trial_already_used', 'Old legacy history allowed IB';

  -- An interrupted transaction cannot consume eligibility or leave partial access.
  email_address := 'lifetime-qa-rollback@example.invalid';
  begin
    perform public.grant_ib_free_trial(email_address, 'QA');
    raise exception 'Simulated interrupted signup' using errcode = 'P1234';
  exception when sqlstate 'P1234' then null;
  end;
  assert not exists(select 1 from trial_private.email_trial_claims where email = email_address),
    'Failed signup retained its claim';
  assert not exists(select 1 from public.ib_free_trials where email = email_address),
    'Failed signup retained trial history';
  assert not exists(select 1 from public.student_access where email = email_address),
    'Failed signup retained access';

  -- Invalid input never consumes a claim.
  select * into next_result from public.grant_ib_free_trial('not-an-email', 'QA');
  assert next_result.out_status = 'invalid_email', 'Invalid email was accepted';
  begin
    perform public.grant_tmua_free_trial('not-an-email');
    raise exception 'Legacy invalid email was accepted';
  exception when invalid_parameter_value then null;
  end;

  assert not has_table_privilege('service_role', 'trial_private.email_trial_claims', 'UPDATE')
    and not has_table_privilege('service_role', 'trial_private.email_trial_claims', 'DELETE')
    and not has_table_privilege('service_role', 'trial_private.email_trial_claims', 'TRUNCATE'),
    'Service role can erase trial eligibility history';
end;
$$;

reset role;
do $$
declare role_name text; function_name text;
begin
  foreach role_name in array array['anon','authenticated'] loop
    assert not has_schema_privilege(role_name, 'trial_private', 'USAGE'), 'Private schema exposed';
    assert not has_table_privilege(role_name, 'trial_private.email_trial_claims', 'SELECT')
      and not has_table_privilege(role_name, 'trial_private.email_trial_claims', 'INSERT'),
      'Trial ledger exposed';
    foreach function_name in array array[
      'public.grant_tmua_free_trial(text)', 'public.grant_tmua_free_trial(text,text)',
      'public.grant_esat_free_trial(text,text)', 'public.grant_ib_free_trial(text,text)'
    ] loop
      assert not has_function_privilege(role_name, function_name, 'EXECUTE'),
        'Browser role can grant trials directly';
    end loop;
  end loop;
end;
$$;
select 'PASS: lifetime trials, all portal pairs, both TMUA paths, expiry, deletion, paid access, rollback and permissions' as result;
rollback;
