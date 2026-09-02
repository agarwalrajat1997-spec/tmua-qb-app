begin;

create table if not exists public.sat_question_reports (
  id uuid primary key default gen_random_uuid(),
  user_id uuid null references auth.users(id) on delete set null,
  user_email text not null,
  qid text not null references public.sat_qb_questions(qid) on delete cascade,
  report_text text not null,
  context jsonb not null default '{}'::jsonb,
  status text not null default 'open',
  created_at timestamptz not null default now(),
  resolved_at timestamptz null,
  constraint sat_question_reports_text_length
    check (char_length(btrim(report_text)) between 5 and 4000),
  constraint sat_question_reports_status_valid
    check (status in ('open', 'reviewing', 'resolved', 'dismissed')),
  constraint sat_question_reports_context_object
    check (jsonb_typeof(context) = 'object')
);

create index if not exists sat_question_reports_open_created_idx
  on public.sat_question_reports (status, created_at desc);

create index if not exists sat_question_reports_qid_created_idx
  on public.sat_question_reports (qid, created_at desc);

alter table public.sat_question_reports enable row level security;
revoke all on table public.sat_question_reports from anon, authenticated;
grant all on table public.sat_question_reports to service_role;

comment on table public.sat_question_reports is
  'Authenticated SAT Question Bank issue reports. Writes are server-only via the service role.';

create or replace function public.publish_sat_qb_release(
  p_expected_count integer,
  p_expected_qid_md5 text
)
returns table (
  published_count integer,
  active_count integer,
  answer_verified_count integer,
  qid_md5 text
)
language plpgsql
security definer
set search_path = pg_catalog, public
as $$
declare
  v_count integer;
  v_qid_md5 text;
begin
  if coalesce(auth.role(), '') <> 'service_role' then
    raise exception 'service_role is required';
  end if;

  select count(*)::integer,
         md5(string_agg(qid, E'\n' order by qid))
    into v_count, v_qid_md5
    from public.sat_qb_questions;

  if v_count <> p_expected_count then
    raise exception 'SAT publish count mismatch: expected %, found %',
      p_expected_count, v_count;
  end if;

  if v_qid_md5 is distinct from lower(p_expected_qid_md5) then
    raise exception 'SAT publish qid hash mismatch: expected %, found %',
      lower(p_expected_qid_md5), v_qid_md5;
  end if;

  if exists (
    select 1
      from public.sat_qb_questions
     where answer is null
        or btrim(answer) = ''
        or prompt_html is null
        or btrim(prompt_html) = ''
        or jsonb_typeof(options) <> 'array'
        or jsonb_array_length(options) <> 4
  ) then
    raise exception 'SAT publish validation failed: incomplete question data';
  end if;

  if exists (
    select 1
      from public.sat_qb_questions
     where page_assets::text like '%data:image/%'
        or options::text like '%data:image/%'
  ) then
    raise exception 'SAT publish validation failed: embedded image data remains';
  end if;

  update public.sat_qb_questions
     set answer_verified = true,
         is_active = true,
         updated_at = now();

  return query
    select count(*)::integer,
           count(*) filter (where is_active)::integer,
           count(*) filter (where answer_verified)::integer,
           md5(string_agg(qid, E'\n' order by qid))
      from public.sat_qb_questions;
end;
$$;

revoke all on function public.publish_sat_qb_release(integer, text)
  from public, anon, authenticated;
grant execute on function public.publish_sat_qb_release(integer, text)
  to service_role;

commit;
