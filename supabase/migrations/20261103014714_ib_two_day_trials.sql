-- Two-day IB trials. Existing authenticated users retain their pre-launch access.
-- New accounts require an unexpired IB entitlement. No cron job is needed.
create table public.ib_free_trials (
 id uuid primary key default gen_random_uuid(),
 email text not null unique check (email = lower(btrim(email))),
 student_name text, started_at timestamptz not null default now(),
 expires_at timestamptz not null default (now() + interval '48 hours'),
 started_email_sent_at timestamptz,
 status text not null default 'active' check (status in ('active','expired')),
 created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
 check (expires_at = started_at + interval '48 hours')
);
alter table public.ib_free_trials enable row level security;
revoke all on public.ib_free_trials from public, anon, authenticated;
grant all on public.ib_free_trials to service_role;

create table public.ib_legacy_access (
 user_id uuid primary key references auth.users(id) on delete cascade,
 granted_at timestamptz not null default now()
);
alter table public.ib_legacy_access enable row level security;
revoke all on public.ib_legacy_access from public, anon, authenticated;
grant select on public.ib_legacy_access to authenticated;
grant all on public.ib_legacy_access to service_role;
create policy ib_legacy_read_own on public.ib_legacy_access for select to authenticated
 using (user_id = (select auth.uid()));
insert into public.ib_legacy_access (user_id) select id from auth.users;

CREATE OR REPLACE FUNCTION public.grant_ib_free_trial(p_email text, p_student_name text DEFAULT NULL::text)
 RETURNS TABLE(out_status text, out_email text, out_student_name text, out_started_at timestamp with time zone, out_expires_at timestamp with time zone)
 LANGUAGE plpgsql
 SECURITY INVOKER
 SET search_path TO ''
AS $function$
declare
  v_email text := lower(trim(coalesce(p_email, '')));
  v_name text := nullif(trim(coalesce(p_student_name, '')), '');
  v_started_at timestamptz := now();
  v_expires_at timestamptz := now() + interval '2 days';
  v_existing record;
  v_product text;
begin
  if v_email = '' or v_email !~* '^[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}$' then
    return query
    select
      'invalid_email'::text,
      v_email,
      v_name,
      null::timestamptz,
      null::timestamptz;
    return;
  end if;

  perform pg_advisory_xact_lock(hashtextextended('ib_trial:' || v_email, 0));

  select *
  into v_existing
  from public.ib_free_trials
  where lower(email) = v_email
  limit 1;

  if found then
    return query
    select
      case
        when v_existing.expires_at > now()
          then 'trial_already_active'::text
        else 'trial_already_used'::text
      end,
      v_existing.email,
      coalesce(v_existing.student_name, v_name),
      v_existing.started_at,
      v_existing.expires_at;
    return;
  end if;

  insert into public.ib_free_trials (
    email,
    student_name,
    started_at,
    expires_at,
    status
  )
  values (
    v_email,
    v_name,
    v_started_at,
    v_expires_at,
    'active'
  );

  foreach v_product in array array['ib-portal']
  loop
    update public.student_access as sa
    set
      approved = true,
      expires_at = case
        when sa.approved = true
          and (sa.expires_at is null or sa.expires_at > v_expires_at)
          then sa.expires_at
        else v_expires_at
      end,
      access_source = case
        when sa.approved = true
          and (sa.expires_at is null or sa.expires_at > v_expires_at)
          then sa.access_source
        else 'ib_free_trial'
      end,
      student_name = case
        when sa.approved = true
          and (sa.expires_at is null or sa.expires_at > v_expires_at)
          then sa.student_name
        else coalesce(v_name, sa.student_name)
      end,
      updated_at = now()
    where lower(sa.email) = v_email
      and sa.product = v_product;

    if not found then
      insert into public.student_access (
        email,
        product,
        approved,
        expires_at,
        access_source,
        student_name
      )
      values (
        v_email,
        v_product,
        true,
        v_expires_at,
        'ib_free_trial',
        v_name
      );
    end if;
  end loop;

  return query
  select
    'trial_started'::text,
    v_email,
    v_name,
    v_started_at,
    v_expires_at;
end;
$function$
;
CREATE OR REPLACE FUNCTION public.mark_ib_trial_started_email_sent(p_email text)
 RETURNS void
 LANGUAGE sql
 SECURITY INVOKER
 SET search_path TO ''
AS $function$
  update public.ib_free_trials
  set
    started_email_sent_at = coalesce(started_email_sent_at, now()),
    updated_at = now()
  where lower(email) = lower(trim(coalesce(p_email, '')));
$function$
;
revoke execute on function public.grant_ib_free_trial(text,text) from public,anon,authenticated;
grant execute on function public.grant_ib_free_trial(text,text) to service_role;
revoke execute on function public.mark_ib_trial_started_email_sent(text) from public,anon,authenticated;
grant execute on function public.mark_ib_trial_started_email_sent(text) to service_role;

create function public.ib_access_state() returns text
language plpgsql stable security invoker set search_path = '' as $$
declare access_row public.student_access;
begin
 if (select auth.uid()) is null then return 'trial_required'; end if;
 select * into access_row from public.student_access
 where lower(email) = lower((select auth.jwt())->>'email') and product = 'ib-portal'
 limit 1;
 if found and access_row.approved is not true then return 'trial_required'; end if;
 if access_row.approved = true and (access_row.expires_at is null or access_row.expires_at > now()) then return 'active'; end if;
 if exists(select 1 from public.ib_legacy_access where user_id=(select auth.uid())) then return 'active'; end if;
 if access_row.expires_at is not null and access_row.expires_at <= now() then return 'trial_expired'; end if;
 return 'trial_required';
end; $$;
revoke execute on function public.ib_access_state() from public,anon;
grant execute on function public.ib_access_state() to authenticated,service_role;

-- Extend the existing paid-fulfilment function's product allowlist only.
CREATE OR REPLACE FUNCTION public.stripe_grant_student_access(target_email text, target_product text, target_expires_at timestamp with time zone DEFAULT NULL::timestamp with time zone, target_access_source text DEFAULT 'stripe'::text)
 RETURNS student_access
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO ''
AS $function$
DECLARE
  normalized_email text;
  granted_row public.student_access;
BEGIN
  normalized_email := lower(trim(target_email));

  IF normalized_email IS NULL OR normalized_email = '' THEN
    RAISE EXCEPTION 'Email cannot be blank';
  END IF;

  IF target_product NOT IN (
    'tmua-question-bank',
    'practice-tests',
    'tmua-classes',
    'esat-question-bank',
    'esat-practice-tests',
    'esat-classes',
    'amc-question-bank',
    'sat-question-bank',
    'sat-practice-tests',
    'ib-portal'
  ) THEN
    RAISE EXCEPTION 'Invalid Thriving Scholars product: %', target_product;
  END IF;

  INSERT INTO public.student_access
    (email, product, approved, expires_at, access_source, updated_at)
  VALUES
    (normalized_email, target_product, true, target_expires_at, target_access_source, now())
  ON CONFLICT ((lower(email)), product)
  DO UPDATE SET
    approved = true,
    expires_at = CASE
      WHEN public.student_access.expires_at IS NULL THEN NULL
      WHEN EXCLUDED.expires_at IS NULL THEN NULL
      ELSE greatest(public.student_access.expires_at, EXCLUDED.expires_at)
    END,
    access_source = EXCLUDED.access_source,
    updated_at = now()
  RETURNING * INTO granted_row;

  RETURN granted_row;
END;
$function$
;

