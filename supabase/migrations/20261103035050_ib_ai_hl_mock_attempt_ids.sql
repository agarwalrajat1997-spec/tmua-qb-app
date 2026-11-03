-- Add the ten AI HL papers without changing any existing AA ID or saved row.
-- The existing elapsed_seconds check already enforces 7,200 seconds for HL
-- Papers 1/2 and 4,500 seconds (75 minutes) for every Paper 3.
-- Keep ownership policies, column privileges and immutable responses/marks intact.
alter table public.ib_maths_mock_attempts
  drop constraint ib_maths_mock_attempts_mock_id_check,
  add constraint ib_maths_mock_attempts_mock_id_check check (
    mock_id ~ '^aa-hl-set-[ab]-paper-[123]$'
    or mock_id ~ '^aa-sl-set-[ab]-paper-[12]$'
    or mock_id ~ '^ai-hl-set-[a-d]-paper-[12]$'
    or mock_id ~ '^ai-hl-set-[ab]-paper-3$'
  );
