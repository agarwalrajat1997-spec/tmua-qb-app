create extension if not exists pgcrypto;

create table if not exists public.tmua_qb_attempt_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  email text,
  product text not null default 'tmua-question-bank',
  question_id text not null,
  topic_id text,
  selected_answer text,
  is_correct boolean not null,
  attempted_at timestamptz not null default now(),
  source text not null default 'tmua-question-bank',
  client_event_id text,
  history_quality text not null default 'observed',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create unique index if not exists
  tmua_qb_attempt_events_client_event_id_uidx
on public.tmua_qb_attempt_events(client_event_id)
where client_event_id is not null;

create index if not exists
  tmua_qb_attempt_events_user_attempted_idx
on public.tmua_qb_attempt_events(user_id, attempted_at desc);

create index if not exists
  tmua_qb_attempt_events_email_attempted_idx
on public.tmua_qb_attempt_events(lower(email), attempted_at desc);

create index if not exists
  tmua_qb_attempt_events_question_idx
on public.tmua_qb_attempt_events(user_id, question_id, attempted_at);

alter table public.tmua_qb_attempt_events enable row level security;

drop policy if exists
  "Users read their own TMUA QB attempt events"
on public.tmua_qb_attempt_events;

create policy
  "Users read their own TMUA QB attempt events"
on public.tmua_qb_attempt_events
for select
using (auth.uid() = user_id);

alter table public.practice_test_attempts
  add column if not exists attempt_number integer,
  add column if not exists started_at timestamptz,
  add column if not exists paper_1_score integer,
  add column if not exists paper_2_score integer,
  add column if not exists is_full_timed_attempt boolean,
  add column if not exists prior_question_exposure_count integer,
  add column if not exists prior_question_exposure_percentage numeric(6,3),
  add column if not exists score_conversion_profile text,
  add column if not exists predictor_metadata jsonb not null default '{}'::jsonb;

create index if not exists
  practice_test_attempts_user_test_submitted_idx
on public.practice_test_attempts(user_id, test_id, submitted_at);

comment on table public.tmua_qb_attempt_events is
  'Append-only observed TMUA question-bank answer events. Existing mutable qb_progress rows are not treated as historical first attempts.';

comment on column public.tmua_qb_attempt_events.history_quality is
  'observed for newly captured events; inferred or imported records must not silently be treated as observed first attempts.';