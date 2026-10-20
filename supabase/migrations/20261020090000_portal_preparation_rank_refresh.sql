-- Refresh coordination only. Predictor/rank formulas and append-only history
-- remain unchanged. Never expose another student's snapshot to a browser.
create table public.portal_preparation_rank_refresh (
  programme text primary key check (programme in ('tmua','esat')),
  lease_token uuid,
  lease_until timestamptz not null default '-infinity',
  next_attempt_at timestamptz not null default '-infinity',
  refreshed_at timestamptz,
  run_id uuid references public.tmua_preparation_rank_runs(id),
  last_error text
);
alter table public.portal_preparation_rank_refresh enable row level security;
revoke all on public.portal_preparation_rank_refresh from public, anon, authenticated, service_role;
grant select, insert, update on public.portal_preparation_rank_refresh to service_role;

create function public.claim_portal_rank_refresh(p_programme text)
returns uuid language plpgsql security invoker set search_path = '' as $$
declare v_token uuid;
begin
  if p_programme not in ('tmua','esat') then raise exception 'Unknown programme'; end if;
  insert into public.portal_preparation_rank_refresh(programme) values(p_programme)
    on conflict do nothing;
  update public.portal_preparation_rank_refresh
    set lease_token = gen_random_uuid(), lease_until = now() + interval '10 minutes'
    where programme = p_programme and lease_until <= now() and next_attempt_at <= now()
      and (refreshed_at is null or refreshed_at <= now() - interval '30 minutes')
    returning lease_token into v_token;
  return v_token;
end;
$$;

create function public.finish_portal_rank_refresh(p_programme text, p_token uuid, p_run_id uuid)
returns boolean language plpgsql security invoker set search_path = '' as $$
declare v_run public.tmua_preparation_rank_runs; v_count integer; v_updated integer;
begin
  select * into v_run from public.tmua_preparation_rank_runs where id = p_run_id;
  if not found or v_run.model_version <> (case p_programme
    when 'tmua' then 'tmua-preparation-rank-v1-20260810'
    when 'esat' then 'esat-preparation-rank-v1-20260819' else '' end) then
    raise exception 'Invalid ranking run';
  end if;
  select count(*) into v_count from public.tmua_preparation_rank_snapshots
    where run_id = p_run_id and model_version = v_run.model_version;
  if v_count <> v_run.active_cohort_size then raise exception 'Incomplete ranking run'; end if;
  update public.portal_preparation_rank_refresh
    set run_id = p_run_id, refreshed_at = now(), lease_token = null,
      lease_until = '-infinity', next_attempt_at = '-infinity', last_error = null
    where programme = p_programme and lease_token = p_token;
  get diagnostics v_updated = row_count;
  return v_updated = 1;
end;
$$;

create function public.fail_portal_rank_refresh(p_programme text, p_token uuid)
returns void language sql security invoker set search_path = '' as $$
  update public.portal_preparation_rank_refresh
    set lease_token = null, lease_until = '-infinity',
      next_attempt_at = now() + interval '5 minutes', last_error = 'Refresh failed; see server logs'
    where programme = p_programme and lease_token = p_token;
$$;

-- Invoked only by the authenticated server handler, never by a client key.
-- Email and UUID must come from the server-verified auth session, not from
-- request parameters or editable profile metadata. Service role only.
create function public.read_portal_preparation_rank(p_programme text, p_user_id uuid, p_email text)
returns jsonb language plpgsql stable security invoker set search_path = '' as $$
declare v_state public.portal_preparation_rank_refresh;
  v_snapshot public.tmua_preparation_rank_snapshots;
  v_model text; v_cohort integer; v_empty jsonb;
begin
  v_model := case p_programme when 'tmua' then 'tmua-preparation-rank-v1-20260810'
    when 'esat' then 'esat-preparation-rank-v1-20260819' else null end;
  if v_model is null then raise exception 'Unknown programme'; end if;
  v_empty := jsonb_build_object('modelVersion',v_model,'hasGenuinePreparationEvidence',false,
    'score',null,'rank',null,'cohortSize',0,'components',null,'calculatedAt',now());
  if not exists (
    select 1 from public.student_access a
    where lower(trim(a.email)) = lower(trim(p_email)) and a.approved is true
      and (a.expires_at is null or a.expires_at > now())
      and a.product = any(case p_programme when 'tmua'
        then array['practice-tests','tmua-question-bank','tmua-classes']
        else array['esat-practice-tests','esat-question-bank','esat-classes'] end)
  ) then return v_empty; end if;
  select * into v_state from public.portal_preparation_rank_refresh where programme=p_programme;
  if v_state.run_id is null or v_state.refreshed_at < now() - interval '24 hours' then
    return v_empty || jsonb_build_object('status','temporarily_unavailable');
  end if;
  select active_cohort_size into v_cohort from public.tmua_preparation_rank_runs
    where id=v_state.run_id and model_version=v_model;
  select * into v_snapshot from public.tmua_preparation_rank_snapshots
    where run_id=v_state.run_id and user_id=p_user_id and model_version=v_model;
  if not found then return v_empty || jsonb_build_object('cohortSize',coalesce(v_cohort,0),
    'calculatedAt',v_state.refreshed_at); end if;
  return jsonb_build_object('modelVersion',v_model,
    'hasGenuinePreparationEvidence',v_snapshot.genuine_preparation_evidence,
    'score',v_snapshot.actual_preparation_score,'rank',v_snapshot.actual_preparation_rank,
    'cohortSize',v_snapshot.actual_active_cohort_size,'calculatedAt',v_state.refreshed_at,
    'components',case when v_snapshot.genuine_preparation_evidence then jsonb_build_object(
      'performance',v_snapshot.performance_component,'breadth',v_snapshot.breadth_component,
      'evidenceDepth',v_snapshot.evidence_depth_component,'recentActivity',v_snapshot.recent_activity_component,
      'consistency',v_snapshot.consistency_component,'recovery',v_snapshot.recovery_component) else null end);
end;
$$;
revoke all on function public.claim_portal_rank_refresh(text) from public,anon,authenticated;
revoke all on function public.finish_portal_rank_refresh(text,uuid,uuid) from public,anon,authenticated;
revoke all on function public.fail_portal_rank_refresh(text,uuid) from public,anon,authenticated;
revoke all on function public.read_portal_preparation_rank(text,uuid,text) from public,anon,authenticated;
grant execute on function public.claim_portal_rank_refresh(text) to service_role;
grant execute on function public.finish_portal_rank_refresh(text,uuid,uuid) to service_role;
grant execute on function public.fail_portal_rank_refresh(text,uuid) to service_role;
grant execute on function public.read_portal_preparation_rank(text,uuid,text) to service_role;
