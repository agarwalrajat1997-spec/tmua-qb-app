create table public.tmua_prediction_snapshots (
  id uuid primary key default gen_random_uuid(),

  user_id uuid not null
    references auth.users(id)
    on delete cascade,

  model_version text not null
    check (btrim(model_version) <> ''),

  input_hash text not null
    check (btrim(input_hash) <> ''),

  prediction_status text not null
    check (
      prediction_status in (
        'predicted',
        'insufficient_evidence'
      )
    ),

  predicted_tmua_score9 numeric(4,2),
  lower_bound numeric(4,2),
  upper_bound numeric(4,2),

  confidence text
    check (
      confidence is null
      or confidence in (
        'low',
        'medium',
        'high'
      )
    ),

  test_signal_score9 numeric(4,2),

  test_weight numeric(9,4)
    not null default 0
    check (test_weight >= 0),

  test_evidence_count integer
    not null default 0
    check (test_evidence_count >= 0),

  independent_test_count integer
    not null default 0
    check (independent_test_count >= 0),

  combined_full_count integer
    not null default 0
    check (combined_full_count >= 0),

  qb_signal_score9 numeric(4,2),

  qb_weight numeric(9,4)
    not null default 0
    check (qb_weight >= 0),

  qb_unique_questions integer
    not null default 0
    check (qb_unique_questions >= 0),

  qb_topic_coverage numeric(7,4)
    not null default 0
    check (
      qb_topic_coverage >= 0
      and qb_topic_coverage <= 1
    ),

  conversion_set_hash text not null
    check (btrim(conversion_set_hash) <> ''),

  active_topic_set_hash text not null
    check (btrim(active_topic_set_hash) <> ''),

  evidence_details jsonb
    not null default '{}'::jsonb
    check (
      jsonb_typeof(evidence_details) = 'object'
    ),

  calculated_at timestamptz
    not null default now(),

  created_at timestamptz
    not null default now(),

  constraint
    tmua_prediction_snapshots_score_bounds_chk
    check (
      (
        predicted_tmua_score9 is null
        or predicted_tmua_score9 between 1 and 9
      )
      and
      (
        lower_bound is null
        or lower_bound between 1 and 9
      )
      and
      (
        upper_bound is null
        or upper_bound between 1 and 9
      )
      and
      (
        test_signal_score9 is null
        or test_signal_score9 between 1 and 9
      )
      and
      (
        qb_signal_score9 is null
        or qb_signal_score9 between 2.5 and 8.5
      )
    ),

  constraint
    tmua_prediction_snapshots_status_consistency_chk
    check (
      (
        prediction_status = 'predicted'
        and predicted_tmua_score9 is not null
        and lower_bound is not null
        and upper_bound is not null
        and confidence is not null
        and lower_bound <= predicted_tmua_score9
        and predicted_tmua_score9 <= upper_bound
        and (
          (
            test_signal_score9 is not null
            and test_weight > 0
          )
          or
          (
            qb_signal_score9 is not null
            and qb_weight > 0
          )
        )
      )
      or
      (
        prediction_status = 'insufficient_evidence'
        and predicted_tmua_score9 is null
        and lower_bound is null
        and upper_bound is null
        and confidence is null
        and test_signal_score9 is null
        and test_weight = 0
        and qb_signal_score9 is null
        and qb_weight = 0
      )
    ),

  constraint
    tmua_prediction_snapshots_test_signal_consistency_chk
    check (
      (
        test_signal_score9 is null
        and test_weight = 0
        and test_evidence_count = 0
        and independent_test_count = 0
        and combined_full_count = 0
      )
      or
      (
        test_signal_score9 is not null
        and test_weight > 0
        and test_evidence_count > 0
        and independent_test_count > 0
        and independent_test_count <= test_evidence_count
        and combined_full_count <= independent_test_count
      )
    ),

  constraint
    tmua_prediction_snapshots_qb_signal_consistency_chk
    check (
      (
        qb_unique_questions < 30
        and qb_signal_score9 is null
        and qb_weight = 0
      )
      or
      (
        qb_unique_questions >= 30
        and qb_signal_score9 is not null
        and qb_weight > 0
      )
    ),

  constraint
    tmua_prediction_snapshots_user_model_input_key
    unique (
      user_id,
      model_version,
      input_hash
    )
);

create index
  tmua_prediction_snapshots_user_calculated_idx
on public.tmua_prediction_snapshots (
  user_id,
  calculated_at desc
);

create index
  tmua_prediction_snapshots_model_calculated_idx
on public.tmua_prediction_snapshots (
  model_version,
  calculated_at desc
);

alter table
  public.tmua_prediction_snapshots
enable row level security;

create policy
  tmua_prediction_snapshots_select_own
on public.tmua_prediction_snapshots
for select
to authenticated
using (
  auth.uid() = user_id
);

revoke all
on table public.tmua_prediction_snapshots
from anon;

revoke all
on table public.tmua_prediction_snapshots
from authenticated;

revoke all
on table public.tmua_prediction_snapshots
from service_role;

grant select
on table public.tmua_prediction_snapshots
to authenticated;

grant select, insert
on table public.tmua_prediction_snapshots
to service_role;

comment on table
  public.tmua_prediction_snapshots
is
  'Append-only server-owned TMUA Predictor snapshots. Students may read only their own rows.';

comment on column
  public.tmua_prediction_snapshots.prediction_status
is
  'predicted or insufficient_evidence; insufficient evidence never receives a synthetic TMUA score.';

comment on column
  public.tmua_prediction_snapshots.input_hash
is
  'Deterministic hash of model version, trusted evidence, conversion-set provenance and active-topic provenance.';

comment on column
  public.tmua_prediction_snapshots.evidence_details
is
  'Server-generated diagnostic provenance. It is not authoritative raw evidence.';