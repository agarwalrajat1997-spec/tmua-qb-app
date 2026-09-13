alter table public.qb_progress
  add column if not exists answer_submitted_at timestamptz,
  add column if not exists answer_elapsed_seconds integer,
  add column if not exists submission_id text;

alter table public.tmua_qb_attempt_events
  add column if not exists status text,
  add column if not exists difficulty integer,
  add column if not exists response_seconds integer,
  add column if not exists attempt_number integer,
  add column if not exists predictor_eligible boolean not null default true,
  add column if not exists exclusion_reason text,
  add column if not exists source_progress_id uuid,
  add column if not exists submission_id text;

-- A normal UNIQUE index permits multiple NULL values and gives
-- ON CONFLICT a deterministic unique target.
drop index if exists
  public.tmua_qb_attempt_events_client_event_id_uidx;

create unique index
  tmua_qb_attempt_events_client_event_id_uidx
on public.tmua_qb_attempt_events(client_event_id);

create index if not exists
  tmua_qb_attempt_events_user_question_attempt_idx
on public.tmua_qb_attempt_events(
  user_id,
  question_id,
  attempt_number
);

create index if not exists
  tmua_qb_attempt_events_predictor_eligible_idx
on public.tmua_qb_attempt_events(
  user_id,
  predictor_eligible,
  attempted_at desc
);

create or replace function
  public.capture_tmua_predictor_attempt_event()
returns trigger
language plpgsql
security definer
set search_path to ''
as $function$
declare
  v_question record;
  v_status text;
  v_is_correct boolean;
  v_response_seconds integer;
  v_attempt_number integer;
  v_predictor_eligible boolean;
  v_exclusion_reason text;
begin
  if NEW.product is distinct from 'tmua-question-bank' then
    return NEW;
  end if;

  if NEW.submission_id is null
     or btrim(NEW.submission_id) = ''
  then
    return NEW;
  end if;

  -- A retried database request carrying the same submission ID
  -- must not become a second attempt.
  if TG_OP = 'UPDATE'
     and NEW.submission_id is not distinct from OLD.submission_id
  then
    return NEW;
  end if;

  v_status := lower(btrim(coalesce(NEW.status, '')));

  if v_status not in (
    'correct',
    'right',
    'wrong',
    'incorrect'
  ) then
    return NEW;
  end if;

  if NEW.selected_answer is null
     or btrim(NEW.selected_answer) = ''
  then
    return NEW;
  end if;

  select
    q.qid,
    q.display_order,
    q.topic,
    q.difficulty,
    q.answer
  into v_question
  from public.tmua_qb_questions q
  where q.is_active = true
    and (
      q.qid = NEW.question_id
      or
      q.display_order =
        case
          when btrim(NEW.question_id) ~ '^[0-9]+$'
            then btrim(NEW.question_id)::integer
          else null
        end
    )
  order by
    case
      when q.qid = NEW.question_id then 0
      else 1
    end
  limit 1;

  if not found then
    return NEW;
  end if;

  -- Correctness is calculated from the canonical answer in the
  -- database rather than trusting a browser-provided boolean.
  v_is_correct :=
    upper(btrim(NEW.selected_answer)) =
    upper(btrim(v_question.answer));

  v_response_seconds :=
    case
      when NEW.answer_elapsed_seconds is null then null
      else greatest(0, NEW.answer_elapsed_seconds)
    end;

  -- Explicit rule: question-bank answers below ten seconds do not
  -- affect the predicted score.
  v_predictor_eligible :=
    v_response_seconds is not null
    and v_response_seconds >= 10;

  v_exclusion_reason :=
    case
      when v_response_seconds is null
        then 'missing_response_time'
      when v_response_seconds < 10
        then 'under_10_seconds'
      else null
    end;

  select
    coalesce(max(e.attempt_number), 0) + 1
  into v_attempt_number
  from public.tmua_qb_attempt_events e
  where e.user_id = NEW.user_id
    and e.question_id = NEW.question_id;

  insert into public.tmua_qb_attempt_events (
    user_id,
    email,
    product,
    question_id,
    topic_id,
    selected_answer,
    is_correct,
    attempted_at,
    source,
    client_event_id,
    history_quality,
    metadata,
    status,
    difficulty,
    response_seconds,
    attempt_number,
    predictor_eligible,
    exclusion_reason,
    source_progress_id,
    submission_id
  )
  values (
    NEW.user_id,
    lower(NEW.email),
    'tmua-question-bank',
    NEW.question_id,
    v_question.topic,
    NEW.selected_answer,
    v_is_correct,
    coalesce(
      NEW.answer_submitted_at,
      NEW.updated_at,
      now()
    ),
    'qb-progress-trigger-v2',
    'qb-progress|' ||
      NEW.user_id::text ||
      '|' ||
      NEW.submission_id,
    'observed',
    jsonb_build_object(
      'capture_version', '20260807-2',
      'canonical_qid', v_question.qid,
      'display_order', v_question.display_order,
      'saved_status', v_status
    ),
    v_status,
    v_question.difficulty,
    v_response_seconds,
    v_attempt_number,
    v_predictor_eligible,
    v_exclusion_reason,
    NEW.id,
    NEW.submission_id
  )
  on conflict (client_event_id) do nothing;

  return NEW;
end;
$function$;

drop trigger if exists
  trg_capture_tmua_predictor_attempt
on public.qb_progress;

create trigger
  trg_capture_tmua_predictor_attempt
after insert or update of submission_id
on public.qb_progress
for each row
execute function
  public.capture_tmua_predictor_attempt_event();

comment on function
  public.capture_tmua_predictor_attempt_event()
is
  'Captures authenticated TMUA question-bank Check Answer submissions. Responses below ten seconds are retained for audit but excluded from prediction evidence.';