-- Manual access control table (approve students by email)
-- Product can be: 'tmua-question-bank', 'practice-tests', etc.
create table if not exists public.student_access (
  id bigserial primary key,
  email text not null,
  product text not null default 'tmua-question-bank',
  approved boolean not null default false,
  created_at timestamptz not null default now(),
  unique (email, product)
);

alter table public.student_access enable row level security;

-- Allow signed-in users to read ONLY their own row (matched by JWT email)
drop policy if exists "student_access_select_own" on public.student_access;
create policy "student_access_select_own"
on public.student_access
for select
to authenticated
using (lower(email) = lower((auth.jwt() ->> 'email')));

-- No inserts/updates/deletes from clients (admin manages approvals in dashboard)
-- (service role bypasses RLS automatically)

-- Helpful index
create index if not exists student_access_email_idx on public.student_access (lower(email));