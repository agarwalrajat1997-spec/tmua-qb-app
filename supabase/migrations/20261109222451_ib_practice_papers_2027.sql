-- Extend the existing Maths mock history to both new AI HL Paper 3s.
alter table public.ib_maths_mock_attempts
  drop constraint ib_maths_mock_attempts_mock_id_check,
  add constraint ib_maths_mock_attempts_mock_id_check check (
    mock_id ~ '^aa-hl-set-[ab]-paper-[123]$' or mock_id ~ '^aa-sl-set-[ab]-paper-[12]$'
    or mock_id ~ '^ai-hl-set-[a-d]-paper-[123]$' or mock_id ~ '^ai-sl-set-[ab]-paper-[12]$'
  );

create table public.ib_practice_paper_attempts (
  id uuid primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  paper_id text not null check (paper_id in ('business-a-paper-1','business-sl-a-paper-2','business-hl-a-paper-2','business-hl-a-paper-3','aa-sl-probability','aa-sl-rates','aa-hl-statistics','aa-hl-trigonometry')),
  choice smallint,
  answers jsonb not null check (jsonb_typeof(answers)='object' and octet_length(answers::text)<=600000),
  self_marks jsonb check (jsonb_typeof(self_marks)='object' and octet_length(self_marks::text)<=10000),
  elapsed_seconds integer not null check (elapsed_seconds between 0 and case paper_id
    when 'business-hl-a-paper-2' then 6300 when 'business-a-paper-1' then 5400 when 'business-sl-a-paper-2' then 5400
    when 'business-hl-a-paper-3' then 4500 when 'aa-hl-trigonometry' then 1500 else 2100 end),
  submitted_at timestamptz not null default now(),
  check (case paper_id when 'business-a-paper-1' then choice is not null and choice in (1,2)
    when 'business-sl-a-paper-2' then choice is not null and choice in (2,3)
    when 'business-hl-a-paper-2' then choice is not null and choice in (3,4) else choice is null end)
);
create index ib_practice_paper_history on public.ib_practice_paper_attempts(user_id,paper_id,submitted_at desc);
alter table public.ib_practice_paper_attempts enable row level security;
revoke all on public.ib_practice_paper_attempts from public,anon,authenticated;
grant select on public.ib_practice_paper_attempts to authenticated;
grant insert(id,user_id,paper_id,choice,answers,elapsed_seconds) on public.ib_practice_paper_attempts to authenticated;
grant update(self_marks) on public.ib_practice_paper_attempts to authenticated;
create policy ib_practice_paper_read on public.ib_practice_paper_attempts for select to authenticated using ((select auth.uid())=user_id);
create policy ib_practice_paper_submit on public.ib_practice_paper_attempts for insert to authenticated with check ((select auth.uid())=user_id);
create policy ib_practice_paper_mark on public.ib_practice_paper_attempts for update to authenticated using ((select auth.uid())=user_id and self_marks is null) with check ((select auth.uid())=user_id and self_marks is not null);
