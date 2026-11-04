-- Independent Physics mock history preserves the earlier bank-compiled series untouched.
create table public.ib_physics_challenge_attempts (
  id uuid primary key,
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  mock_id text not null check (mock_id ~ '^physics-hl-challenge-[abc]$' or mock_id ~ '^physics-sl-challenge-[ab]$'),
  paper text not null check (paper in ('1', '2')),
  student_name text not null default '' check (char_length(student_name) <= 100),
  answers jsonb not null check (jsonb_typeof(answers) = 'object' and octet_length(answers::text) <= 600000),
  elapsed_seconds integer not null check (elapsed_seconds >= 0 and elapsed_seconds <= case when mock_id like 'physics-sl-%' then 5400 when paper = '1' then 7200 else 9000 end),
  submitted_at timestamptz not null default now(),
  self_marks jsonb check (self_marks is null or jsonb_typeof(self_marks) = 'object'),
  marked_at timestamptz,
  constraint ib_physics_challenge_marking_pair check ((self_marks is null) = (marked_at is null))
);
create index ib_physics_challenge_attempts_user_history on public.ib_physics_challenge_attempts (user_id, mock_id, paper, submitted_at desc);
alter table public.ib_physics_challenge_attempts enable row level security;
revoke all on public.ib_physics_challenge_attempts from public, anon, authenticated;
grant select on public.ib_physics_challenge_attempts to authenticated;
grant insert (id, user_id, mock_id, paper, student_name, answers, elapsed_seconds) on public.ib_physics_challenge_attempts to authenticated;
grant update (self_marks, marked_at) on public.ib_physics_challenge_attempts to authenticated;
create policy ib_physics_challenge_read_own on public.ib_physics_challenge_attempts for select to authenticated using ((select auth.uid()) = user_id);
create policy ib_physics_challenge_submit_own on public.ib_physics_challenge_attempts for insert to authenticated with check ((select auth.uid()) = user_id);
create policy ib_physics_challenge_mark_own on public.ib_physics_challenge_attempts for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);

-- Column privileges preserve submitted responses even through the Data API.
-- A trigger also prevents changing a completed self-assessment or immutable fields.
create function public.guard_ib_physics_challenge_attempt()
returns trigger language plpgsql security invoker set search_path = pg_catalog, public as $$
declare point record;
begin
  if row(new.id, new.user_id, new.mock_id, new.paper, new.student_name, new.answers, new.elapsed_seconds, new.submitted_at)
     is distinct from row(old.id, old.user_id, old.mock_id, old.paper, old.student_name, old.answers, old.elapsed_seconds, old.submitted_at) then
    raise exception 'Submitted Physics responses are immutable' using errcode = '23514';
  end if;
  if old.self_marks is not null and row(new.self_marks, new.marked_at) is distinct from row(old.self_marks, old.marked_at) then
    raise exception 'Saved self-assessment is immutable' using errcode = '23514';
  end if;
  if new.self_marks is not null then
    for point in select value from jsonb_each(new.self_marks) loop
      if jsonb_typeof(point.value) <> 'number' then
        raise exception 'Self-assessment requires integer marks' using errcode = '23514';
      end if;
      if (point.value::text)::numeric < 0 or (point.value::text)::numeric > 10 or trunc((point.value::text)::numeric) <> (point.value::text)::numeric then
        raise exception 'Self-assessment marks are out of range' using errcode = '23514';
      end if;
    end loop;
  end if;
  return new;
end;
$$;
revoke all on function public.guard_ib_physics_challenge_attempt() from public, anon, authenticated;
create trigger guard_ib_physics_challenge_attempt_before_update before update on public.ib_physics_challenge_attempts for each row execute function public.guard_ib_physics_challenge_attempt();
