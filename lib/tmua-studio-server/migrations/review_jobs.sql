-- Additive, service-only storage. Apply through the normal Supabase migration workflow.
-- No question, audit, entitlement, progress or existing notebook records are changed.
create table public.tmua_studio_review_jobs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  request_id uuid not null,
  payload_hash text not null check (payload_hash ~ '^[a-f0-9]{64}$'),
  qid text not null, content_version text not null,
  status text not null check (status in ('reserved','pending','complete','failed')),
  provider_id text, review_context jsonb, result jsonb, usage jsonb,
  model text not null, error_code text,
  created_at timestamptz not null default now(), completed_at timestamptz,
  unique(user_id,request_id)
);
create index tmua_studio_review_jobs_created_idx on public.tmua_studio_review_jobs(created_at);
create index tmua_studio_review_jobs_user_hash_idx on public.tmua_studio_review_jobs(user_id,payload_hash,created_at desc);
alter table public.tmua_studio_review_jobs enable row level security;
revoke all on public.tmua_studio_review_jobs from public,anon,authenticated;
grant select,insert,update,delete on public.tmua_studio_review_jobs to service_role;

create function public.reserve_tmua_studio_review(
  p_user uuid,p_request uuid,p_hash text,p_qid text,p_version text,p_model text,p_context jsonb
) returns jsonb language plpgsql security invoker set search_path='' as $$
declare existing public.tmua_studio_review_jobs; new_id uuid;
begin
  -- Serializes claims across server instances; no client can call this function.
  perform pg_advisory_xact_lock(731904282);
  if p_user is null or p_request is null or p_hash !~ '^[a-f0-9]{64}$'
    or p_qid is null or length(p_qid)>160 or p_version is null or length(p_version)>200
    or p_model not in ('gpt-6.1-terra','gpt-6-astra') then raise exception 'Invalid review reservation'; end if;
  select * into existing from public.tmua_studio_review_jobs where user_id=p_user and request_id=p_request;
  if found then
    if existing.payload_hash<>p_hash then return jsonb_build_object('status','conflict'); end if;
    return jsonb_build_object('status',existing.status,'id',existing.id,'requestId',existing.request_id,'result',existing.result);
  end if;
  select * into existing from public.tmua_studio_review_jobs where user_id=p_user and payload_hash=p_hash
    and status='complete' and created_at>now()-interval '30 days' order by created_at desc limit 1;
  if found then return jsonb_build_object('status','complete','result',existing.result,'requestId',existing.request_id); end if;
  if exists(select 1 from public.tmua_studio_review_jobs where user_id=p_user and status in ('reserved','pending') and created_at>now()-interval '20 minutes') then
    return jsonb_build_object('status','busy');
  end if;
  if exists(select 1 from public.tmua_studio_review_jobs where user_id=p_user and payload_hash=p_hash and created_at>now()-interval '1 minute') then
    return jsonb_build_object('status','busy');
  end if;
  -- Retains the prepared Studio pilot's existing budget safeguards: 15/user/day, 500/month globally.
  if (select count(*) from public.tmua_studio_review_jobs where user_id=p_user and created_at>=date_trunc('day',now() at time zone 'UTC') at time zone 'UTC')>=15
    or (select count(*) from public.tmua_studio_review_jobs where created_at>=date_trunc('month',now() at time zone 'UTC') at time zone 'UTC')>=500 then
    return jsonb_build_object('status','limit');
  end if;
  insert into public.tmua_studio_review_jobs(user_id,request_id,payload_hash,qid,content_version,status,model,review_context)
    values(p_user,p_request,p_hash,p_qid,p_version,'reserved',p_model,p_context) returning id into new_id;
  return jsonb_build_object('status','claimed','id',new_id,'requestId',p_request);
end;
$$;
revoke all on function public.reserve_tmua_studio_review(uuid,uuid,text,text,text,text,jsonb) from public,anon,authenticated;
grant execute on function public.reserve_tmua_studio_review(uuid,uuid,text,text,text,text,jsonb) to service_role;
