create table if not exists
  public.tmua_score_conversion_profiles (
    profile text primary key,

    conversion_kind text not null
      check (
        conversion_kind in (
          'official',
          'specimen',
          'mock'
        )
      ),

    conversion_version text not null,

    score_values numeric[] not null
      check (
        cardinality(score_values) = 41
      ),

    metadata jsonb not null default '{}'::jsonb,

    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
  );

alter table
  public.tmua_score_conversion_profiles
enable row level security;

drop policy if exists
  "Authenticated users read TMUA score profiles"
on public.tmua_score_conversion_profiles;

create policy
  "Authenticated users read TMUA score profiles"
on public.tmua_score_conversion_profiles
for select
to authenticated
using (true);

grant select
on public.tmua_score_conversion_profiles
to authenticated;


insert into public.tmua_score_conversion_profiles (
  profile,
  conversion_kind,
  conversion_version,
  score_values,
  metadata
)
values
  ('official-2016', 'official', '20260806-1', array[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.6,2.1,2.6,3.0,3.4,3.8,4.2,4.5,4.8,5.2,5.5,5.8,6.1,6.4,6.7,7.1,7.4,7.7,8.0,8.3,8.7,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0]::numeric[], '{}'::jsonb),
  ('official-2017', 'official', '20260806-1', array[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.5,1.9,2.2,2.6,3.0,3.3,3.6,3.9,4.2,4.5,4.8,5.1,5.4,5.6,5.9,6.2,6.5,6.8,7.1,7.4,7.7,8.0,8.4,8.8,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0]::numeric[], '{}'::jsonb),
  ('official-2018', 'official', '20260806-1', array[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.5,1.9,2.3,2.6,3.0,3.3,3.6,3.9,4.2,4.5,4.8,5.1,5.4,5.6,5.9,6.2,6.5,6.8,7.1,7.4,7.7,8.0,8.4,8.8,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0]::numeric[], '{}'::jsonb),
  ('official-2019', 'official', '20260806-1', array[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.1,1.5,1.9,2.3,2.6,3.0,3.3,3.6,3.9,4.2,4.5,4.8,5.1,5.4,5.7,5.9,6.2,6.5,6.6,6.7,6.8,7.0,7.1,7.2,7.4,7.5,7.7,7.9,8.1,8.3,8.6,9.0,9.0,9.0]::numeric[], '{}'::jsonb),
  ('official-2020', 'official', '20260806-1', array[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.4,1.8,2.2,2.6,2.9,3.3,3.6,3.9,4.2,4.5,4.8,5.1,5.3,5.6,5.9,6.2,6.5,6.6,6.7,6.8,7.0,7.1,7.2,7.4,7.5,7.7,7.8,8.1,8.3,8.6,9.0,9.0,9.0]::numeric[], '{}'::jsonb),
  ('official-2021', 'official', '20260806-1', array[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.1,1.5,1.9,2.3,2.6,3.0,3.3,3.6,3.9,4.2,4.5,4.8,5.1,5.4,5.6,5.9,6.2,6.5,6.6,6.7,6.8,7.0,7.1,7.2,7.4,7.5,7.7,7.9,8.1,8.3,8.6,9.0,9.0,9.0]::numeric[], '{}'::jsonb),
  ('official-2022', 'official', '20260806-1', array[1.0,1.0,1.0,1.0,1.0,1.0,1.2,1.6,2.1,2.5,2.9,3.2,3.6,3.9,4.2,4.5,4.8,5.1,5.4,5.7,5.9,6.2,6.5,6.6,6.7,6.8,6.9,7.0,7.1,7.2,7.4,7.5,7.6,7.8,8.0,8.1,8.4,8.6,9.0,9.0,9.0]::numeric[], '{}'::jsonb),
  ('official-2023', 'official', '20260806-1', array[1.0,1.0,1.0,1.0,1.0,1.0,1.5,1.9,2.4,2.8,3.2,3.5,3.9,4.2,4.5,4.8,5.1,5.4,5.7,6.0,6.2,6.5,6.6,6.7,6.8,6.9,7.0,7.1,7.2,7.3,7.4,7.6,7.7,7.8,8.0,8.2,8.4,8.6,9.0,9.0,9.0]::numeric[], '{}'::jsonb),
  ('specimen-estimate', 'specimen', '20260806-1', array[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.5,1.9,2.3,2.6,3.0,3.3,3.6,3.9,4.2,4.5,4.8,5.1,5.4,5.6,5.9,6.2,6.5,6.8,7.1,7.4,7.7,8.0,8.4,8.8,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0]::numeric[], '{}'::jsonb),
  ('mock1', 'mock', '20260806-1', array[1.0,1.0,1.0,1.0,1.0,1.0,1.3,1.5,1.9,2.2,2.6,3.0,3.6,3.9,4.2,4.5,4.8,5.0,5.3,5.5,5.8,6.0,6.2,6.3,6.5,6.8,7.0,7.2,7.3,7.5,7.8,8.0,8.2,8.3,8.5,8.8,9.0,9.0,9.0,9.0,9.0]::numeric[], '{}'::jsonb),
  ('mock2', 'mock', '20260806-1', array[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.3,1.5,1.9,2.2,2.5,2.8,3.2,3.5,3.8,4.1,4.5,4.8,5.0,5.2,5.3,5.5,5.8,6.0,6.3,6.5,6.7,6.8,7.0,7.3,7.5,7.8,8.0,8.2,8.3,8.5,8.8,9.0,9.0]::numeric[], '{}'::jsonb),
  ('informed2024-2025', 'mock', '20260806-1', array[1.0,1.0,1.0,1.0,1.0,1.3,1.5,1.9,2.3,3.0,3.7,4.1,4.5,5.0,5.3,5.5,5.7,5.8,6.0,6.3,6.5,6.7,6.8,7.0,7.2,7.3,7.5,7.7,7.8,8.0,8.2,8.3,8.5,8.8,9.0,9.0,9.0,9.0,9.0,9.0,9.0]::numeric[], '{}'::jsonb)
on conflict (profile) do update
set
  conversion_kind =
    excluded.conversion_kind,

  conversion_version =
    excluded.conversion_version,

  score_values =
    excluded.score_values,

  metadata =
    excluded.metadata,

  updated_at = now();


create or replace function
  public.tmua_convert_overall_score(
    p_profile text,
    p_raw integer
  )
returns numeric
language sql
stable
security definer
set search_path to ''
as $function$
  select
    conversion.score_values[
      least(
        40,
        greatest(
          0,
          coalesce(p_raw, 0)
        )
      ) + 1
    ]
  from public.tmua_score_conversion_profiles
    as conversion
  where conversion.profile = p_profile;
$function$;

revoke all
on function
  public.tmua_convert_overall_score(text, integer)
from public, anon, authenticated;


alter table
  public.tmua_test_attempt_evaluations

  add column if not exists
    overall_raw_score integer,

  add column if not exists
    authoritative_tmua_score9 numeric(3,1),

  add column if not exists
    score_conversion_profile text,

  add column if not exists
    score_conversion_version text,

  add column if not exists
    score_status text;


create or replace function
  public.finalize_tmua_test_attempt_score(
    p_attempt_id uuid
  )
returns void
language plpgsql
security definer
set search_path to ''
as $function$
declare
  v_evaluation
    public.tmua_test_attempt_evaluations%rowtype;

  v_catalog
    public.tmua_test_catalog%rowtype;

  v_overall_raw integer := 0;

  v_authoritative_score numeric(3,1);

  v_conversion_version text;

  v_score_status text;
begin
  select *
  into v_evaluation
  from public.tmua_test_attempt_evaluations
  where attempt_id = p_attempt_id;

  if not found then
    return;
  end if;

  select *
  into v_catalog
  from public.tmua_test_catalog
  where test_id = v_evaluation.test_id;

  if not found then
    return;
  end if;

  v_overall_raw :=
    coalesce(
      v_evaluation.paper_1_raw_score,
      0
    ) +
    coalesce(
      v_evaluation.paper_2_raw_score,
      0
    );

  if v_catalog.score_conversion_profile is not null then
    select conversion_version
    into v_conversion_version
    from public.tmua_score_conversion_profiles
    where profile =
      v_catalog.score_conversion_profile;
  end if;

  if v_catalog.paper = 'full' then
    if v_evaluation.combined_score_eligible then
      if v_catalog.score_conversion_profile is null then
        v_score_status :=
          'missing_conversion_profile';

      else
        v_authoritative_score :=
          public.tmua_convert_overall_score(
            v_catalog.score_conversion_profile,
            v_overall_raw
          );

        if v_authoritative_score is null then
          v_score_status :=
            'missing_conversion_profile';
        else
          v_score_status :=
            'converted_combined_full_test';
        end if;
      end if;

    elsif v_evaluation.predictor_eligible then
      v_score_status :=
        'single_paper_evidence_only';

    else
      v_score_status :=
        'excluded';
    end if;

  elsif v_evaluation.predictor_eligible then
    -- A 20-question paper or a topic test contributes raw,
    -- weighted evidence. It is not converted into an invented
    -- overall TMUA score out of nine.
    v_score_status :=
      'raw_evidence_only';

  else
    v_score_status :=
      'excluded';
  end if;

  update public.tmua_test_attempt_evaluations
  set
    overall_raw_score =
      v_overall_raw,

    authoritative_tmua_score9 =
      v_authoritative_score,

    score_conversion_profile =
      v_catalog.score_conversion_profile,

    score_conversion_version =
      v_conversion_version,

    score_status =
      v_score_status,

    evaluated_at =
      now()

  where attempt_id = p_attempt_id;


  update public.practice_test_attempts
  set
    attempt_number =
      v_evaluation.attempt_number,

    paper_1_score =
      case
        when v_evaluation.paper in ('full', '1')
          then v_evaluation.paper_1_raw_score
        else null
      end,

    paper_2_score =
      case
        when v_evaluation.paper in ('full', '2')
          then v_evaluation.paper_2_raw_score
        else null
      end,

    is_full_timed_attempt =
      case
        when v_evaluation.paper = 'full'
          then
            v_evaluation.combined_score_eligible
        else false
      end,

    score_conversion_profile =
      v_catalog.score_conversion_profile,

    tmua_score9 =
      v_authoritative_score,

    predictor_metadata =
      coalesce(
        predictor_metadata,
        '{}'::jsonb
      ) ||
      jsonb_build_object(
        'recognised_tmua_test',
          true,

        'test_kind',
          v_evaluation.test_kind,

        'paper',
          v_evaluation.paper,

        'predictor_eligible',
          v_evaluation.predictor_eligible,

        'combined_score_eligible',
          v_evaluation.combined_score_eligible,

        'effective_weight',
          v_evaluation.effective_weight,

        'score_status',
          v_score_status,

        'authoritative_tmua_score9',
          v_authoritative_score,

        'score_conversion_profile',
          v_catalog.score_conversion_profile,

        'score_conversion_version',
          v_conversion_version,

        'raw_mark_authority',
          'submitted_answers_and_key_v1',

        'finalisation_version',
          '20260807-1'
      )

  where id = p_attempt_id;
end;
$function$;

revoke all
on function
  public.finalize_tmua_test_attempt_score(uuid)
from public, anon, authenticated;


create or replace function
  public.capture_tmua_test_score_finalisation()
returns trigger
language plpgsql
security definer
set search_path to ''
as $function$
begin
  perform
    public.finalize_tmua_test_attempt_score(
      NEW.id
    );

  return NEW;
end;
$function$;

revoke all
on function
  public.capture_tmua_test_score_finalisation()
from public, anon, authenticated;


drop trigger if exists
  trg_zz_finalize_tmua_practice_attempt
on public.practice_test_attempts;

-- PostgreSQL runs triggers of the same type in trigger-name
-- order. "trg_zz" therefore runs after the existing
-- "trg_evaluate" validity trigger.
create trigger
  trg_zz_finalize_tmua_practice_attempt

after insert or update of
  test_id,
  total_questions,
  score,
  answers,
  correct_answers,
  time_spent

on public.practice_test_attempts

for each row

execute function
  public.capture_tmua_test_score_finalisation();


do $backfill$
declare
  evaluation_record record;
begin
  for evaluation_record in
    select attempt_id
    from public.tmua_test_attempt_evaluations
  loop
    perform
      public.finalize_tmua_test_attempt_score(
        evaluation_record.attempt_id
      );
  end loop;
end;
$backfill$;


-- Historical ESAT records were previously given meaningless
-- TMUA scores by the generic submission route. They remain in
-- the shared attempt table but carry no TMUA conversion.
update public.practice_test_attempts
set
  tmua_score9 = null,

  score_conversion_profile = null,

  paper_1_score = null,

  paper_2_score = null,

  is_full_timed_attempt = null,

  predictor_metadata =
    coalesce(
      predictor_metadata,
      '{}'::jsonb
    ) ||
    jsonb_build_object(
      'recognised_tmua_test',
        false,

      'tmua_score_cleared',
        true,

      'finalisation_version',
        '20260807-1'
    )

where
  test_id like 'esat-%'
  or
  test_id =
    'esat-engineering-full-mock-test-1';


comment on table
  public.tmua_score_conversion_profiles
is
  'Authoritative 0-to-40 raw-score conversion profiles used for valid full TMUA tests.';

comment on column
  public.tmua_test_attempt_evaluations.authoritative_tmua_score9
is
  'Overall TMUA score generated only for a valid combined 40-question attempt. Single-paper and topic evidence remain unconverted raw evidence.';

comment on column
  public.tmua_test_attempt_evaluations.score_status
is
  'Explains whether the attempt received a combined full-test conversion, contributes raw/single-paper evidence, or was excluded.';