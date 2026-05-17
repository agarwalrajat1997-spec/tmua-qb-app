-- ============================================================
-- Thriving Scholars — Phase 1 Foundation
-- Tables:
--   1) practice_test_attempts
--   2) qb_progress
-- RLS + policies: users can only access their own rows
-- ============================================================

-- Required for gen_random_uuid()
create extension if not exists pgcrypto;

-- ----------------------------
-- 1) practice_test_attempts
-- ----------------------------
create table if not exists public.practice_test_attempts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  email text,
  test_id text not null,
  test_title text,
  paper text,
  total_questions integer not null default 0,
  score integer not null default 0,
  answers jsonb not null default '[]'::jsonb,
  correct_answers jsonb not null default '[]'::jsonb,
  time_spent jsonb not null default '[]'::jsonb,
  flags jsonb not null default '[]'::jsonb,
  incorrect jsonb not null default '[]'::jsonb,
  session_label text,
  student_name text,
  submitted_at timestamptz not null default now()
);

create index if not exists idx_practice_attempts_user_time
  on public.practice_test_attempts (user_id, submitted_at desc);

create index if not exists idx_practice_attempts_user_test
  on public.practice_test_attempts (user_id, test_id);

alter table public.practice_test_attempts enable row level security;

do $migPath
begin
  if not exists (
    select 1 from pg_policies where schemaname = 'public'
      and tablename = 'practice_test_attempts'
      and policyname = 'pta_select_own'
  ) then
    create policy pta_select_own
      on public.practice_test_attempts
      for select
      using (auth.uid() = user_id);
  end if;

  if not exists (
    select 1 from pg_policies where schemaname = 'public'
      and tablename = 'practice_test_attempts'
      and policyname = 'pta_insert_own'
  ) then
    create policy pta_insert_own
      on public.practice_test_attempts
      for insert
      with check (auth.uid() = user_id);
  end if;
end $migPath;

-- (optional) allow deleting own attempts (comment out if you don't want)
do $migPath
begin
  if not exists (
    select 1 from pg_policies where schemaname = 'public'
      and tablename = 'practice_test_attempts'
      and policyname = 'pta_delete_own'
  ) then
    create policy pta_delete_own
      on public.practice_test_attempts
      for delete
      using (auth.uid() = user_id);
  end if;
end $migPath;

-- ----------------------------
-- 2) qb_progress
-- ----------------------------
create table if not exists public.qb_progress (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  product text not null default 'tmua-question-bank',
  question_id text not null,
  status text not null default 'unseen',
  selected_answer text,
  flagged boolean not null default false,
  time_spent integer not null default 0,
  last_seen_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- one row per (user, product, question)
create unique index if not exists uq_qb_progress_user_product_question
  on public.qb_progress (user_id, product, question_id);

create index if not exists idx_qb_progress_user_updated
  on public.qb_progress (user_id, updated_at desc);

alter table public.qb_progress enable row level security;

do $migPath
begin
  if not exists (
    select 1 from pg_policies where schemaname = 'public'
      and tablename = 'qb_progress'
      and policyname = 'qbp_select_own'
  ) then
    create policy qbp_select_own
      on public.qb_progress
      for select
      using (auth.uid() = user_id);
  end if;

  if not exists (
    select 1 from pg_policies where schemaname = 'public'
      and tablename = 'qb_progress'
      and policyname = 'qbp_insert_own'
  ) then
    create policy qbp_insert_own
      on public.qb_progress
      for insert
      with check (auth.uid() = user_id);
  end if;

  if not exists (
    select 1 from pg_policies where schemaname = 'public'
      and tablename = 'qb_progress'
      and policyname = 'qbp_update_own'
  ) then
    create policy qbp_update_own
      on public.qb_progress
      for update
      using (auth.uid() = user_id)
      with check (auth.uid() = user_id);
  end if;

  if not exists (
    select 1 from pg_policies where schemaname = 'public'
      and tablename = 'qb_progress'
      and policyname = 'qbp_delete_own'
  ) then
    create policy qbp_delete_own
      on public.qb_progress
      for delete
      using (auth.uid() = user_id);
  end if;
end $migPath;

-- Keep updated_at fresh
create or replace function public.set_updated_at()
returns trigger as $migPath
begin
  new.updated_at = now();
  return new;
end;
$migPath language plpgsql;

drop trigger if exists trg_qb_progress_updated_at on public.qb_progress;
create trigger trg_qb_progress_updated_at
before update on public.qb_progress
for each row execute function public.set_updated_at();