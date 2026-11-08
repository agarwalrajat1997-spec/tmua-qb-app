do $guard$ begin
  if md5(pg_get_functiondef('public.capture_tmua_predictor_attempt_event()'::regprocedure)) <> 'bacc5b755a75dd020ca9ba2181a1de81' then
    raise exception 'The scoring trigger has changed; review before installing';
  end if;
end $guard$;
alter table private.tmua_original_release_20261108 add column published_at timestamptz;
CREATE OR REPLACE FUNCTION public.capture_tmua_predictor_attempt_event()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO ''
AS $function$
declare
  v_question record;
  v_release record;
  v_content_version text;
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

  -- Old tabs and offline journals may submit a historical version after release.
  select payload, before_row, published_at into v_release
  from private.tmua_original_release_20261108 where qid = v_question.qid;
  if found then
    if split_part(NEW.submission_id, '|', 3) = ('version=' || (v_release.payload->>'content_version')) then
      v_question.answer := v_release.payload->>'answer';
      v_question.topic := v_release.payload->>'topic';
      v_question.difficulty := (v_release.payload->>'difficulty')::integer;
      v_content_version := v_release.payload->>'content_version';
    elsif NEW.submission_id like 'tmua-stable-v1|%' then
      v_question.answer := v_release.payload->>'previous_answer';
      v_question.topic := v_release.payload->>'previous_topic';
      v_question.difficulty := (v_release.payload->>'previous_difficulty')::integer;
      v_content_version := v_release.payload->>'previous_version';
    elsif v_release.published_at is not null and NEW.answer_submitted_at < v_release.published_at then
      v_question.answer := v_release.before_row->>'answer';
      v_question.topic := v_release.before_row->>'topic';
      v_question.difficulty := (v_release.before_row->>'difficulty')::integer;
      v_content_version := 'legacy-db-20261108';
    elsif v_release.published_at is not null then
      v_content_version := v_release.payload->>'content_version';
    end if;
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
    ) || jsonb_strip_nulls(jsonb_build_object('content_version', v_content_version)),
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
$function$
;
