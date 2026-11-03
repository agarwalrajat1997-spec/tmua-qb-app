begin;
do $qa$
declare
  owner_id uuid;
  other_id uuid;
  attempt_id uuid := gen_random_uuid();
  aa_id uuid := gen_random_uuid();
  new_id uuid;
  mock text;
  changed integer;
begin
  select id into owner_id from auth.users order by id limit 1;
  select id into other_id from auth.users where id <> owner_id order by id limit 1;
  if owner_id is null or other_id is null then raise exception 'Two existing users are required for isolated RLS verification'; end if;
  perform set_config('request.jwt.claim.sub', owner_id::text, true);
  execute 'set local role authenticated';
  insert into public.ib_maths_mock_attempts(id,user_id,mock_id,student_name,answers,elapsed_seconds)
    values(attempt_id,owner_id,'ai-hl-set-a-paper-1','QA_AI_HL_ROLLBACK_20261103','{"1:a":"retained working"}',7200);
  if not exists(select 1 from public.ib_maths_mock_attempts where id=attempt_id and user_id=owner_id and answers->>'1:a'='retained working') then raise exception 'Owner AI submit/read failed'; end if;
  foreach mock in array array['ai-hl-set-a-paper-2','ai-hl-set-a-paper-3','ai-hl-set-b-paper-1','ai-hl-set-b-paper-2','ai-hl-set-b-paper-3','ai-hl-set-c-paper-1','ai-hl-set-c-paper-2','ai-hl-set-d-paper-1','ai-hl-set-d-paper-2'] loop
    new_id := gen_random_uuid();
    insert into public.ib_maths_mock_attempts(id,user_id,mock_id,student_name,answers,elapsed_seconds)
      values(new_id,owner_id,mock,'QA_AI_HL_ROLLBACK_20261103','{}',case when mock like '%-paper-3' then 4500 else 7200 end);
  end loop;
  if (select count(*) from public.ib_maths_mock_attempts where student_name='QA_AI_HL_ROLLBACK_20261103') <> 10 then raise exception 'Not all ten AI IDs were accepted'; end if;
  insert into public.ib_maths_mock_attempts(id,user_id,mock_id,student_name,answers,elapsed_seconds)
    values(aa_id,owner_id,'aa-sl-set-a-paper-1','QA_AI_HL_ROLLBACK_20261103','{}',5400);
  if exists(select 1 from public.ib_maths_mock_attempts where id=attempt_id and mock_id='aa-sl-set-a-paper-1') then raise exception 'AA mock filter exposed an AI attempt'; end if;
  if exists(select 1 from public.ib_maths_mock_attempts where id=aa_id and mock_id='ai-hl-set-a-paper-1') then raise exception 'AI mock filter exposed an AA attempt'; end if;
  begin
    insert into public.ib_maths_mock_attempts(id,user_id,mock_id,student_name,answers,elapsed_seconds) values(gen_random_uuid(),owner_id,'ai-hl-set-c-paper-3','QA_AI_HL_ROLLBACK_20261103','{}',4500);
    raise exception 'Disallowed AI C3 was accepted';
  exception when check_violation then null; end;
  begin
    insert into public.ib_maths_mock_attempts(id,user_id,mock_id,student_name,answers,elapsed_seconds) values(gen_random_uuid(),owner_id,'ai-hl-set-a-paper-3','QA_AI_HL_ROLLBACK_20261103','{}',4501);
    raise exception 'Paper 3 exceeded 75 minutes';
  exception when check_violation then null; end;
  begin
    update public.ib_maths_mock_attempts set answers='{"1:a":"overwrite"}' where id=attempt_id;
    raise exception 'Submitted answers were overwritten';
  exception when insufficient_privilege or check_violation then null; end;
  update public.ib_maths_mock_attempts set self_marks='{"1:a":4}',marked_at=now() where id=attempt_id;
  get diagnostics changed = row_count;
  if changed <> 1 or not exists(select 1 from public.ib_maths_mock_attempts where id=attempt_id and self_marks='{"1:a":4}'::jsonb and marked_at is not null) then raise exception 'Owner self-mark/read failed'; end if;
  begin
    update public.ib_maths_mock_attempts set self_marks='{"1:a":0}',marked_at=now() where id=attempt_id;
    raise exception 'Completed self-assessment was overwritten';
  exception when check_violation then null; end;
  perform set_config('request.jwt.claim.sub', other_id::text, true);
  if exists(select 1 from public.ib_maths_mock_attempts where student_name='QA_AI_HL_ROLLBACK_20261103') then raise exception 'Other user read owner rows'; end if;
  update public.ib_maths_mock_attempts set self_marks='{}',marked_at=now() where id=attempt_id;
  get diagnostics changed = row_count;
  if changed <> 0 then raise exception 'Other user updated owner marks'; end if;
  begin
    insert into public.ib_maths_mock_attempts(id,user_id,mock_id,student_name,answers,elapsed_seconds) values(gen_random_uuid(),owner_id,'ai-hl-set-a-paper-1','QA_AI_HL_ROLLBACK_20261103','{}',0);
    raise exception 'Other user inserted an owner row';
  exception when insufficient_privilege then null; end;
  execute 'set local role anon';
  begin
    perform 1 from public.ib_maths_mock_attempts limit 1;
    raise exception 'Anonymous table access was granted';
  exception when insufficient_privilege then null; end;
  execute 'reset role';
end;
$qa$;
rollback;
select count(*) as remaining_qa_rows from public.ib_maths_mock_attempts where student_name='QA_AI_HL_ROLLBACK_20261103';
