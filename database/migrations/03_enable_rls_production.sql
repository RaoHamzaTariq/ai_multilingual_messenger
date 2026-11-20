-- Migration 03: Enable Row Level Security (RLS) for Production
-- Re-enables RLS and applies security policies per instructions/DATABASE_AND_API.md

alter table public.profiles enable row level security;
alter table public.friendships enable row level security;
alter table public.messages enable row level security;
alter table public.translations enable row level security;

-- Profiles Policies
create policy "Profiles are viewable by authenticated users"
  on public.profiles for select
  to authenticated
  using (true);

create policy "Users can insert their own profile"
  on public.profiles for insert
  to authenticated
  with check (auth.uid() = id);

create policy "Users can update their own profile"
  on public.profiles for update
  to authenticated
  using (auth.uid() = id);

-- Friendships Policies
create policy "Users can view their friendships"
  on public.friendships for select
  to authenticated
  using (auth.uid() = requester_id or auth.uid() = addressee_id);

create policy "Users can send friendship requests"
  on public.friendships for insert
  to authenticated
  with check (auth.uid() = requester_id);

create policy "Addressee can update friendship status"
  on public.friendships for update
  to authenticated
  using (auth.uid() = addressee_id);

-- Messages Policies
create policy "Users can read their own messages"
  on public.messages for select
  to authenticated
  using (auth.uid() = sender_id or auth.uid() = receiver_id);

create policy "Users can send messages to accepted friends"
  on public.messages for insert
  to authenticated
  with check (
    auth.uid() = sender_id and exists (
      select 1 from public.friendships
      where status = 'accepted'
        and (
          (requester_id = auth.uid() and addressee_id = receiver_id)
          or
          (requester_id = receiver_id and addressee_id = auth.uid())
        )
    )
  );

-- Translations Policies
create policy "Users can read translations for their messages"
  on public.translations for select
  to authenticated
  using (
    exists (
      select 1 from public.messages m
      where m.id = message_id
        and (m.sender_id = auth.uid() or m.receiver_id = auth.uid())
    )
  );
