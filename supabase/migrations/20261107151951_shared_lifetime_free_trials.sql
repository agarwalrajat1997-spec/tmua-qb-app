-- One lifetime free trial per normalized email across TMUA, ESAT and IB.
-- Keep the claim independently of auth users, access rows and delivery metadata.
set local lock_timeout = '5s';
set local statement_timeout = '30s';

-- Serialize the historical snapshot with old grants while installing the guards.
lock table public.tmua_free_trials, public.esat_free_trials,
  public.ib_free_trials, public.tmua_free_trial_claims,
  public.student_access in share row exclusive mode;

create schema if not exists trial_private;
revoke all on schema trial_private from public, anon, authenticated;
grant usage on schema trial_private to service_role;

create table trial_private.email_trial_claims (
  email text primary key check (email = lower(btrim(email)) and email <> ''),
  first_programme text not null check (first_programme in ('tmua', 'esat', 'ib')),
  first_started_at timestamptz not null,
  first_expires_at timestamptz,
  recorded_at timestamptz not null default now()
);
alter table trial_private.email_trial_claims enable row level security;
revoke all on trial_private.email_trial_claims from public, anon, authenticated, service_role;
grant select, insert on trial_private.email_trial_claims to service_role;
comment on table trial_private.email_trial_claims is
  'Lifetime free-trial eligibility. Server-only, insert-only for service_role; intentionally no cascading auth/access foreign key.';

with trial_history as (
  select lower(btrim(email)) email, 'tmua'::text programme, started_at, expires_at
  from public.tmua_free_trials
  union all
  select lower(btrim(email)), 'esat', started_at, expires_at from public.esat_free_trials
  union all
  select lower(btrim(email)), 'ib', started_at, expires_at from public.ib_free_trials
  union all
  select lower(btrim(email)), 'tmua', trial_started_at, trial_expires_at
  from public.tmua_free_trial_claims
), history_with_access_fallback as (
  select * from trial_history
  union all
  -- Only explicit trial grants are evidence. Paid/manual expiry is not a trial.
  select lower(btrim(sa.email)), split_part(sa.access_source, '_', 1),
    sa.created_at, sa.expires_at
  from public.student_access sa
  where sa.access_source in ('tmua_free_trial', 'esat_free_trial', 'ib_free_trial')
    and not exists (select 1 from trial_history h where h.email = lower(btrim(sa.email)))
)
insert into trial_private.email_trial_claims
  (email, first_programme, first_started_at, first_expires_at)
select distinct on (email) email, programme, started_at, expires_at
from history_with_access_fallback
where email <> ''
order by email, started_at, programme;

-- All four historical write paths consume the same unique claim. The trigger
-- also protects dates from being reset while allowing notification/status writes.
create function trial_private.guard_trial_history() returns trigger
language plpgsql security invoker set search_path = '' as $$
declare
  v_started_at timestamptz;
  v_expires_at timestamptz;
begin
  new.email := lower(btrim(new.email));
  if tg_op = 'UPDATE' then
    if new.email is distinct from lower(btrim(old.email)) then
      raise exception 'A free trial cannot be transferred to another email' using errcode = '23514';
    end if;
    if tg_table_name = 'tmua_free_trial_claims' then
      if new.trial_started_at is distinct from old.trial_started_at
         or new.trial_expires_at is distinct from old.trial_expires_at then
        raise exception 'A free trial cannot be restarted or extended' using errcode = '23514';
      end if;
    elsif new.started_at is distinct from old.started_at
       or new.expires_at is distinct from old.expires_at then
      raise exception 'A free trial cannot be restarted or extended' using errcode = '23514';
    end if;
    return new;
  end if;

  if new.email is null or length(new.email) > 254
     or new.email !~* '^[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}$' then
    raise exception 'Invalid email address' using errcode = '22023';
  end if;
  if tg_table_name = 'tmua_free_trial_claims' then
    v_started_at := new.trial_started_at;
    v_expires_at := new.trial_expires_at;
  else
    v_started_at := new.started_at;
    v_expires_at := new.expires_at;
  end if;

  perform pg_advisory_xact_lock(hashtextextended('portal_free_trial:' || new.email, 0));
  insert into trial_private.email_trial_claims
    (email, first_programme, first_started_at, first_expires_at)
  values (new.email, tg_argv[0], v_started_at, v_expires_at)
  on conflict (email) do nothing;
  if not found then
    raise exception 'This email has already used its lifetime free trial' using errcode = '23505';
  end if;
  return new;
end;
$$;
revoke all on function trial_private.guard_trial_history() from public, anon, authenticated;
grant execute on function trial_private.guard_trial_history() to service_role;

create trigger guard_lifetime_trial before insert or update on public.tmua_free_trials
for each row execute function trial_private.guard_trial_history('tmua');
create trigger guard_lifetime_trial before insert or update on public.esat_free_trials
for each row execute function trial_private.guard_trial_history('esat');
create trigger guard_lifetime_trial before insert or update on public.ib_free_trials
for each row execute function trial_private.guard_trial_history('ib');
create trigger guard_lifetime_trial before insert or update on public.tmua_free_trial_claims
for each row execute function trial_private.guard_trial_history('tmua');

create function trial_private.grant_free_trial(
  p_programme text, p_email text, p_student_name text
) returns table(out_status text, out_email text, out_student_name text,
  out_started_at timestamptz, out_expires_at timestamptz)
language plpgsql security invoker set search_path = '' as $$
declare
  v_email text := lower(btrim(coalesce(p_email, '')));
  v_name text := nullif(btrim(coalesce(p_student_name, '')), '');
  v_started_at timestamptz := now();
  v_expires_at timestamptz := now() + interval '48 hours';
  v_existing record;
  v_claim trial_private.email_trial_claims%rowtype;
  v_products text[];
  v_product text;
begin
  if p_programme is null or p_programme not in ('tmua', 'esat', 'ib') then
    raise exception 'Invalid trial programme' using errcode = '22023';
  end if;
  if v_email = '' or length(v_email) > 254
     or v_email !~* '^[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}$' then
    return query select 'invalid_email'::text, v_email, v_name,
      null::timestamptz, null::timestamptz;
    return;
  end if;

  perform pg_advisory_xact_lock(hashtextextended('portal_free_trial:' || v_email, 0));

  -- An active repeat is a login retry, never a new access grant. Preserve old
  -- active windows even for emails that historically tried multiple programmes.
  select h.* into v_existing from (
    select t.email, t.student_name, t.started_at, t.expires_at,
      (t.status = 'active' and t.ended_email_sent_at is null) active, 0 priority
    from public.tmua_free_trials t
    where p_programme = 'tmua' and lower(btrim(t.email)) = v_email
    union all
    select t.email, t.student_name, t.started_at, t.expires_at, t.status = 'active', 0
    from public.esat_free_trials t
    where p_programme = 'esat' and lower(btrim(t.email)) = v_email
    union all
    select t.email, t.student_name, t.started_at, t.expires_at, t.status = 'active', 0
    from public.ib_free_trials t
    where p_programme = 'ib' and lower(btrim(t.email)) = v_email
    union all
    select t.email, null::text, t.trial_started_at, t.trial_expires_at, true, 1
    from public.tmua_free_trial_claims t
    where p_programme = 'tmua' and lower(btrim(t.email)) = v_email
  ) h order by h.priority, h.started_at limit 1;
  if found then
    return query select
      case when v_existing.active and v_existing.expires_at > now()
        then 'trial_already_active'::text else 'trial_already_used'::text end,
      v_email, coalesce(v_existing.student_name, v_name),
      v_existing.started_at, v_existing.expires_at;
    return;
  end if;

  select * into v_claim from trial_private.email_trial_claims where email = v_email;
  if found then
    return query select 'trial_already_used'::text, v_email, v_name,
      v_claim.first_started_at, v_claim.first_expires_at;
    return;
  end if;

  -- The history insert's trigger atomically claims the email. If any entitlement
  -- write fails, PostgreSQL rolls back the claim and trial together.
  case p_programme
    when 'tmua' then
      insert into public.tmua_free_trials (email, student_name, started_at, expires_at, status)
      values (v_email, v_name, v_started_at, v_expires_at, 'active');
      v_products := array['tmua-question-bank', 'practice-tests'];
    when 'esat' then
      insert into public.esat_free_trials (email, student_name, started_at, expires_at, status)
      values (v_email, v_name, v_started_at, v_expires_at, 'active');
      v_products := array['esat-question-bank', 'esat-classes'];
    when 'ib' then
      insert into public.ib_free_trials (email, student_name, started_at, expires_at, status)
      values (v_email, v_name, v_started_at, v_expires_at, 'active');
      v_products := array['ib-portal'];
  end case;

  foreach v_product in array v_products loop
    insert into public.student_access as sa
      (email, product, approved, expires_at, access_source, student_name, updated_at)
    values (v_email, v_product, true, v_expires_at, p_programme || '_free_trial', v_name, now())
    on conflict ((lower(email)), product) do update set
      approved = true,
      expires_at = excluded.expires_at,
      access_source = excluded.access_source,
      student_name = coalesce(excluded.student_name, sa.student_name),
      updated_at = excluded.updated_at
    -- Preserve approved paid/manual access, even when less than 48 hours remain,
    -- and never shorten any longer/permanent approved entitlement.
    where not (sa.approved and (
      sa.expires_at is null or sa.expires_at >= excluded.expires_at
      or (sa.expires_at > now() and coalesce(sa.access_source, 'manual')
        not in ('tmua_free_trial', 'esat_free_trial', 'ib_free_trial'))
    ));
  end loop;

  return query select 'trial_started'::text, v_email, v_name, v_started_at, v_expires_at;
end;
$$;
revoke all on function trial_private.grant_free_trial(text,text,text) from public, anon, authenticated;
grant execute on function trial_private.grant_free_trial(text,text,text) to service_role;

-- The existing DEFAULT on the two-argument TMUA overload makes one-argument
-- SQL calls ambiguous. No objects depend on this overload; recreate it without
-- DEFAULT, and preserve the explicit one-argument compatibility wrapper below.
drop function public.grant_tmua_free_trial(text,text);
create function public.grant_tmua_free_trial(p_email text, p_student_name text)
returns table(out_status text, out_email text, out_student_name text,
  out_started_at timestamptz, out_expires_at timestamptz)
language sql security invoker set search_path = '' as $$
  select * from trial_private.grant_free_trial('tmua', p_email, p_student_name);
$$;
create or replace function public.grant_esat_free_trial(p_email text, p_student_name text default null::text)
returns table(out_status text, out_email text, out_student_name text,
  out_started_at timestamptz, out_expires_at timestamptz)
language sql security invoker set search_path = '' as $$
  select * from trial_private.grant_free_trial('esat', p_email, p_student_name);
$$;
create or replace function public.grant_ib_free_trial(p_email text, p_student_name text default null::text)
returns table(out_status text, out_email text, out_student_name text,
  out_started_at timestamptz, out_expires_at timestamptz)
language sql security invoker set search_path = '' as $$
  select * from trial_private.grant_free_trial('ib', p_email, p_student_name);
$$;

-- Retain the legacy response shape, but remove its independent trial history.
create or replace function public.grant_tmua_free_trial(p_email text)
returns table(out_email text, out_product text, out_approved boolean,
  out_expires_at timestamptz, out_status text)
language plpgsql security invoker set search_path = '' as $$
declare v_result record;
begin
  select * into strict v_result from public.grant_tmua_free_trial(p_email, null::text);
  if v_result.out_status = 'invalid_email' then
    raise exception 'Invalid email address' using errcode = '22023';
  end if;
  return query select v_result.out_email::text, p.product,
    coalesce(sa.approved, false), sa.expires_at,
    case when v_result.out_status in ('trial_started', 'trial_already_active')
           and sa.approved and sa.expires_at is null
      then 'permanent_access_unchanged'::text else v_result.out_status::text end
  from (values ('tmua-question-bank'::text), ('practice-tests'::text)) p(product)
  left join public.student_access sa
    on lower(btrim(sa.email)) = v_result.out_email and sa.product = p.product;
end;
$$;

revoke all on function public.grant_tmua_free_trial(text,text) from public, anon, authenticated;
revoke all on function public.grant_tmua_free_trial(text) from public, anon, authenticated;
revoke all on function public.grant_esat_free_trial(text,text) from public, anon, authenticated;
revoke all on function public.grant_ib_free_trial(text,text) from public, anon, authenticated;
grant execute on function public.grant_tmua_free_trial(text,text) to service_role;
grant execute on function public.grant_tmua_free_trial(text) to service_role;
grant execute on function public.grant_esat_free_trial(text,text) to service_role;
grant execute on function public.grant_ib_free_trial(text,text) to service_role;

notify pgrst, 'reload schema';
