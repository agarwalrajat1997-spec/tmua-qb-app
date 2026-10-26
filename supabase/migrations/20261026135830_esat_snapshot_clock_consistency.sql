create or replace function public.esat_save_module_predictions(p_user_id uuid, p_revision uuid, p_predictions jsonb,
  p_model_version text, p_evidence_at timestamptz) returns void
language plpgsql security invoker set search_path = '' as $$
declare
  plan public.esat_exam_plans%rowtype;
  snapshot_time timestamptz;
begin
  select * into plan from public.esat_exam_plans where user_id = p_user_id for update;
  if not found or plan.revision <> p_revision then raise exception 'Your exam details changed. Refresh your predictions.'; end if;
  snapshot_time := clock_timestamp();
  -- A slow request started before the cutoff must never overwrite the lock.
  if snapshot_time >= plan.lock_at then
    perform public.esat_lock_due_predictions(p_user_id);
    return;
  end if;
  if p_predictions is null or jsonb_typeof(p_predictions) <> 'array' or jsonb_array_length(p_predictions) <> 3
    or p_evidence_at is null or p_evidence_at >= plan.lock_at or p_evidence_at > snapshot_time
    or coalesce(p_model_version, '') = '' then raise exception 'Invalid module prediction snapshot.'; end if;
  if (select array_agg(value->>'module' order by ord) from jsonb_array_elements(p_predictions) with ordinality as item(value, ord)) is distinct from plan.modules then
    raise exception 'Prediction modules do not match the exam booking.';
  end if;
  -- Out-of-order requests cannot replace a more recent evidence snapshot.
  if plan.evidence_at is not null and p_evidence_at < plan.evidence_at then return; end if;
  update public.esat_exam_plans set predictions = p_predictions, prediction_saved_at = snapshot_time,
    evidence_at = p_evidence_at, model_version = p_model_version where user_id = p_user_id;
end;
$$;
