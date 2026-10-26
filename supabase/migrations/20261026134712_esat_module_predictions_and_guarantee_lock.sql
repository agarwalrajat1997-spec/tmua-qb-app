-- ESAT uses independently calculated module predictions. Students can read
-- their records; only the authenticated application server writes them.
create table public.esat_exam_plans (
  user_id uuid primary key references auth.users(id) on delete cascade,
  exam_date date not null,
  modules text[] not null,
  lock_at timestamptz not null,
  revision uuid not null default gen_random_uuid(),
  predictions jsonb,
  prediction_saved_at timestamptz,
  evidence_at timestamptz,
  model_version text,
  updated_at timestamptz not null default clock_timestamp(),
  check (cardinality(modules) = 3 and modules @> array['Mathematics 1']::text[]
    and modules <@ array['Mathematics 1','Mathematics 2','Physics','Chemistry','Biology']::text[]),
  check (lock_at = ((exam_date - 2)::timestamp at time zone 'Europe/London'))
);
create index esat_exam_plans_lock_at_idx on public.esat_exam_plans(lock_at);

create table public.esat_prediction_locks (
  user_id uuid not null references auth.users(id) on delete cascade,
  exam_date date not null,
  modules text[] not null,
  lock_at timestamptz not null,
  locked_at timestamptz not null default clock_timestamp(),
  predictions jsonb not null,
  prediction_saved_at timestamptz,
  evidence_at timestamptz,
  model_version text,
  policy_version text not null default 'esat-two-modules-half-point-v1',
  primary key (user_id, exam_date),
  check (jsonb_typeof(predictions) = 'array' and jsonb_array_length(predictions) = 3),
  check (prediction_saved_at is null or prediction_saved_at < lock_at),
  check (evidence_at is null or evidence_at < lock_at)
);

create table public.esat_result_submissions (
  user_id uuid not null,
  exam_date date not null,
  actual_scores jsonb not null,
  assessment jsonb not null,
  submitted_at timestamptz not null default clock_timestamp(),
  verification_status text not null default 'pending' check (verification_status in ('pending','verified','rejected')),
  primary key (user_id, exam_date),
  foreign key (user_id, exam_date) references public.esat_prediction_locks(user_id, exam_date) on delete cascade
);

alter table public.esat_exam_plans enable row level security;
alter table public.esat_prediction_locks enable row level security;
alter table public.esat_result_submissions enable row level security;
revoke all on public.esat_exam_plans, public.esat_prediction_locks, public.esat_result_submissions from anon, authenticated;
grant select on public.esat_exam_plans, public.esat_prediction_locks, public.esat_result_submissions to authenticated;
grant all on public.esat_exam_plans, public.esat_prediction_locks, public.esat_result_submissions to service_role;
create policy esat_plan_read_own on public.esat_exam_plans for select to authenticated using ((select auth.uid()) = user_id);
create policy esat_locks_read_own on public.esat_prediction_locks for select to authenticated using ((select auth.uid()) = user_id);
create policy esat_results_read_own on public.esat_result_submissions for select to authenticated using ((select auth.uid()) = user_id);

create function public.esat_guard_prediction_lock() returns trigger
language plpgsql security invoker set search_path = '' as $$
begin
  raise exception 'Locked ESAT predictions are immutable.';
end;
$$;
create trigger esat_prediction_lock_immutable before update on public.esat_prediction_locks
for each row execute function public.esat_guard_prediction_lock();

-- Invoker permissions are intentional. These RPCs are callable only by the
-- server's service_role. Identity is taken from the verified session by the API.
create function public.esat_lock_due_predictions(p_user_id uuid default null) returns integer
language plpgsql security invoker set search_path = '' as $$
declare
  plan public.esat_exam_plans%rowtype;
  frozen jsonb;
  inserted integer := 0;
  affected integer;
begin
  for plan in select p.* from public.esat_exam_plans p
    where (p_user_id is null or p.user_id = p_user_id) and p.lock_at <= clock_timestamp()
      and not exists (select 1 from public.esat_prediction_locks l where l.user_id = p.user_id and l.exam_date = p.exam_date)
    for update of p
  loop
    frozen := plan.predictions;
    if frozen is null then
      select jsonb_agg(jsonb_build_object('module', m, 'score', null, 'confidence', null,
        'lowerBound', null, 'upperBound', null, 'independentTestCount', 0,
        'qbUniqueQuestions', 0, 'qbTopicCoverage', 0, 'guaranteeEligible', false, 'inputHash', '') order by ord)
      into frozen from unnest(plan.modules) with ordinality as choices(m, ord);
    end if;
    insert into public.esat_prediction_locks(user_id, exam_date, modules, lock_at, predictions,
      prediction_saved_at, evidence_at, model_version)
    values (plan.user_id, plan.exam_date, plan.modules, plan.lock_at, frozen,
      plan.prediction_saved_at, plan.evidence_at, plan.model_version)
    on conflict (user_id, exam_date) do nothing;
    get diagnostics affected = row_count;
    inserted := inserted + affected;
  end loop;
  return inserted;
end;
$$;

create function public.esat_save_exam_plan(p_user_id uuid, p_exam_date date, p_modules text[]) returns void
language plpgsql security invoker set search_path = '' as $$
declare
  previous public.esat_exam_plans%rowtype;
  cutoff timestamptz := (p_exam_date - 2)::timestamp at time zone 'Europe/London';
begin
  if p_exam_date is null or p_modules is null or cardinality(p_modules) <> 3
    or (select count(distinct module) from unnest(p_modules) module) <> 3
    or array_position(p_modules, null) is not null
    or not (p_modules @> array['Mathematics 1']::text[] and p_modules <@ array['Mathematics 1','Mathematics 2','Physics','Chemistry','Biology']::text[]) then
    raise exception 'Choose Mathematics 1 and exactly two other ESAT modules.';
  end if;
  -- Serialize even the first plan insert, when no row exists yet.
  perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(p_user_id::text, 0));
  perform public.esat_lock_due_predictions(p_user_id);
  select * into previous from public.esat_exam_plans where user_id = p_user_id for update;
  if found and previous.lock_at <= clock_timestamp()
    and previous.exam_date >= (clock_timestamp() at time zone 'Europe/London')::date then
    raise exception 'Your exam details and predictions are locked for this sitting. Contact Thriving Scholars if your booking has changed.';
  end if;
  if cutoff <= clock_timestamp() then
    raise exception 'Save your exam details before the lock date, two days before the exam.';
  end if;
  if exists (select 1 from public.esat_prediction_locks where user_id = p_user_id and exam_date = p_exam_date) then
    raise exception 'This exam sitting already has locked predictions.';
  end if;
  if previous.exam_date = p_exam_date and previous.modules = p_modules then return; end if;
  insert into public.esat_exam_plans(user_id, exam_date, modules, lock_at)
  values (p_user_id, p_exam_date, p_modules, cutoff)
  on conflict (user_id) do update set exam_date = excluded.exam_date, modules = excluded.modules,
    lock_at = excluded.lock_at, revision = gen_random_uuid(), predictions = null,
    prediction_saved_at = null, evidence_at = null, model_version = null, updated_at = clock_timestamp();
end;
$$;

create function public.esat_save_module_predictions(p_user_id uuid, p_revision uuid, p_predictions jsonb,
  p_model_version text, p_evidence_at timestamptz) returns void
language plpgsql security invoker set search_path = '' as $$
declare
  plan public.esat_exam_plans%rowtype;
begin
  select * into plan from public.esat_exam_plans where user_id = p_user_id for update;
  if not found or plan.revision <> p_revision then raise exception 'Your exam details changed. Refresh your predictions.'; end if;
  -- A slow request started before the cutoff must never overwrite the lock.
  if clock_timestamp() >= plan.lock_at then
    perform public.esat_lock_due_predictions(p_user_id);
    return;
  end if;
  if p_predictions is null or jsonb_typeof(p_predictions) <> 'array' or jsonb_array_length(p_predictions) <> 3
    or p_evidence_at is null or p_evidence_at >= plan.lock_at or p_evidence_at > clock_timestamp()
    or coalesce(p_model_version, '') = '' then raise exception 'Invalid module prediction snapshot.'; end if;
  if (select array_agg(value->>'module' order by ord) from jsonb_array_elements(p_predictions) with ordinality as item(value, ord)) is distinct from plan.modules then
    raise exception 'Prediction modules do not match the exam booking.';
  end if;
  -- Out-of-order requests cannot replace a more recent evidence snapshot.
  if plan.evidence_at is not null and p_evidence_at < plan.evidence_at then return; end if;
  update public.esat_exam_plans set predictions = p_predictions, prediction_saved_at = clock_timestamp(),
    evidence_at = p_evidence_at, model_version = p_model_version where user_id = p_user_id;
end;
$$;

revoke all on function public.esat_guard_prediction_lock() from public, anon, authenticated;
revoke all on function public.esat_lock_due_predictions(uuid) from public, anon, authenticated;
revoke all on function public.esat_save_exam_plan(uuid,date,text[]) from public, anon, authenticated;
revoke all on function public.esat_save_module_predictions(uuid,uuid,jsonb,text,timestamptz) from public, anon, authenticated;
grant execute on function public.esat_lock_due_predictions(uuid) to service_role;
grant execute on function public.esat_save_exam_plan(uuid,date,text[]) to service_role;
grant execute on function public.esat_save_module_predictions(uuid,uuid,jsonb,text,timestamptz) to service_role;

-- Freezes the latest server-saved, displayed prediction even when the student
-- never opens the portal near the deadline. The cutoff, not job run time,
-- determines which snapshot qualifies. All subsequent reads also enforce it.
select cron.schedule('esat-lock-module-predictions', '* * * * *', 'select public.esat_lock_due_predictions();');
