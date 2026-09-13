create index if not exists sat_question_reports_user_created_idx
  on public.sat_question_reports (user_id, created_at desc);
