-- TMUA Question Bank secure schema
-- Public question text/options in tmua_questions
-- Private answers/solutions in tmua_question_keys
-- User progress in user_question_progress (RLS by auth.uid())

create extension if not exists pgcrypto;

create table if not exists public.question_banks (
  id text primary key,
  title text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.tmua_questions (
  id uuid primary key default gen_random_uuid(),
  bank_id text not null references public.question_banks(id) on delete cascade,
  q_order integer not null,
  paper text,
  topic text,
  subtopic text,
  difficulty smallint,
  prompt_html text not null,
  options jsonb not null,
  page_assets jsonb not null default '[]'::jsonb,
  is_published boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (bank_id, q_order)
);

create index if not exists idx_tmua_questions_bank_order
  on public.tmua_questions(bank_id, q_order);

create table if not exists public.tmua_question_keys (
  question_id uuid primary key references public.tmua_questions(id) on delete cascade,
  answer text not null,
  solution_html text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.user_question_progress (
  user_id uuid not null references auth.users(id) on delete cascade,
  question_id uuid not null references public.tmua_questions(id) on delete cascade,
  selected text,
  checked boolean not null default false,
  is_correct boolean,
  flagged boolean not null default false,
  updated_at timestamptz not null default now(),
  primary key (user_id, question_id)
);

create index if not exists idx_user_question_progress_question
  on public.user_question_progress(question_id);

-- Grants
grant usage on schema public to anon, authenticated;
grant select on public.question_banks to authenticated;
grant select on public.tmua_questions to authenticated;
grant select, insert, update, delete on public.user_question_progress to authenticated;

-- Keep answer keys private
revoke all on public.tmua_question_keys from anon, authenticated;

-- RLS
alter table public.question_banks enable row level security;
alter table public.tmua_questions enable row level security;
alter table public.user_question_progress enable row level security;

drop policy if exists question_banks_auth_read on public.question_banks;
create policy question_banks_auth_read
  on public.question_banks
  for select
  to authenticated
  using (true);

drop policy if exists tmua_questions_auth_read on public.tmua_questions;
create policy tmua_questions_auth_read
  on public.tmua_questions
  for select
  to authenticated
  using (is_published = true);

drop policy if exists progress_select_own on public.user_question_progress;
create policy progress_select_own
  on public.user_question_progress
  for select
  to authenticated
  using (auth.uid() = user_id);

drop policy if exists progress_insert_own on public.user_question_progress;
create policy progress_insert_own
  on public.user_question_progress
  for insert
  to authenticated
  with check (auth.uid() = user_id);

drop policy if exists progress_update_own on public.user_question_progress;
create policy progress_update_own
  on public.user_question_progress
  for update
  to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

drop policy if exists progress_delete_own on public.user_question_progress;
create policy progress_delete_own
  on public.user_question_progress
  for delete
  to authenticated
  using (auth.uid() = user_id);

-- Seed a sample bank + sample question
insert into public.question_banks (id, title)
values ('tmua-question-bank', 'TMUA Question Bank')
on conflict (id) do update set title = excluded.title;

insert into public.tmua_questions (
  id, bank_id, q_order, paper, topic, subtopic, difficulty, prompt_html, options, page_assets, is_published
) values (
  '11111111-1111-1111-1111-111111111111',
  'tmua-question-bank',
  1,
  'Paper 1',
  '1_Algebra & Functions',
  'Starter',
  2,
  '<p>If \(x+3=10\), what is \(x\)?</p>',
  jsonb_build_array(
    jsonb_build_object('label','A','html','5'),
    jsonb_build_object('label','B','html','6'),
    jsonb_build_object('label','C','html','7'),
    jsonb_build_object('label','D','html','8')
  ),
  '[]'::jsonb,
  true
)
on conflict (id) do nothing;

insert into public.tmua_question_keys (question_id, answer, solution_html)
values (
  '11111111-1111-1111-1111-111111111111',
  'C',
  '<p>Subtract 3 from both sides:</p><p>\(x=7\)</p>'
)
on conflict (question_id) do nothing;