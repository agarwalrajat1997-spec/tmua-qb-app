-- New, append-only assessment history. No previously submitted scores are recalculated.
create table public.amc_practice_attempts (
 id uuid primary key,
 student_email text not null,
 paper text not null,
 version text not null,
 level smallint not null check (level in (8,10,12)),
 scoring_key text not null check (scoring_key ~ '^[A-E]{25}$'),
 started_at timestamptz not null default now(),
 due_at timestamptz not null,
 submitted_at timestamptz,
 responses jsonb not null default '[]'::jsonb,
 correct smallint, incorrect smallint, blanks smallint, points numeric(5,1),
 check(submitted_at is null or (correct+incorrect+blanks=25 and points is not null))
);
alter table public.amc_practice_attempts enable row level security;
revoke all on public.amc_practice_attempts from public, anon, authenticated;
grant select,insert,update on public.amc_practice_attempts to service_role;
create index amc_practice_attempts_by_student on public.amc_practice_attempts(student_email,started_at desc);
