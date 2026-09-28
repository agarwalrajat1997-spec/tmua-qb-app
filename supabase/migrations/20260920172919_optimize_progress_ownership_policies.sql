-- Reduce per-row auth evaluation and remove only audited equivalent policies.
-- Snapshot verified 2026-09-20. Roles, grants, ownership and email matching are unchanged.
-- Product approval/expiry remains checked by application/RPC logic; this migration
-- does not broaden those checks or edit any student progress/entitlement rows.
-- Rollback: node scripts/verify-progress-rls.mjs --print-rollback
begin;
set local lock_timeout = '3s';
set local statement_timeout = '15s';

do $guard$
declare
  expected jsonb := '[{"cmd":"DELETE","qual":"((auth.uid())::text = (user_id)::text)","roles":["public"],"tablename":"qb_progress","permissive":"PERMISSIVE","policyname":"qb_progress_delete_own","schemaname":"public","with_check":null},{"cmd":"INSERT","qual":null,"roles":["public"],"tablename":"qb_progress","permissive":"PERMISSIVE","policyname":"qb_progress_insert_own","schemaname":"public","with_check":"((auth.uid())::text = (user_id)::text)"},{"cmd":"SELECT","qual":"((auth.uid())::text = (user_id)::text)","roles":["public"],"tablename":"qb_progress","permissive":"PERMISSIVE","policyname":"qb_progress_select_own","schemaname":"public","with_check":null},{"cmd":"UPDATE","qual":"((auth.uid())::text = (user_id)::text)","roles":["public"],"tablename":"qb_progress","permissive":"PERMISSIVE","policyname":"qb_progress_update_own","schemaname":"public","with_check":"((auth.uid())::text = (user_id)::text)"},{"cmd":"DELETE","qual":"(auth.uid() = user_id)","roles":["public"],"tablename":"qb_progress","permissive":"PERMISSIVE","policyname":"qbp_delete_own","schemaname":"public","with_check":null},{"cmd":"INSERT","qual":null,"roles":["public"],"tablename":"qb_progress","permissive":"PERMISSIVE","policyname":"qbp_insert_own","schemaname":"public","with_check":"(auth.uid() = user_id)"},{"cmd":"SELECT","qual":"(auth.uid() = user_id)","roles":["public"],"tablename":"qb_progress","permissive":"PERMISSIVE","policyname":"qbp_select_own","schemaname":"public","with_check":null},{"cmd":"UPDATE","qual":"(auth.uid() = user_id)","roles":["public"],"tablename":"qb_progress","permissive":"PERMISSIVE","policyname":"qbp_update_own","schemaname":"public","with_check":"(auth.uid() = user_id)"},{"cmd":"SELECT","qual":"(lower(email) = lower((auth.jwt() ->> ''email''::text)))","roles":["authenticated"],"tablename":"student_access","permissive":"PERMISSIVE","policyname":"student_access_select_own","schemaname":"public","with_check":null},{"cmd":"SELECT","qual":"(lower(email) = lower((auth.jwt() ->> ''email''::text)))","roles":["authenticated"],"tablename":"student_access","permissive":"PERMISSIVE","policyname":"students can read own access","schemaname":"public","with_check":null},{"cmd":"DELETE","qual":"((auth.uid())::text = (user_id)::text)","roles":["public"],"tablename":"user_progress","permissive":"PERMISSIVE","policyname":"user_progress_delete_own","schemaname":"public","with_check":null},{"cmd":"INSERT","qual":null,"roles":["public"],"tablename":"user_progress","permissive":"PERMISSIVE","policyname":"user_progress_insert_own","schemaname":"public","with_check":"((auth.uid())::text = (user_id)::text)"},{"cmd":"SELECT","qual":"(auth.uid() = user_id)","roles":["public"],"tablename":"user_progress","permissive":"PERMISSIVE","policyname":"user_progress_read_own","schemaname":"public","with_check":null},{"cmd":"SELECT","qual":"((auth.uid())::text = (user_id)::text)","roles":["public"],"tablename":"user_progress","permissive":"PERMISSIVE","policyname":"user_progress_select_own","schemaname":"public","with_check":null},{"cmd":"UPDATE","qual":"((auth.uid())::text = (user_id)::text)","roles":["public"],"tablename":"user_progress","permissive":"PERMISSIVE","policyname":"user_progress_update_own","schemaname":"public","with_check":"((auth.uid())::text = (user_id)::text)"}]'::jsonb;
  policy jsonb;
  actual jsonb;
begin
  if (select count(*) from pg_policies where schemaname='public'
      and tablename in ('qb_progress','user_progress','student_access')) <> jsonb_array_length(expected) then
    raise exception 'RLS policy inventory has changed; review before migrating';
  end if;
  for policy in select value from jsonb_array_elements(expected) loop
    select to_jsonb(p) into actual from pg_policies p
      where schemaname='public' and tablename=policy->>'tablename' and policyname=policy->>'policyname';
    if actual is distinct from policy then
      raise exception 'RLS policy changed: %.%; review before migrating',policy->>'tablename',policy->>'policyname';
    end if;
  end loop;
  if exists (select 1 from pg_class where oid in
      ('public.qb_progress'::regclass,'public.user_progress'::regclass,'public.student_access'::regclass)
      and not relrowsecurity) then
    raise exception 'Expected row level security to remain enabled';
  end if;
  if (select count(*) from information_schema.columns where table_schema='public'
      and table_name in ('qb_progress','user_progress') and column_name='user_id' and udt_name='uuid') <> 2 then
    raise exception 'Ownership UUID columns changed; review equivalence';
  end if;
end;
$guard$;

drop policy "qb_progress_delete_own" on public.qb_progress;
drop policy "qb_progress_insert_own" on public.qb_progress;
drop policy "qb_progress_select_own" on public.qb_progress;
drop policy "qb_progress_update_own" on public.qb_progress;
drop policy "qbp_delete_own" on public.qb_progress;
drop policy "qbp_insert_own" on public.qb_progress;
drop policy "qbp_select_own" on public.qb_progress;
drop policy "qbp_update_own" on public.qb_progress;
drop policy "student_access_select_own" on public.student_access;
drop policy "students can read own access" on public.student_access;
drop policy "user_progress_delete_own" on public.user_progress;
drop policy "user_progress_insert_own" on public.user_progress;
drop policy "user_progress_read_own" on public.user_progress;
drop policy "user_progress_select_own" on public.user_progress;
drop policy "user_progress_update_own" on public.user_progress;

-- Keep PUBLIC on progress exactly as audited: an unauthenticated request has
-- auth.uid() NULL and cannot match a row. Table privileges are not modified.
-- UUID equality equals the former UUID::text comparison without losing index use.
create policy qb_progress_select_own on public.qb_progress
  as permissive for select to public
  using ((select auth.uid()) = user_id);

create policy qb_progress_insert_own on public.qb_progress
  as permissive for insert to public
  with check ((select auth.uid()) = user_id);

create policy qb_progress_update_own on public.qb_progress
  as permissive for update to public
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy qb_progress_delete_own on public.qb_progress
  as permissive for delete to public
  using ((select auth.uid()) = user_id);

create policy user_progress_select_own on public.user_progress
  as permissive for select to public
  using ((select auth.uid()) = user_id);

create policy user_progress_insert_own on public.user_progress
  as permissive for insert to public
  with check ((select auth.uid()) = user_id);

create policy user_progress_update_own on public.user_progress
  as permissive for update to public
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy user_progress_delete_own on public.user_progress
  as permissive for delete to public
  using ((select auth.uid()) = user_id);

create policy student_access_select_own on public.student_access
  as permissive for select to authenticated
  using (lower(email) = (select lower(auth.jwt()->>'email')));

commit;
