-- ==============================================================================
-- AI Multilingual Messenger - Complete Database Schema & RLS Setup
-- Run this in your Supabase Project SQL Editor
-- ==============================================================================

-- 1. PROFILES TABLE
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  username text unique not null,
  display_name text,
  preferred_language text,
  created_at timestamptz default now()
);

alter table public.profiles enable row level security;

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

-- Trigger to automatically create a profile row upon sign up (bypasses RLS)
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, username, display_name, preferred_language)
  values (
    new.id,
    lower(coalesce(new.raw_user_meta_data->>'username', split_part(new.email, '@', 1))),
    coalesce(new.raw_user_meta_data->>'username', split_part(new.email, '@', 1)),
    null
  )
  on conflict (id) do nothing;
  return new;
end;
$$ language plpgsql security definer;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();


-- 2. FRIENDSHIPS TABLE
create table if not exists public.friendships (
  id uuid primary key default gen_random_uuid(),
  requester_id uuid not null references public.profiles(id) on delete cascade,
  addressee_id uuid not null references public.profiles(id) on delete cascade,
  status text not null check (status in ('pending', 'accepted', 'rejected')),
  created_at timestamptz default now(),
  constraint unique_friendship_pair unique (requester_id, addressee_id)
);

alter table public.friendships enable row level security;

-- Users can read rows where they are requester or addressee
create policy "Users can view their friendships"
  on public.friendships for select
  to authenticated
  using (auth.uid() = requester_id or auth.uid() = addressee_id);

-- Only requester can insert
create policy "Users can send friendship requests"
  on public.friendships for insert
  to authenticated
  with check (auth.uid() = requester_id);

-- Only addressee can update status (accept / reject)
create policy "Addressee can update friendship status"
  on public.friendships for update
  to authenticated
  using (auth.uid() = addressee_id);


-- 3. MESSAGES TABLE
create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  sender_id uuid not null references public.profiles(id) on delete cascade,
  receiver_id uuid not null references public.profiles(id) on delete cascade,
  type text not null check (type in ('text', 'image', 'voice')),
  content text,
  media_url text,
  duration_seconds int check (duration_seconds is null or duration_seconds <= 60),
  created_at timestamptz default now()
);

alter table public.messages enable row level security;

-- Users can read rows where they are sender or receiver
create policy "Users can read their own messages"
  on public.messages for select
  to authenticated
  using (auth.uid() = sender_id or auth.uid() = receiver_id);

-- Insert allowed only if sender = auth.uid() AND accepted friendship exists
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


-- 4. TRANSLATIONS TABLE (Caching Rule: Unique message_id, target_language)
create table if not exists public.translations (
  id uuid primary key default gen_random_uuid(),
  message_id uuid not null references public.messages(id) on delete cascade,
  target_language text not null,
  detected_language text,
  transcript text,
  translated_text text not null,
  created_at timestamptz default now(),
  constraint unique_message_target_lang unique (message_id, target_language)
);

alter table public.translations enable row level security;

-- Users can read translations for messages they participate in
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

-- Backend service role key handles inserting translations (bypasses RLS)


-- 5. STORAGE BUCKETS (chat-images and chat-voice)
insert into storage.buckets (id, name, public, file_size_limit)
values
  ('chat-images', 'chat-images', false, 1048576), -- 1 MB limit
  ('chat-voice', 'chat-voice', false, 10485760)   -- 10 MB limit (for max 60s voice audio)
on conflict (id) do nothing;

-- Storage RLS: only authenticated users who are part of the chat can upload/read
create policy "Authenticated users can upload chat images"
  on storage.objects for insert
  to authenticated
  with check (bucket_id = 'chat-images');

create policy "Users can view chat images"
  on storage.objects for select
  to authenticated
  using (bucket_id = 'chat-images');

create policy "Authenticated users can upload chat voice notes"
  on storage.objects for insert
  to authenticated
  with check (bucket_id = 'chat-voice');

create policy "Users can view chat voice notes"
  on storage.objects for select
  to authenticated
  using (bucket_id = 'chat-voice');
