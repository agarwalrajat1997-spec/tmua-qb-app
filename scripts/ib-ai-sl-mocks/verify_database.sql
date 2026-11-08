begin;
do $verify$
declare owner_id uuid; rid uuid; test_id text; accepted int:=0;
begin
 select id into owner_id from auth.users limit 1;
 if owner_id is null then raise exception 'No QA principal available'; end if;
 perform set_config('request.jwt.claim.sub',owner_id::text,true);
 execute 'set local role authenticated';
 foreach test_id in array array['ai-sl-set-a-paper-1','ai-sl-set-a-paper-2','ai-sl-set-b-paper-1','ai-sl-set-b-paper-2'] loop
  rid:=gen_random_uuid();
  insert into public.ib_maths_mock_attempts(id,user_id,mock_id,student_name,answers,elapsed_seconds) values(rid,owner_id,test_id,'QA_AI_SL_ROLLBACK_20261108','{"1:a":"QA calculation"}',5400);
  if not exists(select 1 from public.ib_maths_mock_attempts where id=rid and mock_id=test_id and answers->>'1:a'='QA calculation') then raise exception 'Cannot read submitted response'; end if;
  update public.ib_maths_mock_attempts set self_marks='{"1:a":1}',marked_at=now() where id=rid and user_id=owner_id;
  if not exists(select 1 from public.ib_maths_mock_attempts where id=rid and marked_at is not null and self_marks->>'1:a'='1') then raise exception 'Marking failed'; end if;
  accepted:=accepted+1;
 end loop;
 begin
  insert into public.ib_maths_mock_attempts(id,user_id,mock_id,student_name,answers,elapsed_seconds) values(gen_random_uuid(),owner_id,'ai-sl-set-a-paper-3','QA_AI_SL_ROLLBACK_20261108','{}',4500);
  raise exception 'AI SL Paper 3 accepted';
 exception when check_violation then null; end;
 begin
  insert into public.ib_maths_mock_attempts(id,user_id,mock_id,student_name,answers,elapsed_seconds) values(gen_random_uuid(),owner_id,'ai-sl-set-b-paper-2','QA_AI_SL_ROLLBACK_20261108','{}',5401);
  raise exception 'Overtime accepted';
 exception when check_violation then null; end;
 if accepted<>4 then raise exception 'Missing paper'; end if;
end; $verify$;
rollback;
