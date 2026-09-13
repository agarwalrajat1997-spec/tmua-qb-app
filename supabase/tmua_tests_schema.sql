-- ===========================
-- Thriving Scholars TMUA schema (tests + attempts) + RLS
-- Run FIRST in Supabase SQL Editor
-- ===========================

create extension if not exists "pgcrypto";

create table if not exists public.tests (
  slug text primary key,
  title text not null,
  kind text not null check (kind in ('topic','mock','official_sample','official_past_paper','full_mock')),
  paper text not null check (paper in ('paper1','paper2','paper1+paper2')),
  duration_minutes int not null,
  topics text[] not null,
  cover_image_url text,
  solution_pdf_url text,
  test_url text,
  sort_order int not null default 0,
  is_free boolean not null default false,
  is_public boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.attempts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  test_slug text not null references public.tests(slug) on delete cascade,
  test_title text not null,
  score int not null,
  max_score int not null,
  answers jsonb not null,
  flags jsonb not null,
  time_spent_seconds jsonb not null,
  incorrect_questions int[] not null default '{}'::int[],
  started_at timestamptz not null,
  submitted_at timestamptz not null,
  created_at timestamptz not null default now()
);

create index if not exists attempts_user_submitted_idx
  on public.attempts (user_id, submitted_at desc);

create index if not exists attempts_user_test_idx
  on public.attempts (user_id, test_slug, submitted_at desc);

-- RLS
alter table public.tests enable row level security;
alter table public.attempts enable row level security;

-- tests readable to everyone (you can restrict later)
drop policy if exists "tests_read" on public.tests;
create policy "tests_read" on public.tests
for select using (true);

-- attempts: only self
drop policy if exists "attempts_read_own" on public.attempts;
create policy "attempts_read_own" on public.attempts
for select using (auth.uid() = user_id);

drop policy if exists "attempts_insert_own" on public.attempts;
create policy "attempts_insert_own" on public.attempts
for insert with check (auth.uid() = user_id);