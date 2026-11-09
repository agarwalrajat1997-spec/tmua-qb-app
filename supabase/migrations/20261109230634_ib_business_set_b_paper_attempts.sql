alter table public.ib_practice_paper_attempts
  drop constraint ib_practice_paper_attempts_paper_id_check,
  drop constraint ib_practice_paper_attempts_check,
  drop constraint ib_practice_paper_attempts_check1,
  add constraint ib_practice_paper_id_check check (
    paper_id in ('business-a-paper-1','business-sl-a-paper-2','business-hl-a-paper-2','business-hl-a-paper-3',
                 'business-b-paper-1','business-sl-b-paper-2','business-hl-b-paper-2','business-hl-b-paper-3',
                 'aa-sl-probability','aa-sl-rates','aa-hl-statistics','aa-hl-trigonometry')),
  add constraint ib_practice_elapsed_check check (elapsed_seconds between 0 and case
    when paper_id in ('business-hl-a-paper-2','business-hl-b-paper-2') then 6300
    when paper_id in ('business-a-paper-1','business-b-paper-1','business-sl-a-paper-2','business-sl-b-paper-2') then 5400
    when paper_id in ('business-hl-a-paper-3','business-hl-b-paper-3') then 4500
    when paper_id='aa-hl-trigonometry' then 1500 else 2100 end),
  add constraint ib_practice_section_choice_check check (case
    when paper_id in ('business-a-paper-1','business-b-paper-1') then choice is not null and choice in (1,2)
    when paper_id in ('business-sl-a-paper-2','business-sl-b-paper-2') then choice is not null and choice in (2,3)
    when paper_id in ('business-hl-a-paper-2','business-hl-b-paper-2') then choice is not null and choice in (3,4)
    else choice is null end);
