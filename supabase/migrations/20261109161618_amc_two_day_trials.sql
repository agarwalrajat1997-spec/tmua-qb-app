-- One 48-hour AMC trial per normalized email. Access expires at request time;
-- no expiry job is needed, and approved paid access is never shortened.
create table public.amc_free_trials (
  id uuid primary key default gen_random_uuid(),
  email text not null unique check (email = lower(btrim(email))),
  student_name text,
  started_at timestamptz not null default now(),
  expires_at timestamptz not null default (now() + interval '48 hours'),
  started_email_sent_at timestamptz,
  status text not null default 'active' check (status in ('active', 'expired')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (expires_at = started_at + interval '48 hours')
);
alter table public.amc_free_trials enable row level security;
revoke all on public.amc_free_trials from public, anon, authenticated;
grant select, insert, update on public.amc_free_trials to service_role;

-- Explicit underlying privileges for the service-only invoker functions.
grant select, insert, update on public.student_access to service_role;
grant usage on sequence public.student_access_id_seq to service_role;

create function public.grant_amc_free_trial(p_email text, p_student_name text default null)
returns table (
  out_status text, out_email text, out_student_name text,
  out_started_at timestamptz, out_expires_at timestamptz
)
language plpgsql security invoker set search_path = '' as $$
declare
  v_email text := lower(btrim(coalesce(p_email, '')));
  v_name text := nullif(btrim(coalesce(p_student_name, '')), '');
  v_started_at timestamptz := now();
  v_expires_at timestamptz := now() + interval '48 hours';
  v_existing public.amc_free_trials;
begin
  if v_email = '' or length(v_email) > 254 or
     v_email !~* '^[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}$' then
    return query select 'invalid_email'::text, v_email, v_name, null::timestamptz, null::timestamptz;
    return;
  end if;

  perform pg_advisory_xact_lock(hashtextextended('amc_trial:' || v_email, 0));
  select * into v_existing from public.amc_free_trials where email = v_email;
  if found then
    return query select
      case when v_existing.expires_at > now() then 'trial_already_active'::text
           else 'trial_already_used'::text end,
      v_existing.email, coalesce(v_existing.student_name, v_name),
      v_existing.started_at, v_existing.expires_at;
    return;
  end if;

  insert into public.amc_free_trials (email, student_name, started_at, expires_at)
  values (v_email, v_name, v_started_at, v_expires_at);

  -- The existing normalized unique index makes this atomic with paid grants.
  insert into public.student_access as sa
    (email, product, approved, expires_at, access_source, student_name, updated_at)
  values (v_email, 'amc-question-bank', true, v_expires_at, 'amc_free_trial', v_name, now())
  on conflict ((lower(email)), product) do update set
    approved = true,
    expires_at = case
      when sa.approved and (sa.expires_at is null or sa.expires_at >= v_expires_at)
        then sa.expires_at else v_expires_at end,
    access_source = case
      when sa.approved and (sa.expires_at is null or sa.expires_at >= v_expires_at)
        then sa.access_source else 'amc_free_trial' end,
    student_name = case
      when sa.approved and (sa.expires_at is null or sa.expires_at >= v_expires_at)
        then sa.student_name else coalesce(v_name, sa.student_name) end,
    updated_at = now();

  return query select 'trial_started'::text, v_email, v_name, v_started_at, v_expires_at;
end;
$$;

create function public.mark_amc_trial_started_email_sent(p_email text)
returns void language sql security invoker set search_path = '' as $$
  update public.amc_free_trials
  set started_email_sent_at = coalesce(started_email_sent_at, now()), updated_at = now()
  where email = lower(btrim(coalesce(p_email, '')));
$$;

revoke execute on function public.grant_amc_free_trial(text, text) from public, anon, authenticated;
grant execute on function public.grant_amc_free_trial(text, text) to service_role;
revoke execute on function public.mark_amc_trial_started_email_sent(text) from public, anon, authenticated;
grant execute on function public.mark_amc_trial_started_email_sent(text) to service_role;
