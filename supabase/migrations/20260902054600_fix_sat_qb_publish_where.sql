begin;

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
         updated_at = now()
   where is_active is distinct from true
      or answer_verified is distinct from true;

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
