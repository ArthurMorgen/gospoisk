-- Выполнить в Supabase SQL Editor (Dashboard → SQL Editor → New query)

create table if not exists saved_searches (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) on delete cascade not null,
  keywords text[] not null,
  platforms text[] default '{"portal","eis"}',
  name text,
  created_at timestamptz default now(),
  last_run_at timestamptz
);

-- RLS: каждый видит только свои поиски
alter table saved_searches enable row level security;

create policy "Users can view own searches"
  on saved_searches for select
  using (auth.uid() = user_id);

create policy "Users can insert own searches"
  on saved_searches for insert
  with check (auth.uid() = user_id);

create policy "Users can delete own searches"
  on saved_searches for delete
  using (auth.uid() = user_id);

create policy "Users can update own searches"
  on saved_searches for update
  using (auth.uid() = user_id);
