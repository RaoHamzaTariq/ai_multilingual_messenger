-- Migration 02: Disable Row Level Security (RLS) for Development
-- This permits unrestricted reads and writes during local dev testing

alter table public.profiles disable row level security;
alter table public.friendships disable row level security;
alter table public.messages disable row level security;
alter table public.translations disable row level security;
