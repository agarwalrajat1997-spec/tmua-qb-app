-- TMUA Preparation Rank V1
-- Phase 3C3 persistence foundation.
--
-- This migration creates:
--   1. append-only explicit exclusion decisions
--   2. append-only cohort/ranking runs
--   3. append-only per-student ranking snapshots
--
-- It does not calculate ranks and does not modify Predictor V1.

create table public.tmua_preparation_rank_exclusions (
    id uuid primary key default gen_random_uuid(),

    user_id uuid not null,

    decision text not null
        check (
            decision in (
                'exclude',
                'include'
            )
        ),

    reason text not null
        check (
            length(trim(reason)) > 0
        ),

    created_at timestamptz not null default now()
);

comment on table public.tmua_preparation_rank_exclusions is
    'Append-only explicit Preparation Rank exclusion/include decisions. Latest event per user wins. Never infer exclusions from email addresses.';

create index tmua_preparation_rank_exclusions_user_created_idx
    on public.tmua_preparation_rank_exclusions (
        user_id,
        created_at desc,
        id desc
    );


create table public.tmua_preparation_rank_runs (
    id uuid primary key default gen_random_uuid(),

    model_version text not null
        check (
            length(trim(model_version)) > 0
        ),

    input_hash text not null
        check (
            input_hash ~ '^[0-9a-f]{64}$'
        ),

    cohort_as_of timestamptz not null,

    window_start timestamptz not null,

    entitled_auth_user_count integer not null
        check (
            entitled_auth_user_count >= 0
        ),

    excluded_user_count integer not null
        check (
            excluded_user_count >= 0
        ),

    active_cohort_size integer not null
        check (
            active_cohort_size >= 0
        ),

    rankable_count integer not null
        check (
            rankable_count >= 0
        ),

    cohort_details jsonb not null default '{}'::jsonb,

    created_at timestamptz not null default now(),

    constraint tmua_preparation_rank_runs_window_check
        check (
            window_start =
                cohort_as_of - interval '30 days'
        ),

    constraint tmua_preparation_rank_runs_rankable_check
        check (
            rankable_count <= active_cohort_size
        ),

    constraint tmua_preparation_rank_runs_excluded_check
        check (
            excluded_user_count <= entitled_auth_user_count
        ),

    constraint tmua_preparation_rank_runs_dedupe
        unique (
            model_version,
            input_hash
        )
);

comment on table public.tmua_preparation_rank_runs is
    'Append-only TMUA Preparation Rank cohort runs. A run records the factual rolling-30-day cohort used for ranking.';


create table public.tmua_preparation_rank_snapshots (
    id uuid primary key default gen_random_uuid(),

    run_id uuid not null
        references public.tmua_preparation_rank_runs(id)
        on delete restrict,

    user_id uuid not null,

    model_version text not null
        check (
            length(trim(model_version)) > 0
        ),

    genuine_preparation_evidence boolean not null,

    actual_preparation_score double precision,

    actual_preparation_rank integer,

    actual_active_cohort_size integer not null
        check (
            actual_active_cohort_size >= 1
        ),

    performance_component double precision not null
        check (
            performance_component >= 0
            and performance_component <= 1
        ),

    breadth_component double precision not null
        check (
            breadth_component >= 0
            and breadth_component <= 1
        ),

    evidence_depth_component double precision not null
        check (
            evidence_depth_component >= 0
            and evidence_depth_component <= 1
        ),

    recent_activity_component double precision not null
        check (
            recent_activity_component >= 0
            and recent_activity_component <= 1
        ),

    consistency_component double precision not null
        check (
            consistency_component >= 0
            and consistency_component <= 1
        ),

    recovery_component double precision not null
        check (
            recovery_component >= 0
            and recovery_component <= 1
        ),

    predicted_tmua_score9 double precision
        check (
            predicted_tmua_score9 is null
            or (
                predicted_tmua_score9 >= 1
                and predicted_tmua_score9 <= 9
            )
        ),

    predictor_input_hash text
        check (
            predictor_input_hash is null
            or predictor_input_hash ~ '^[0-9a-f]{64}$'
        ),

    broad_or_full_independent_test_families integer not null
        check (
            broad_or_full_independent_test_families >= 0
        ),

    predictor_test_weight double precision not null
        check (
            predictor_test_weight >= 0
        ),

    trusted_unique_first_exposures integer not null
        check (
            trusted_unique_first_exposures >= 0
        ),

    trusted_canonical_topic_coverage double precision not null
        check (
            trusted_canonical_topic_coverage >= 0
            and trusted_canonical_topic_coverage <= 1
        ),

    distinct_canonical_qb_interactions_30d integer not null
        check (
            distinct_canonical_qb_interactions_30d >= 0
        ),

    independent_recognised_test_families_30d integer not null
        check (
            independent_recognised_test_families_30d >= 0
        ),

    recovery_value double precision
        check (
            recovery_value is null
            or (
                recovery_value >= 0
                and recovery_value <= 1
            )
        ),

    evidence_details jsonb not null default '{}'::jsonb,

    created_at timestamptz not null default now(),

    constraint tmua_preparation_rank_snapshots_score_range
        check (
            actual_preparation_score is null
            or (
                actual_preparation_score >= 0
                and actual_preparation_score <= 100
            )
        ),

    constraint tmua_preparation_rank_snapshots_rank_range
        check (
            actual_preparation_rank is null
            or (
                actual_preparation_rank >= 1
                and actual_preparation_rank <=
                    actual_active_cohort_size
            )
        ),

    constraint tmua_preparation_rank_snapshots_evidence_state
        check (
            (
                genuine_preparation_evidence is true
                and actual_preparation_score is not null
                and actual_preparation_rank is not null
            )
            or
            (
                genuine_preparation_evidence is false
                and actual_preparation_score is null
                and actual_preparation_rank is null
                and performance_component = 0
                and breadth_component = 0
                and evidence_depth_component = 0
                and recent_activity_component = 0
                and consistency_component = 0
                and recovery_component = 0
            )
        ),

    constraint tmua_preparation_rank_snapshots_run_user_unique
        unique (
            run_id,
            user_id
        )
);

comment on table public.tmua_preparation_rank_snapshots is
    'Append-only per-student Preparation Rank V1 snapshots. Students may read only their own snapshots.';


create index tmua_preparation_rank_snapshots_user_created_idx
    on public.tmua_preparation_rank_snapshots (
        user_id,
        created_at desc
    );

create index tmua_preparation_rank_snapshots_run_rank_idx
    on public.tmua_preparation_rank_snapshots (
        run_id,
        actual_preparation_rank
    )
    where actual_preparation_rank is not null;


alter table public.tmua_preparation_rank_exclusions
    enable row level security;

alter table public.tmua_preparation_rank_runs
    enable row level security;

alter table public.tmua_preparation_rank_snapshots
    enable row level security;


revoke all on table public.tmua_preparation_rank_exclusions
    from anon, authenticated, service_role;

revoke all on table public.tmua_preparation_rank_runs
    from anon, authenticated, service_role;

revoke all on table public.tmua_preparation_rank_snapshots
    from anon, authenticated, service_role;


grant select, insert
    on table public.tmua_preparation_rank_exclusions
    to service_role;

grant select, insert
    on table public.tmua_preparation_rank_runs
    to service_role;

grant select, insert
    on table public.tmua_preparation_rank_snapshots
    to service_role;

grant select
    on table public.tmua_preparation_rank_snapshots
    to authenticated;


create policy tmua_preparation_rank_snapshots_select_own
    on public.tmua_preparation_rank_snapshots
    for select
    to authenticated
    using (
        auth.uid() = user_id
    );


-- Deliberately no authenticated INSERT / UPDATE / DELETE policy.
--
-- Deliberately no authenticated access to:
--   tmua_preparation_rank_runs
--   tmua_preparation_rank_exclusions
--
-- The service role receives SELECT + INSERT only.
-- UPDATE and DELETE remain unavailable at application-role level.
--
-- Exclusion decisions are append-only:
-- latest (created_at, id) event for a user wins.
--
-- Rank runs and snapshots are append-only.
-- No schema object here alters TMUA Predictor V1.
