-- Permit exactly the new reminder in addition to the existing good-luck
-- campaign. Keep all existing receipts, the primary key, grants and RLS intact.
-- The single ALTER is atomic: the table is never left without its allowlist.
alter table public.student_popup_receipts
  drop constraint student_popup_receipts_campaign_key_check,
  add constraint student_popup_receipts_campaign_key_check
    check (campaign_key in (
      'pre-exam-good-luck-2026-10-10',
      'tmua-final-warmup-2026-10-13'
    ));
