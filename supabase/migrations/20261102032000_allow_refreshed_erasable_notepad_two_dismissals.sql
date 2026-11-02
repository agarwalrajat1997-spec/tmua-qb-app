-- Allow the refreshed Amazon notepad campaign to begin a new two-dismissal cycle.
-- Existing campaign receipts remain valid and unchanged.

alter table public.student_popup_receipts
  drop constraint if exists student_popup_receipts_campaign_key_check;

alter table public.student_popup_receipts
  add constraint student_popup_receipts_campaign_key_check
  check (
    campaign_key = any (
      array[
        'pre-exam-good-luck-2026-10-10',
        'tmua-final-warmup-2026-10-13',
        'esat-final-warmup-2026-10-14',
        'erasable-notepad-amazon-2026-11-dismissal-1',
        'erasable-notepad-amazon-2026-11-dismissal-2',
        'erasable-notepad-amazon-image-refresh-2026-11-dismissal-1',
        'erasable-notepad-amazon-image-refresh-2026-11-dismissal-2'
      ]::text[]
    )
  );
