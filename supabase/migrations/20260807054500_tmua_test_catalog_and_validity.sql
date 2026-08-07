create table if not exists public.tmua_test_catalog (
  test_id text primary key,
  title text not null,

  test_kind text not null
    check (
      test_kind in (
        'official_full',
        'mock_full',
        'paper_test',
        'topic_test',
        'specimen_full'
      )
    ),

  paper text not null
    check (paper in ('full', '1', '2')),

  topic_breadth text not null
    check (
      topic_breadth in (
        'full_syllabus',
        'broad',
        'narrow'
      )
    ),

  expected_questions integer not null
    check (expected_questions in (20, 40)),

  expected_seconds integer not null
    check (expected_seconds > 0),

  minimum_partial_answered integer not null default 12,
  minimum_full_weight_answered integer not null default 18,

  minimum_average_seconds numeric(8,2)
    not null default 10,

  base_weight numeric(6,3) not null
    check (base_weight >= 0 and base_weight <= 1.5),

  score_conversion_profile text,

  predictor_enabled boolean not null default true,
  leaderboard_enabled boolean not null default true,

  catalogue_version text not null default '20260807-2',

  topics text[] not null default '{}'::text[],
  metadata jsonb not null default '{}'::jsonb,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.tmua_test_catalog
  enable row level security;

drop policy if exists
  "Authenticated users read TMUA test catalogue"
on public.tmua_test_catalog;

create policy
  "Authenticated users read TMUA test catalogue"
on public.tmua_test_catalog
for select
to authenticated
using (true);

grant select
on public.tmua_test_catalog
to authenticated;


insert into public.tmua_test_catalog (
  test_id,
  title,
  test_kind,
  paper,
  topic_breadth,
  expected_questions,
  expected_seconds,
  minimum_partial_answered,
  minimum_full_weight_answered,
  minimum_average_seconds,
  base_weight,
  score_conversion_profile,
  predictor_enabled,
  leaderboard_enabled,
  catalogue_version,
  topics,
  metadata
)
values
(
  'full-mock-01-all-topics',
  'TMUA Mock Full Test 1',
  'mock_full',
  'full',
  'full_syllabus',
  40,
  9000,
  12,
  18,
  10,
  0.950,
  'mock1',
  true,
  true,
  '20260807-2',
  array['all-topics'],
  '{"source":"thriving-scholars"}'::jsonb
),
(
  'full-mock-02-all-topics',
  'TMUA Mock Full Test 2',
  'mock_full',
  'full',
  'full_syllabus',
  40,
  9000,
  12,
  18,
  10,
  0.950,
  'mock2',
  true,
  true,
  '20260807-2',
  array['all-topics'],
  '{"source":"thriving-scholars"}'::jsonb
),
(
  'full-official-2016',
  'TMUA Official 2016',
  'official_full',
  'full',
  'full_syllabus',
  40,
  9000,
  12,
  18,
  10,
  1.000,
  'official-2016',
  true,
  true,
  '20260807-2',
  array['all-topics'],
  '{"year":2016,"conversion":"official"}'::jsonb
),
(
  'full-official-2017',
  'TMUA Official 2017',
  'official_full',
  'full',
  'full_syllabus',
  40,
  9000,
  12,
  18,
  10,
  1.000,
  'official-2017',
  true,
  true,
  '20260807-2',
  array['all-topics'],
  '{"year":2017,"conversion":"official"}'::jsonb
),
(
  'full-official-2018',
  'TMUA Official 2018',
  'official_full',
  'full',
  'full_syllabus',
  40,
  9000,
  12,
  18,
  10,
  1.000,
  'official-2018',
  true,
  true,
  '20260807-2',
  array['all-topics'],
  '{"year":2018,"conversion":"official"}'::jsonb
),
(
  'full-official-2019',
  'TMUA Official 2019',
  'official_full',
  'full',
  'full_syllabus',
  40,
  9000,
  12,
  18,
  10,
  1.000,
  'official-2019',
  true,
  true,
  '20260807-2',
  array['all-topics'],
  '{"year":2019,"conversion":"official"}'::jsonb
),
(
  'full-official-2020',
  'TMUA Official 2020',
  'official_full',
  'full',
  'full_syllabus',
  40,
  9000,
  12,
  18,
  10,
  1.000,
  'official-2020',
  true,
  true,
  '20260807-2',
  array['all-topics'],
  '{"year":2020,"conversion":"official"}'::jsonb
),
(
  'full-official-2021',
  'TMUA Official 2021',
  'official_full',
  'full',
  'full_syllabus',
  40,
  9000,
  12,
  18,
  10,
  1.000,
  'official-2021',
  true,
  true,
  '20260807-2',
  array['all-topics'],
  '{"year":2021,"conversion":"official"}'::jsonb
),
(
  'full-official-2022',
  'TMUA Official 2022',
  'official_full',
  'full',
  'full_syllabus',
  40,
  9000,
  12,
  18,
  10,
  1.000,
  'official-2022',
  true,
  true,
  '20260807-2',
  array['all-topics'],
  '{"year":2022,"conversion":"official"}'::jsonb
),
(
  'full-official-2023',
  'TMUA Official 2023',
  'official_full',
  'full',
  'full_syllabus',
  40,
  9000,
  12,
  18,
  10,
  1.000,
  'official-2023',
  true,
  true,
  '20260807-2',
  array['all-topics'],
  '{"year":2023,"conversion":"official"}'::jsonb
),
(
  'full-specimen',
  'TMUA Specimen Full Test',
  'specimen_full',
  'full',
  'full_syllabus',
  40,
  9000,
  12,
  18,
  10,
  0.850,
  'specimen-estimate',
  true,
  true,
  '20260807-2',
  array['all-topics'],
  '{"conversion":"estimated"}'::jsonb
),
(
  'p1-mock-01-algebra-sequences-functions-geometry',
  'TMUA Topic Test 1 — Algebra, Sequences, Functions and Geometry',
  'topic_test',
  '1',
  'broad',
  20,
  4500,
  12,
  18,
  10,
  0.720,
  null,
  true,
  true,
  '20260807-2',
  array[
    'algebra',
    'sequences',
    'functions',
    'geometry'
  ],
  '{}'::jsonb
),
(
  'p1-mock-02-graphs-trig-logs',
  'TMUA Topic Test 2 — Graphs, Trigonometry and Logarithms',
  'topic_test',
  '1',
  'broad',
  20,
  4500,
  12,
  18,
  10,
  0.680,
  null,
  true,
  true,
  '20260807-2',
  array[
    'graphs',
    'trigonometry',
    'logarithms'
  ],
  '{}'::jsonb
),
(
  'p1-mock-03-calculus',
  'TMUA Topic Test 3 — Calculus',
  'topic_test',
  '1',
  'narrow',
  20,
  4500,
  12,
  18,
  10,
  0.600,
  null,
  true,
  true,
  '20260807-2',
  array['calculus'],
  '{}'::jsonb
),
(
  'p2-mock-04-logic-proofs',
  'TMUA Topic Test 4 — Logic and Proofs',
  'topic_test',
  '2',
  'narrow',
  20,
  4500,
  12,
  18,
  10,
  0.620,
  null,
  true,
  true,
  '20260807-2',
  array[
    'logic',
    'proof'
  ],
  '{}'::jsonb
),
(
  'p1-mock-05-all-topics',
  'TMUA Topic Test 5 — Mixed-Topic Paper 1',
  'paper_test',
  '1',
  'full_syllabus',
  20,
  4500,
  12,
  18,
  10,
  0.780,
  null,
  true,
  true,
  '20260807-2',
  array['paper-1-all-topics'],
  '{}'::jsonb
),
(
  'p2-mock-06-all-topics',
  'TMUA Mock Test 6 — Paper 2',
  'paper_test',
  '2',
  'full_syllabus',
  20,
  4500,
  12,
  18,
  10,
  0.780,
  null,
  true,
  true,
  '20260807-2',
  array['paper-2-all-topics'],
  '{}'::jsonb
),
(
  'tmua-2024-2025-challenging-mock',
  'TMUA 2024–2025 Informed Challenging Full Test',
  'mock_full',
  'full',
  'full_syllabus',
  40,
  9000,
  12,
  18,
  10,
  0.900,
  'informed2024-2025',
  true,
  true,
  '20260807-2',
  array['all-topics'],
  '{"difficulty":"challenging"}'::jsonb
)
on conflict (test_id) do update
set
  title = excluded.title,
  test_kind = excluded.test_kind,
  paper = excluded.paper,
  topic_breadth = excluded.topic_breadth,
  expected_questions = excluded.expected_questions,
  expected_seconds = excluded.expected_seconds,
  minimum_partial_answered =
    excluded.minimum_partial_answered,
  minimum_full_weight_answered =
    excluded.minimum_full_weight_answered,
  minimum_average_seconds =
    excluded.minimum_average_seconds,
  base_weight = excluded.base_weight,
  score_conversion_profile =
    excluded.score_conversion_profile,
  predictor_enabled = excluded.predictor_enabled,
  leaderboard_enabled = excluded.leaderboard_enabled,
  catalogue_version = excluded.catalogue_version,
  topics = excluded.topics,
  metadata = excluded.metadata,
  updated_at = now();


create table if not exists
  public.tmua_test_attempt_evaluations (
    attempt_id uuid primary key
      references public.practice_test_attempts(id)
      on delete cascade,

    user_id uuid not null,
    test_id text not null
      references public.tmua_test_catalog(test_id),

    test_kind text not null,
    paper text not null,
    catalogue_version text not null,

    attempt_number integer not null,

    answered_count integer not null default 0,

    paper_1_answered_count integer not null default 0,
    paper_2_answered_count integer not null default 0,

    elapsed_seconds numeric(12,3) not null default 0,

    paper_1_elapsed_seconds numeric(12,3)
      not null default 0,

    paper_2_elapsed_seconds numeric(12,3)
      not null default 0,

    paper_1_raw_score integer not null default 0,
    paper_2_raw_score integer not null default 0,

    paper_1_completion_factor numeric(7,4)
      not null default 0,

    paper_2_completion_factor numeric(7,4)
      not null default 0,

    paper_1_timing_factor numeric(7,4)
      not null default 0,

    paper_2_timing_factor numeric(7,4)
      not null default 0,

    paper_1_validity_factor numeric(7,4)
      not null default 0,

    paper_2_validity_factor numeric(7,4)
      not null default 0,

    overall_validity_factor numeric(7,4)
      not null default 0,

    base_weight numeric(7,4) not null default 0,

    paper_1_effective_weight numeric(7,4)
      not null default 0,

    paper_2_effective_weight numeric(7,4)
      not null default 0,

    effective_weight numeric(7,4)
      not null default 0,

    predictor_eligible boolean not null default false,

    combined_score_eligible boolean
      not null default false,

    exclusion_reason text,

    details jsonb not null default '{}'::jsonb,

    evaluated_at timestamptz not null default now()
  );

create index if not exists
  tmua_attempt_evaluations_user_test_idx
on public.tmua_test_attempt_evaluations(
  user_id,
  test_id,
  attempt_number
);

create index if not exists
  tmua_attempt_evaluations_predictor_idx
on public.tmua_test_attempt_evaluations(
  user_id,
  predictor_eligible,
  evaluated_at desc
);

alter table public.tmua_test_attempt_evaluations
  enable row level security;

drop policy if exists
  "Users read their own TMUA test evaluations"
on public.tmua_test_attempt_evaluations;

create policy
  "Users read their own TMUA test evaluations"
on public.tmua_test_attempt_evaluations
for select
to authenticated
using (auth.uid() = user_id);

grant select
on public.tmua_test_attempt_evaluations
to authenticated;


create or replace function
  public.tmua_jsonb_answered_count(
    p_values jsonb,
    p_offset integer,
    p_limit integer
  )
returns integer
language sql
immutable
set search_path to ''
as $function$
  select count(*)::integer
  from jsonb_array_elements(
    case
      when jsonb_typeof(p_values) = 'array'
        then p_values
      else '[]'::jsonb
    end
  ) with ordinality as item(value, position)
  where position > p_offset
    and position <= p_offset + p_limit
    and jsonb_typeof(value) <> 'null'
    and nullif(btrim(value #>> '{}'), '') is not null;
$function$;


create or replace function
  public.tmua_jsonb_correct_count(
    p_answers jsonb,
    p_correct_answers jsonb,
    p_offset integer,
    p_limit integer
  )
returns integer
language sql
immutable
set search_path to ''
as $function$
  select count(*)::integer
  from jsonb_array_elements(
    case
      when jsonb_typeof(p_answers) = 'array'
        then p_answers
      else '[]'::jsonb
    end
  ) with ordinality as answer(value, position)
  join jsonb_array_elements(
    case
      when jsonb_typeof(p_correct_answers) = 'array'
        then p_correct_answers
      else '[]'::jsonb
    end
  ) with ordinality as expected(value, position)
    using (position)
  where answer.position > p_offset
    and answer.position <= p_offset + p_limit
    and jsonb_typeof(answer.value) <> 'null'
    and nullif(
      btrim(answer.value #>> '{}'),
      ''
    ) is not null
    and upper(btrim(answer.value #>> '{}')) =
        upper(btrim(expected.value #>> '{}'));
$function$;


create or replace function
  public.tmua_jsonb_elapsed_seconds(
    p_values jsonb,
    p_offset integer,
    p_limit integer
  )
returns numeric
language sql
immutable
set search_path to ''
as $function$
  select coalesce(
    sum(
      case
        when value_text ~
          '^[+-]?[0-9]+([.][0-9]+)?$'
        then greatest(0, value_text::numeric)
        else 0
      end
    ),
    0
  )
  from (
    select
      item.value #>> '{}' as value_text,
      item.position
    from jsonb_array_elements(
      case
        when jsonb_typeof(p_values) = 'array'
          then p_values
        else '[]'::jsonb
      end
    ) with ordinality as item(value, position)
  ) values_with_positions
  where position > p_offset
    and position <= p_offset + p_limit;
$function$;


create or replace function
  public.tmua_completion_factor(
    p_answered integer,
    p_minimum_partial_answered integer,
    p_minimum_full_weight_answered integer
  )
returns numeric
language sql
immutable
set search_path to ''
as $function$
  select
    case
      when coalesce(p_answered, 0) <
        p_minimum_partial_answered
        then 0.0000

      when p_answered <
        greatest(
          p_minimum_partial_answered,
          p_minimum_full_weight_answered - 2
        )
        then 0.3500

      when p_answered <
        p_minimum_full_weight_answered
        then 0.7000

      else 1.0000
    end;
$function$;


create or replace function
  public.tmua_timing_factor(
    p_elapsed_seconds numeric,
    p_answered integer,
    p_expected_seconds integer,
    p_minimum_average_seconds numeric
  )
returns numeric
language sql
immutable
set search_path to ''
as $function$
  select
    case
      when coalesce(p_answered, 0) <= 0
        then 0.0000

      when coalesce(p_elapsed_seconds, 0) <= 0
        then 0.0000

      when (
        p_elapsed_seconds /
        greatest(p_answered, 1)
      ) < p_minimum_average_seconds
        then 0.0000

      when (
        p_elapsed_seconds /
        greatest(p_expected_seconds, 1)
      ) < 0.1500
        then 0.0000

      when (
        p_elapsed_seconds /
        greatest(p_expected_seconds, 1)
      ) < 0.2500
        then 0.1500

      when (
        p_elapsed_seconds /
        greatest(p_expected_seconds, 1)
      ) < 0.3500
        then 0.4500

      when (
        p_elapsed_seconds /
        greatest(p_expected_seconds, 1)
      ) < 0.5000
        then 0.7500

      when (
        p_elapsed_seconds /
        greatest(p_expected_seconds, 1)
      ) <= 1.3500
        then 1.0000

      when (
        p_elapsed_seconds /
        greatest(p_expected_seconds, 1)
      ) <= 2.0000
        then 0.9000

      else 0.7500
    end;
$function$;


create or replace function
  public.evaluate_tmua_test_attempt(
    p_attempt_id uuid
  )
returns void
language plpgsql
security definer
set search_path to ''
as $function$
declare
  v_attempt public.practice_test_attempts%rowtype;
  v_catalog public.tmua_test_catalog%rowtype;

  v_attempt_number integer;

  v_answered integer := 0;
  v_elapsed numeric := 0;

  v_p1_answered integer := 0;
  v_p2_answered integer := 0;

  v_p1_elapsed numeric := 0;
  v_p2_elapsed numeric := 0;

  v_p1_raw integer := 0;
  v_p2_raw integer := 0;

  v_p1_completion numeric := 0;
  v_p2_completion numeric := 0;

  v_p1_timing numeric := 0;
  v_p2_timing numeric := 0;

  v_p1_validity numeric := 0;
  v_p2_validity numeric := 0;

  v_overall_validity numeric := 0;

  v_p1_weight numeric := 0;
  v_p2_weight numeric := 0;
  v_effective_weight numeric := 0;

  v_predictor_eligible boolean := false;
  v_combined_eligible boolean := false;

  v_exclusion_reason text;
begin
  select *
  into v_attempt
  from public.practice_test_attempts
  where id = p_attempt_id;

  if not found then
    return;
  end if;

  -- Re-evaluation is replace-based. If a recognised TMUA attempt
  -- is later changed to an unknown or non-TMUA test ID, its old
  -- predictor evaluation must not remain active.
  delete from public.tmua_test_attempt_evaluations
  where attempt_id = p_attempt_id;

  select *
  into v_catalog
  from public.tmua_test_catalog
  where test_id = v_attempt.test_id
    and predictor_enabled = true;

  -- Unknown tests, including ESAT, are deliberately excluded.
  if not found then
    return;
  end if;

  select count(*)::integer
  into v_attempt_number
  from public.practice_test_attempts earlier
  where earlier.user_id = v_attempt.user_id
    and earlier.test_id = v_attempt.test_id
    and (
      coalesce(
        earlier.submitted_at,
        '1970-01-01'::timestamptz
      ) <
      coalesce(
        v_attempt.submitted_at,
        '1970-01-01'::timestamptz
      )
      or (
        coalesce(
          earlier.submitted_at,
          '1970-01-01'::timestamptz
        ) =
        coalesce(
          v_attempt.submitted_at,
          '1970-01-01'::timestamptz
        )
        and earlier.id::text <= v_attempt.id::text
      )
    );

  v_attempt_number := greatest(v_attempt_number, 1);

  v_answered :=
    public.tmua_jsonb_answered_count(
      v_attempt.answers,
      0,
      v_catalog.expected_questions
    );

  v_elapsed :=
    public.tmua_jsonb_elapsed_seconds(
      v_attempt.time_spent,
      0,
      v_catalog.expected_questions
    );

  if v_catalog.paper = 'full' then
    v_p1_answered :=
      public.tmua_jsonb_answered_count(
        v_attempt.answers,
        0,
        20
      );

    v_p2_answered :=
      public.tmua_jsonb_answered_count(
        v_attempt.answers,
        20,
        20
      );

    v_p1_elapsed :=
      public.tmua_jsonb_elapsed_seconds(
        v_attempt.time_spent,
        0,
        20
      );

    v_p2_elapsed :=
      public.tmua_jsonb_elapsed_seconds(
        v_attempt.time_spent,
        20,
        20
      );

    v_p1_raw :=
      public.tmua_jsonb_correct_count(
        v_attempt.answers,
        v_attempt.correct_answers,
        0,
        20
      );

    v_p2_raw :=
      public.tmua_jsonb_correct_count(
        v_attempt.answers,
        v_attempt.correct_answers,
        20,
        20
      );

    v_p1_completion :=
      public.tmua_completion_factor(
        v_p1_answered,
        v_catalog.minimum_partial_answered,
        v_catalog.minimum_full_weight_answered
      );

    v_p2_completion :=
      public.tmua_completion_factor(
        v_p2_answered,
        v_catalog.minimum_partial_answered,
        v_catalog.minimum_full_weight_answered
      );

    v_p1_timing :=
      public.tmua_timing_factor(
        v_p1_elapsed,
        v_p1_answered,
        4500,
        v_catalog.minimum_average_seconds
      );

    v_p2_timing :=
      public.tmua_timing_factor(
        v_p2_elapsed,
        v_p2_answered,
        4500,
        v_catalog.minimum_average_seconds
      );

    v_p1_validity :=
      v_p1_completion * v_p1_timing;

    v_p2_validity :=
      v_p2_completion * v_p2_timing;

    v_overall_validity :=
      (v_p1_validity + v_p2_validity) / 2.0;

    -- Either properly completed 20-question paper may stand on
    -- its own as substantial evidence. A single valid paper can
    -- therefore carry up to 75% of the full-test base weight.
    v_p1_weight :=
      v_catalog.base_weight *
      0.7500 *
      v_p1_validity;

    v_p2_weight :=
      v_catalog.base_weight *
      0.7500 *
      v_p2_validity;

    -- A combined score is allowed only when both papers have at
    -- least 18 answered questions and each reaches substantial
    -- timing-and-completion validity. Merely having timing > 0
    -- is not sufficient.
    v_combined_eligible :=
      v_p1_answered >=
        v_catalog.minimum_full_weight_answered
      and
      v_p2_answered >=
        v_catalog.minimum_full_weight_answered
      and
      v_p1_validity >= 0.7500
      and
      v_p2_validity >= 0.7500;

    -- When both papers are valid, the full attempt is capped at
    -- the normal full-test base weight. Otherwise, retain only
    -- the stronger independently valid paper at test level.
    v_effective_weight :=
      case
        when v_combined_eligible then
          v_catalog.base_weight *
          (
            v_p1_validity +
            v_p2_validity
          ) / 2.0

        else greatest(
          v_p1_weight,
          v_p2_weight
        )
      end;

  elsif v_catalog.paper = '1' then
    v_p1_answered := v_answered;
    v_p1_elapsed := v_elapsed;

    v_p1_raw :=
      public.tmua_jsonb_correct_count(
        v_attempt.answers,
        v_attempt.correct_answers,
        0,
        20
      );

    v_p1_completion :=
      public.tmua_completion_factor(
        v_p1_answered,
        v_catalog.minimum_partial_answered,
        v_catalog.minimum_full_weight_answered
      );

    v_p1_timing :=
      public.tmua_timing_factor(
        v_p1_elapsed,
        v_p1_answered,
        v_catalog.expected_seconds,
        v_catalog.minimum_average_seconds
      );

    v_p1_validity :=
      v_p1_completion * v_p1_timing;

    v_overall_validity := v_p1_validity;

    v_p1_weight :=
      v_catalog.base_weight * v_p1_validity;

    v_effective_weight := v_p1_weight;

  else
    v_p2_answered := v_answered;
    v_p2_elapsed := v_elapsed;

    v_p2_raw :=
      public.tmua_jsonb_correct_count(
        v_attempt.answers,
        v_attempt.correct_answers,
        0,
        20
      );

    v_p2_completion :=
      public.tmua_completion_factor(
        v_p2_answered,
        v_catalog.minimum_partial_answered,
        v_catalog.minimum_full_weight_answered
      );

    v_p2_timing :=
      public.tmua_timing_factor(
        v_p2_elapsed,
        v_p2_answered,
        v_catalog.expected_seconds,
        v_catalog.minimum_average_seconds
      );

    v_p2_validity :=
      v_p2_completion * v_p2_timing;

    v_overall_validity := v_p2_validity;

    v_p2_weight :=
      v_catalog.base_weight * v_p2_validity;

    v_effective_weight := v_p2_weight;
  end if;

  v_predictor_eligible :=
    v_effective_weight > 0;

  if v_predictor_eligible then
    v_exclusion_reason := null;

  elsif v_answered <
    v_catalog.minimum_partial_answered then

    v_exclusion_reason :=
      'insufficient_completion';

  elsif v_elapsed <= 0 then
    v_exclusion_reason :=
      'missing_timing';

  elsif (
    v_elapsed /
    greatest(v_answered, 1)
  ) < v_catalog.minimum_average_seconds then

    v_exclusion_reason :=
      'average_under_10_seconds';

  else
    v_exclusion_reason :=
      'implausibly_short_duration';
  end if;

  insert into
    public.tmua_test_attempt_evaluations (
      attempt_id,
      user_id,
      test_id,
      test_kind,
      paper,
      catalogue_version,
      attempt_number,
      answered_count,
      paper_1_answered_count,
      paper_2_answered_count,
      elapsed_seconds,
      paper_1_elapsed_seconds,
      paper_2_elapsed_seconds,
      paper_1_raw_score,
      paper_2_raw_score,
      paper_1_completion_factor,
      paper_2_completion_factor,
      paper_1_timing_factor,
      paper_2_timing_factor,
      paper_1_validity_factor,
      paper_2_validity_factor,
      overall_validity_factor,
      base_weight,
      paper_1_effective_weight,
      paper_2_effective_weight,
      effective_weight,
      predictor_eligible,
      combined_score_eligible,
      exclusion_reason,
      details,
      evaluated_at
    )
  values (
    v_attempt.id,
    v_attempt.user_id,
    v_attempt.test_id,
    v_catalog.test_kind,
    v_catalog.paper,
    v_catalog.catalogue_version,
    v_attempt_number,
    v_answered,
    v_p1_answered,
    v_p2_answered,
    v_elapsed,
    v_p1_elapsed,
    v_p2_elapsed,
    v_p1_raw,
    v_p2_raw,
    v_p1_completion,
    v_p2_completion,
    v_p1_timing,
    v_p2_timing,
    v_p1_validity,
    v_p2_validity,
    v_overall_validity,
    v_catalog.base_weight,
    v_p1_weight,
    v_p2_weight,
    v_effective_weight,
    v_predictor_eligible,
    v_combined_eligible,
    v_exclusion_reason,
    jsonb_build_object(
      'minimum_partial_answered',
        v_catalog.minimum_partial_answered,
      'minimum_full_weight_answered',
        v_catalog.minimum_full_weight_answered,
      'minimum_average_seconds',
        v_catalog.minimum_average_seconds,
      'overall_average_seconds',
        case
          when v_answered > 0
            then round(v_elapsed / v_answered, 3)
          else 0
        end,
      'paper_1_average_seconds',
        case
          when v_p1_answered > 0
            then round(
              v_p1_elapsed / v_p1_answered,
              3
            )
          else 0
        end,
      'paper_2_average_seconds',
        case
          when v_p2_answered > 0
            then round(
              v_p2_elapsed / v_p2_answered,
              3
            )
          else 0
        end,
      'score_conversion_profile',
        v_catalog.score_conversion_profile,
      'paper_1_predictor_usable',
        v_p1_validity > 0,
      'paper_2_predictor_usable',
        v_p2_validity > 0,
      'combined_score_eligible',
        v_combined_eligible,
      'evaluation_version',
        '20260807-2'
    ),
    now()
  )
  on conflict (attempt_id) do update
  set
    user_id = excluded.user_id,
    test_id = excluded.test_id,
    test_kind = excluded.test_kind,
    paper = excluded.paper,
    catalogue_version = excluded.catalogue_version,
    attempt_number = excluded.attempt_number,
    answered_count = excluded.answered_count,
    paper_1_answered_count =
      excluded.paper_1_answered_count,
    paper_2_answered_count =
      excluded.paper_2_answered_count,
    elapsed_seconds = excluded.elapsed_seconds,
    paper_1_elapsed_seconds =
      excluded.paper_1_elapsed_seconds,
    paper_2_elapsed_seconds =
      excluded.paper_2_elapsed_seconds,
    paper_1_raw_score =
      excluded.paper_1_raw_score,
    paper_2_raw_score =
      excluded.paper_2_raw_score,
    paper_1_completion_factor =
      excluded.paper_1_completion_factor,
    paper_2_completion_factor =
      excluded.paper_2_completion_factor,
    paper_1_timing_factor =
      excluded.paper_1_timing_factor,
    paper_2_timing_factor =
      excluded.paper_2_timing_factor,
    paper_1_validity_factor =
      excluded.paper_1_validity_factor,
    paper_2_validity_factor =
      excluded.paper_2_validity_factor,
    overall_validity_factor =
      excluded.overall_validity_factor,
    base_weight = excluded.base_weight,
    paper_1_effective_weight =
      excluded.paper_1_effective_weight,
    paper_2_effective_weight =
      excluded.paper_2_effective_weight,
    effective_weight =
      excluded.effective_weight,
    predictor_eligible =
      excluded.predictor_eligible,
    combined_score_eligible =
      excluded.combined_score_eligible,
    exclusion_reason =
      excluded.exclusion_reason,
    details = excluded.details,
    evaluated_at = now();
end;
$function$;

revoke all
on function public.evaluate_tmua_test_attempt(uuid)
from public, anon, authenticated;


create or replace function
  public.capture_tmua_test_attempt_evaluation()
returns trigger
language plpgsql
security definer
set search_path to ''
as $function$
begin
  perform public.evaluate_tmua_test_attempt(NEW.id);
  return NEW;
end;
$function$;

revoke all
on function
  public.capture_tmua_test_attempt_evaluation()
from public, anon, authenticated;


drop trigger if exists
  trg_evaluate_tmua_practice_attempt
on public.practice_test_attempts;

create trigger
  trg_evaluate_tmua_practice_attempt
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
  public.capture_tmua_test_attempt_evaluation();


do $backfill$
declare
  attempt_record record;
begin
  for attempt_record in
    select attempt.id
    from public.practice_test_attempts attempt
    join public.tmua_test_catalog catalogue
      on catalogue.test_id = attempt.test_id
    where catalogue.predictor_enabled = true
  loop
    perform public.evaluate_tmua_test_attempt(
      attempt_record.id
    );
  end loop;
end;
$backfill$;


comment on table public.tmua_test_catalog is
  'Authoritative catalogue of TMUA practice tests and predictor validity settings. ESAT tests are deliberately absent.';

comment on table
  public.tmua_test_attempt_evaluations
is
  'Validity and evidence-weight assessment for each recognised TMUA practice-test attempt. Full-paper sections are evaluated independently.';

comment on column
  public.tmua_test_attempt_evaluations.combined_score_eligible
is
  'True only when both 20-question papers have sufficient completion and valid timing. A valid single paper may still contribute independently.';