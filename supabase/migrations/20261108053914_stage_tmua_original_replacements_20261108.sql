create table private.tmua_original_release_20261108 (
  qid text primary key, payload jsonb not null, before_row jsonb,
  check (payload->>'qid' = qid)
);
alter table private.tmua_original_release_20261108 enable row level security;
revoke all on private.tmua_original_release_20261108 from public, anon, authenticated;
