-- Extend only the campaign allowlist; preserve existing receipts, grants and RLS.
-- One atomic ALTER keeps the table protected throughout the change.
alter table public.student_popup_receipts
  drop constraint student_popup_receipts_campaign_key_check,
  add constraint student_popup_receipts_campaign_key_check
    check (campaign_key in (
      'pre-exam-good-luck-2026-10-10',
      'tmua-final-warmup-2026-10-13',
      'esat-final-warmup-2026-10-14'
    ));
