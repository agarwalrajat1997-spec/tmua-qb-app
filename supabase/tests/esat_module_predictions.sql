-- Run as an administrator. This test uses one existing auth identity with no plan and rolls back every fixture.
begin;

DO $test$
declare
 u uuid; p public.esat_exam_plans%rowtype; frozen jsonb;
 mods text[] := array['Mathematics 1','Mathematics 2','Physics'];
 sample_scores jsonb := '[{"module":"Mathematics 1","score":6.5,"confidence":"medium","guaranteeEligible":true},{"module":"Mathematics 2","score":6.0,"confidence":"high","guaranteeEligible":true},{"module":"Physics","score":5.5,"confidence":"low","guaranteeEligible":false}]';
begin
 select a.id into u from auth.users a where not exists (select 1 from public.esat_exam_plans existing where existing.user_id=a.id) order by a.created_at limit 1;
 if u is null then raise exception 'Test needs an auth identity without an ESAT plan'; end if; perform set_config('request.jwt.claim.sub',u::text,true);
 perform public.esat_save_exam_plan(u,current_date+10,mods);
 select * into p from public.esat_exam_plans where user_id=u;
 perform public.esat_save_module_predictions(u,p.revision,sample_scores,'test-model',clock_timestamp()-interval '1 second');
 if (select predictions from public.esat_exam_plans where user_id=u) is distinct from sample_scores then raise exception 'Snapshot was not saved'; end if;
 begin
   perform public.esat_save_exam_plan(u,current_date+10,array['Mathematics 1','Physics','Physics']);
   raise exception 'Duplicate modules accepted';
 exception when raise_exception then if sqlerrm='Duplicate modules accepted' then raise; end if; end;
 update public.esat_exam_plans set exam_date=current_date+1, lock_at=(current_date-1)::timestamp at time zone 'Europe/London',
 prediction_saved_at=((current_date-1)::timestamp at time zone 'Europe/London')-interval '1 minute',
 evidence_at=((current_date-1)::timestamp at time zone 'Europe/London')-interval '2 minutes' where user_id=u;
 if public.esat_lock_due_predictions(u) <> 1 then raise exception 'Due snapshot did not lock'; end if;
 if public.esat_lock_due_predictions(u) <> 0 then raise exception 'Lock is not idempotent'; end if;
 select predictions into frozen from public.esat_prediction_locks where user_id=u;
 if frozen is distinct from sample_scores then raise exception 'Locked values changed'; end if;
 perform public.esat_save_module_predictions(u,p.revision,'[]'::jsonb,'later-model',clock_timestamp());
 if (select predictions from public.esat_prediction_locks where user_id=u) is distinct from frozen then raise exception 'Late request changed lock'; end if;
 begin
   perform public.esat_save_exam_plan(u,current_date+20,mods);
   raise exception 'Locked plan rescheduled';
 exception when raise_exception then if sqlerrm='Locked plan rescheduled' then raise; end if; end;
 begin
   update public.esat_prediction_locks set predictions='[]' where user_id=u;
   raise exception 'Locked snapshot modified';
 exception when raise_exception then if sqlerrm='Locked snapshot modified' then raise; end if; end;
 if has_table_privilege('authenticated','public.esat_exam_plans','insert') or
    has_table_privilege('authenticated','public.esat_prediction_locks','update') or
    has_function_privilege('authenticated','public.esat_save_module_predictions(uuid,uuid,jsonb,text,timestamptz)','execute') or
    has_function_privilege('anon','public.esat_save_exam_plan(uuid,date,text[])','execute') then raise exception 'Client write permissions exposed'; end if;
end;
$test$;
set local role authenticated;
DO $rls$ begin
 if (select count(*) from public.esat_exam_plans) <> 1 or (select count(*) from public.esat_prediction_locks) <> 1 then raise exception 'Owner cannot read own records'; end if;
 if exists(select 1 from public.esat_exam_plans where user_id<>auth.uid()) then raise exception 'Other student records visible'; end if;
end; $rls$;
reset role;
set local role anon;
DO $anon$ begin
 begin perform count(*) from public.esat_prediction_locks; raise exception 'Anonymous read allowed'; exception when insufficient_privilege then null; end;
end; $anon$;
reset role;
rollback;
select 'PASS: snapshot locking, immutability, deadline and RLS regression (rolled back)' as verification;
