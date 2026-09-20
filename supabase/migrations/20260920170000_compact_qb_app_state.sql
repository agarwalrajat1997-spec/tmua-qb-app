-- Keep the original state before the first v2 write. No progress records are deleted.
create table if not exists public._qb_app_state_backups_v2 (
  user_id uuid not null,
  product text not null,
  key text not null,
  row_data jsonb not null,
  backed_up_at timestamptz not null default now(),
  primary key (user_id, product, key)
);
alter table public._qb_app_state_backups_v2 enable row level security;
revoke all on public._qb_app_state_backups_v2 from public, anon, authenticated;
insert into public._qb_app_state_backups_v2(user_id, product, key, row_data)
select p.user_id, p.product, p.key, to_jsonb(p)
from public.user_progress p
where p.product in ('tmua-question-bank', 'esat-question-bank') and p.key = 'app_state'
on conflict do nothing;

create or replace function public.compact_qb_state_v2(p_state jsonb)
returns jsonb language plpgsql immutable set search_path = '' as $$
declare v_answers jsonb;
begin
  if jsonb_typeof(p_state) <> 'object' then raise exception 'Invalid state'; end if;
  if not (p_state ? 'answers') then return p_state; end if;
  if jsonb_typeof(p_state->'answers') <> 'object' then raise exception 'Invalid answers'; end if;
  if exists (select 1 from jsonb_each(p_state->'answers') a
      where jsonb_typeof(a.value) <> 'object' or a.key in ('__proto__','constructor','prototype')) then
    raise exception 'Invalid answer entry';
  end if;
  select coalesce(jsonb_object_agg(a.key, a.value - 'solution_html'), '{}'::jsonb)
    into v_answers from jsonb_each(p_state->'answers') a;
  return jsonb_set(p_state, '{answers}', v_answers);
end;
$$;

create or replace function public.save_qb_app_state_v2(p_product text, p_patch jsonb, p_storage_key text)
returns timestamptz language plpgsql security invoker set search_path = '' as $$
declare
  v_uid uuid := auth.uid();
  v_email text := lower(auth.jwt()->>'email');
  v_old jsonb;
  v_state jsonb;
  v_patch jsonb;
  v_merged jsonb;
  v_updated timestamptz;
begin
  if v_uid is null or v_email is null then raise insufficient_privilege; end if;
  if p_product not in ('tmua-question-bank','esat-question-bank') then raise exception 'Invalid product'; end if;
  if p_patch is null or octet_length(p_patch::text) > 1048576 then raise exception 'Invalid progress patch'; end if;
  if not exists (select 1 from public.student_access a where lower(a.email) = v_email
    and a.product = p_product and a.approved and (a.expires_at is null or a.expires_at > now())) then
    raise insufficient_privilege;
  end if;
  v_patch := public.compact_qb_state_v2(p_patch);
  -- The unique row and row lock make changes to different questions merge atomically.
  insert into public.user_progress(user_id,email,product,key,data)
    values(v_uid,v_email,p_product,'app_state','{}'::jsonb) on conflict do nothing;
  select data into v_old from public.user_progress
    where user_id=v_uid and product=p_product and key='app_state' for update;
  if jsonb_typeof(v_old->'parsed') = 'object' then v_state := v_old->'parsed';
  elsif jsonb_typeof(v_old->'raw') = 'string' then v_state := (v_old->>'raw')::jsonb;
  else v_state := '{}'::jsonb;
  end if;
  v_state := public.compact_qb_state_v2(v_state);
  v_merged := (v_state || (v_patch - 'answers')) || jsonb_build_object('answers',
    coalesce(v_state->'answers','{}'::jsonb) || coalesce(v_patch->'answers','{}'::jsonb));
  if v_old->>'version' = '2' and v_merged = v_state then
    select updated_at into v_updated from public.user_progress
      where user_id=v_uid and product=p_product and key='app_state';
    return v_updated;
  end if;
  update public.user_progress set data=jsonb_build_object(
    'version',2,'storage_key',p_storage_key,'parsed',v_merged,'saved_at',clock_timestamp()),
    email=v_email,updated_at=clock_timestamp()
    where user_id=v_uid and product=p_product and key='app_state'
    returning updated_at into v_updated;
  return v_updated;
end;
$$;
revoke all on function public.compact_qb_state_v2(jsonb) from public, anon;
revoke all on function public.save_qb_app_state_v2(text,jsonb,text) from public, anon;
grant execute on function public.compact_qb_state_v2(jsonb) to authenticated;
grant execute on function public.save_qb_app_state_v2(text,jsonb,text) to authenticated;
