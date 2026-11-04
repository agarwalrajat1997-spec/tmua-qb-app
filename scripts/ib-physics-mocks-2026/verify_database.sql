begin;
do $qa$
declare
  owner_id uuid; other_id uuid;
  attempt_id uuid := gen_random_uuid(); new_id uuid;
  set_id text; p text; max_seconds integer; changed integer;
  old_rows bigint; maths_rows bigint;
begin
  select id into owner_id from auth.users order by id limit 1;
  select id into other_id from auth.users where id <> owner_id order by id limit 1;
  if owner_id is null or other_id is null then raise exception 'Two existing users required'; end if;
  select count(*) into old_rows from public.ib_physics_mock_attempts;
  select count(*) into maths_rows from public.ib_maths_mock_attempts;
  perform set_config('request.jwt.claim.sub',owner_id::text,true);
  execute 'set local role authenticated';
  foreach set_id in array array['physics-hl-challenge-a','physics-hl-challenge-b','physics-hl-challenge-c','physics-sl-challenge-a','physics-sl-challenge-b'] loop
    foreach p in array array['1','2'] loop
      new_id := case when set_id='physics-hl-challenge-a' and p='1' then attempt_id else gen_random_uuid() end;
      max_seconds := case when set_id like 'physics-sl-%' then 5400 when p='1' then 7200 else 9000 end;
      insert into public.ib_physics_challenge_attempts(id,user_id,mock_id,paper,student_name,answers,elapsed_seconds)
        values(new_id,owner_id,set_id,p,'QA_PHYSICS_CHALLENGE_ROLLBACK_20261104','{"response":"retained working"}',max_seconds);
      if not exists(select 1 from public.ib_physics_challenge_attempts where id=new_id and user_id=owner_id and mock_id=set_id and paper=p and answers->>'response'='retained working') then raise exception 'Owner submit/read failed'; end if;
      begin
        insert into public.ib_physics_challenge_attempts(id,user_id,mock_id,paper,student_name,answers,elapsed_seconds)
          values(gen_random_uuid(),owner_id,set_id,p,'QA_PHYSICS_CHALLENGE_ROLLBACK_20261104','{}',max_seconds+1);
        raise exception 'Elapsed bound accepted too much time';
      exception when check_violation then null; end;
    end loop;
  end loop;
  if (select count(*) from public.ib_physics_challenge_attempts where student_name='QA_PHYSICS_CHALLENGE_ROLLBACK_20261104')<>10 then raise exception 'Not all ten sittings accepted'; end if;
  begin
    insert into public.ib_physics_challenge_attempts(id,user_id,mock_id,paper,student_name,answers,elapsed_seconds) values(attempt_id,owner_id,'physics-hl-challenge-a','1','QA_PHYSICS_CHALLENGE_ROLLBACK_20261104','{}',0);
    raise exception 'Duplicate attempt ID accepted';
  exception when unique_violation then null; end;
  foreach set_id in array array['physics-sl-challenge-c','physics-hl-mock-01','aa-hl-set-a-paper-1'] loop
    begin
      insert into public.ib_physics_challenge_attempts(id,user_id,mock_id,paper,student_name,answers,elapsed_seconds) values(gen_random_uuid(),owner_id,set_id,'1','QA_PHYSICS_CHALLENGE_ROLLBACK_20261104','{}',0);
      raise exception 'Disallowed set accepted';
    exception when check_violation then null; end;
  end loop;
  begin
    insert into public.ib_physics_challenge_attempts(id,user_id,mock_id,paper,student_name,answers,elapsed_seconds) values(gen_random_uuid(),owner_id,'physics-hl-challenge-a','3','QA_PHYSICS_CHALLENGE_ROLLBACK_20261104','{}',0);
    raise exception 'Paper 3 accepted';
  exception when check_violation then null; end;
  begin
    update public.ib_physics_challenge_attempts set answers='{"response":"overwrite"}' where id=attempt_id;
    raise exception 'Owner overwrote responses';
  exception when insufficient_privilege or check_violation then null; end;
  begin
    update public.ib_physics_challenge_attempts set student_name='Changed' where id=attempt_id;
    raise exception 'Owner overwrote name';
  exception when insufficient_privilege or check_violation then null; end;
  begin
    update public.ib_physics_challenge_attempts set marked_at=now() where id=attempt_id;
    raise exception 'Unpaired marking timestamp accepted';
  exception when check_violation then null; end;
  begin
    update public.ib_physics_challenge_attempts set self_marks='{"part":11}',marked_at=now() where id=attempt_id;
    raise exception 'Out-of-range mark accepted';
  exception when check_violation then null; end;
  begin
    update public.ib_physics_challenge_attempts set self_marks='{"part":0.5}',marked_at=now() where id=attempt_id;
    raise exception 'Fractional mark accepted';
  exception when check_violation then null; end;
  begin
    update public.ib_physics_challenge_attempts set self_marks='{"part":"1"}',marked_at=now() where id=attempt_id;
    raise exception 'String mark accepted';
  exception when check_violation then null; end;
  update public.ib_physics_challenge_attempts set self_marks='{"part":4}',marked_at=now() where id=attempt_id;
  get diagnostics changed=row_count;
  if changed<>1 or not exists(select 1 from public.ib_physics_challenge_attempts where id=attempt_id and self_marks='{"part":4}'::jsonb and marked_at is not null) then raise exception 'Owner save/read self-assessment failed'; end if;
  begin
    update public.ib_physics_challenge_attempts set self_marks='{"part":0}',marked_at=now() where id=attempt_id;
    raise exception 'Saved marks overwritten';
  exception when check_violation then null; end;
  begin
    delete from public.ib_physics_challenge_attempts where id=attempt_id;
    raise exception 'Owner could delete submitted attempt';
  exception when insufficient_privilege then null; end;
  perform set_config('request.jwt.claim.sub',other_id::text,true);
  if exists(select 1 from public.ib_physics_challenge_attempts where student_name='QA_PHYSICS_CHALLENGE_ROLLBACK_20261104') then raise exception 'Other user read owner attempts'; end if;
  update public.ib_physics_challenge_attempts set self_marks='{}',marked_at=now() where id=attempt_id;
  get diagnostics changed=row_count;if changed<>0 then raise exception 'Other user marked owner row'; end if;
  begin
    insert into public.ib_physics_challenge_attempts(id,user_id,mock_id,paper,student_name,answers,elapsed_seconds) values(gen_random_uuid(),owner_id,'physics-hl-challenge-a','1','QA_PHYSICS_CHALLENGE_ROLLBACK_20261104','{}',0);
    raise exception 'Other user inserted owner attempt';
  exception when insufficient_privilege then null; end;
  execute 'set local role anon';
  begin
    perform 1 from public.ib_physics_challenge_attempts limit 1;
    raise exception 'Anonymous read allowed';
  exception when insufficient_privilege then null; end;
  execute 'reset role';
  -- Administrative bypass of RLS still cannot bypass the immutable trigger.
  begin
    update public.ib_physics_challenge_attempts set answers='{"response":"overwrite"}' where id=attempt_id;
    raise exception 'Immutable answer trigger bypassed';
  exception when check_violation then null; end;
  if (select count(*) from public.ib_physics_mock_attempts)<>old_rows or (select count(*) from public.ib_maths_mock_attempts)<>maths_rows then raise exception 'Unrelated history changed'; end if;
end;
$qa$;
rollback;
select count(*) as remaining_qa_rows from public.ib_physics_challenge_attempts where student_name='QA_PHYSICS_CHALLENGE_ROLLBACK_20261104';
