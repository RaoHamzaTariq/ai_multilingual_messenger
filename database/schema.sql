-- Consolidated Database Schema for AI Multilingual Messenger
-- Combines initial tables, trigger, and storage setup

-- 1. Profiles Table
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  username text unique not null,
  display_name text,
  preferred_language text,
  created_at timestamptz default now()
);

-- Trigger to auto-create profile on sign up
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

-- 2. Friendships Table
create table if not exists public.friendships (
  id uuid primary key default gen_random_uuid(),
  requester_id uuid not null references public.profiles(id) on delete cascade,
  addressee_id uuid not null references public.profiles(id) on delete cascade,
  status text not null check (status in ('pending', 'accepted', 'rejected')),
  created_at timestamptz default now(),
  constraint unique_friendship_pair unique (requester_id, addressee_id)
);

-- 3. Messages Table
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

-- 4. Translations Table (Caching: unique on message_id and target_language)
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

-- 5. Storage Buckets
insert into storage.buckets (id, name, public, file_size_limit)
values
  ('chat-images', 'chat-images', false, 1048576), -- 1 MB limit
  ('chat-voice', 'chat-voice', false, 10485760)   -- 10 MB limit (max 60s voice audio)
on conflict (id) do nothing;
