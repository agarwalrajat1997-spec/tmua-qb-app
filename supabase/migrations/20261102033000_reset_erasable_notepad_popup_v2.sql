-- Restart the Amazon erasable-notepad announcement as a fresh two-view
-- campaign while preserving every earlier popup receipt key.

alter table public.student_popup_receipts
  drop constraint if exists student_popup_receipts_campaign_key_check;

alter table public.student_popup_receipts
  add constraint student_popup_receipts_campaign_key_check
  check (
    campaign_key = any (
      array[
        'pre-exam-good-luck-2026-10-10'::text,
        'tmua-final-warmup-2026-10-13'::text,
        'esat-final-warmup-2026-10-14'::text,
        'erasable-notepad-amazon-2026-11-dismissal-1'::text,
        'erasable-notepad-amazon-2026-11-dismissal-2'::text,
        'erasable-notepad-amazon-image-refresh-2026-11-dismissal-1'::text,
        'erasable-notepad-amazon-image-refresh-2026-11-dismissal-2'::text,
        'erasable-notepad-amazon-popup-reset-v2-2026-11-dismissal-1'::text,
        'erasable-notepad-amazon-popup-reset-v2-2026-11-dismissal-2'::text
      ]
    )
  );
