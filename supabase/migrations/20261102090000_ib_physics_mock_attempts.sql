-- Dedicated IB history: never feeds TMUA scoring or predictors.
create table public.ib_physics_mock_attempts (
  id uuid primary key,
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  mock_id text not null check (mock_id ~ '^physics-(sl|hl)-mock-0[1-3]$'),
  paper text not null check (paper in ('1','2')),
  answers jsonb not null check (jsonb_typeof(answers) = 'object'),
  elapsed_seconds integer not null check (elapsed_seconds between 0 and 9000),
  submitted_at timestamptz not null default now(),
  self_marks jsonb check (self_marks is null or jsonb_typeof(self_marks) = 'object'),
  marked_at timestamptz
);
create index ib_physics_mock_attempts_user_history on public.ib_physics_mock_attempts(user_id, submitted_at desc);
alter table public.ib_physics_mock_attempts enable row level security;
revoke all on public.ib_physics_mock_attempts from anon, authenticated;
grant select, insert on public.ib_physics_mock_attempts to authenticated;
-- Submitted answers are immutable; students may only self-assess their own work.
grant update(self_marks, marked_at) on public.ib_physics_mock_attempts to authenticated;
create policy ib_physics_read_own on public.ib_physics_mock_attempts for select to authenticated using ((select auth.uid()) = user_id);
create policy ib_physics_submit_own on public.ib_physics_mock_attempts for insert to authenticated with check ((select auth.uid()) = user_id);
create policy ib_physics_mark_own on public.ib_physics_mock_attempts for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
