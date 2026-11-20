# Database & Migrations

This folder contains all SQL migrations and database schema files for the **AI Multilingual Messenger** project.

## Folder Structure

```
database/
├── schema.sql                         # Full consolidated database schema
├── migrations/
│   ├── 01_initial_schema.sql          # Tables (profiles, friendships, messages, translations), trigger, and storage buckets
│   ├── 02_disable_rls_dev.sql         # Disables RLS for development testing
│   └── 03_enable_rls_production.sql   # Complete Row Level Security policies for production
└── README.md
```

## How to Apply Migrations

### In Supabase Dashboard (SQL Editor)
1. Open your [Supabase Dashboard](https://supabase.com/dashboard).
2. Go to **SQL Editor**.
3. Run `migrations/01_initial_schema.sql` to create all tables, auto-profile trigger, and storage buckets.
4. For local development: run `migrations/02_disable_rls_dev.sql`.
5. For production release: run `migrations/03_enable_rls_production.sql`.
