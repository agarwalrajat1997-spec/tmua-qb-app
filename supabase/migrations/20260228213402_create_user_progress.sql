-- TMUA QB / Practice Sets: per-user progress synced across devices
-- Table: public.user_progress
-- Keys: (user_id, product, scope)
-- RLS: user can only read/write their own rows

create table if not exists public.user_progress (
  user_id uuid not null,
  product text not null,
  scope text not null default 'default',
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  primary key (user_id, product, scope)
);

-- Helpful index for queries (PK already covers, but ok if planner needs)
create index if not exists user_progress_user_product_idx
  on public.user_progress (user_id, product);

-- Enable RLS
alter table public.user_progress enable row level security;

-- Policies (create only if missing)
do $$
begin
  if not exists (
    select 1 from pg_policies
    where schemaname='public' and tablename='user_progress' and policyname='user_progress_select_own'
  ) then
    create policy user_progress_select_own
      on public.user_progress
      for select
      using (auth.uid() = user_id);
  end if;

  if not exists (
    select 1 from pg_policies
    where schemaname='public' and tablename='user_progress' and policyname='user_progress_insert_own'
  ) then
    create policy user_progress_insert_own
      on public.user_progress
      for insert
      with check (auth.uid() = user_id);
  end if;

  if not exists (
    select 1 from pg_policies
    where schemaname='public' and tablename='user_progress' and policyname='user_progress_update_own'
  ) then
    create policy user_progress_update_own
      on public.user_progress
      for update
      using (auth.uid() = user_id)
      with check (auth.uid() = user_id);
  end if;
end $$;

-- Optional: keep updated_at fresh
create or replace function public.touch_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_user_progress_touch on public.user_progress;
create trigger trg_user_progress_touch
before update on public.user_progress
for each row execute function public.touch_updated_at();