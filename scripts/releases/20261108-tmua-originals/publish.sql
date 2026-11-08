do $release$
declare
  changed integer;
begin
  if (select count(*) from private.tmua_original_release_20261108) <> 447 then
    raise exception 'Expected exactly 447 staged questions';
  end if;
  perform q.qid from public.tmua_qb_questions q
    join private.tmua_original_release_20261108 r using (qid)
    order by q.qid for update of q, r;
  if (select count(*) from public.tmua_qb_questions q
      join private.tmua_original_release_20261108 r using(qid)
      where q.is_active and q.display_order=(r.payload->>'app_number')::integer
        and r.before_row is null and md5(to_jsonb(q)::text)=r.payload->>'guard') <> 447 then
    raise exception 'Target records differ from the reviewed snapshot';
  end if;
  update private.tmua_original_release_20261108 r set before_row=to_jsonb(q), published_at=transaction_timestamp()
    from public.tmua_qb_questions q where q.qid=r.qid;
  update public.tmua_qb_questions q set
    topic=s.topic, subtopic=s.subtopic, difficulty=s.difficulty, tags=s.tags,
    prompt_html=s.prompt_html, options=s.options, answer=s.answer, solution_html=s.solution_html,
    answer_verified=true, shortcut_available=false, nice_tip_html=null, checker_flags='[]'::jsonb,
    page_assets='[]'::jsonb, updated_at=r.published_at,
    source_json=jsonb_build_object(
      'qid',q.qid,'kind',q.kind,'paper',q.paper,'topic',s.topic,'subtopic',s.subtopic,'difficulty',s.difficulty,
      'tags',s.tags,'prompt_html',s.prompt_html,'options',s.options,'answer',s.answer,'solution_html',s.solution_html,
      'answer_verified',true,'shortcut_available',false,'nice_tip_html',null,'checker_flags','[]'::jsonb,
      'content_version',s.content_version,'source_sha256',s.source_sha256)
    from private.tmua_original_release_20261108 r
    cross join lateral jsonb_to_record(r.payload) s(topic text, subtopic text, difficulty integer, tags jsonb,
      prompt_html text, options jsonb, answer text, solution_html text, content_version text, source_sha256 text)
    where q.qid=r.qid;
  get diagnostics changed = row_count;
  if changed <> 447 then raise exception 'Updated % rows, expected 447', changed; end if;
  if exists (select 1 from private.tmua_original_release_20261108 r join public.tmua_qb_questions q using(qid)
    where q.prompt_html is distinct from r.payload->>'prompt_html' or q.options is distinct from r.payload->'options'
      or q.answer is distinct from r.payload->>'answer' or q.solution_html is distinct from r.payload->>'solution_html'
      or q.source_json->>'content_version' is distinct from r.payload->>'content_version'
      or md5(r.before_row::text) <> r.payload->>'guard') then raise exception 'Release verification failed'; end if;
end $release$;
