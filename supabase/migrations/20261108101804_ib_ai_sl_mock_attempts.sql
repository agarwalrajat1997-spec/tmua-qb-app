-- Add the four AI SL papers, preserving published AA/AI HL IDs and every saved attempt.
alter table public.ib_maths_mock_attempts
  drop constraint ib_maths_mock_attempts_mock_id_check,
  add constraint ib_maths_mock_attempts_mock_id_check check (
    mock_id ~ '^aa-hl-set-[ab]-paper-[123]$'
    or mock_id ~ '^aa-sl-set-[ab]-paper-[12]$'
    or mock_id ~ '^ai-hl-set-[a-d]-paper-[12]$'
    or mock_id ~ '^ai-hl-set-[ab]-paper-3$'
    or mock_id ~ '^ai-sl-set-[ab]-paper-[12]$'
  ),
  drop constraint ib_maths_mock_attempts_check,
  add constraint ib_maths_mock_attempts_check check (
    elapsed_seconds >= 0 and elapsed_seconds <= case
      when mock_id like 'aa-sl-%' or mock_id like 'ai-sl-%' then 5400
      when mock_id like '%-paper-3' then 4500
      else 7200 end
  );
