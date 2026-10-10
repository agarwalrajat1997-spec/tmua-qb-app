-- A single account-wide receipt gives both portals at-most-once delivery.
-- Receipts are never expired or reset when the campaign ends.
create table public.student_popup_receipts (
  user_id uuid not null references auth.users(id) on delete cascade,
  campaign_key text not null check (campaign_key = 'pre-exam-good-luck-2026-10-10'),
  claimed_at timestamptz not null default now(),
  primary key (user_id, campaign_key)
);

alter table public.student_popup_receipts enable row level security;

revoke all on table public.student_popup_receipts from public, anon, authenticated;
grant select, insert on table public.student_popup_receipts to authenticated;

create policy "Students read their own popup receipts"
  on public.student_popup_receipts for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "Students claim their own popup once"
  on public.student_popup_receipts for insert to authenticated
  with check ((select auth.uid()) = user_id);

comment on table public.student_popup_receipts is
  'Permanent account-scoped popup receipts, shared by TMUA and ESAT. Claim atomically before display; do not delete on dismissal or campaign expiry.';
