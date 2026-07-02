-- ============================================================================
-- Woodshed — Voting backend (M0)  ·  migration 0001
-- ----------------------------------------------------------------------------
-- Run this whole file ONCE in the Supabase SQL editor (as the project owner).
-- It is idempotent-ish: safe to re-run (drops/recreates functions, `if not
-- exists` on tables). Re-running will NOT wipe existing votes.
--
-- Design (see docs/STACK-AND-SEQUENCING.md — "the through-line is Supabase"):
--   * public schema, snake_case, created_at timestamptz.
--   * AUTH-READY from day one: votes.user_id -> auth.users(id) (nullable now),
--     anon voters identified by voter_hash. No auth is built yet; we just don't
--     preclude it. When accounts arrive post-M3, cast_vote already branches on
--     auth.uid() and the same RPCs keep working.
--   * SINGLE-SELECT model (Chris's call): one vote per browser TOTAL, not one
--     per option. Casting for a different option MOVES your vote (upsert).
--   * Tables are locked under RLS with NO anon policies. All access is through
--     two security-definer RPCs. anon can execute the RPCs and nothing else.
--   * Option "other" carries a free-text write-in (votes.note). Notes are
--     server-side only — never returned by the anon RPCs. Read them yourself
--     with the admin query at the bottom of this file.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. Tables
-- ---------------------------------------------------------------------------
create table if not exists public.vote_options (
  id    text primary key,
  label text not null,
  meta  text,
  sort  int  not null default 0
);

create table if not exists public.votes (
  id         uuid primary key default gen_random_uuid(),
  option_id  text not null references public.vote_options(id),
  voter_hash text,                                        -- anon identity (localStorage UUID)
  user_id    uuid references auth.users(id),              -- auth-ready seam (null until login exists)
  note       text,                                        -- free-text write-in for the "other" option
  ip         inet,                                        -- optional secondary dedupe signal (not enforced)
  created_at timestamptz not null default now(),
  -- exactly one identity per row (guards against malformed inserts)
  constraint votes_identity_ck check (voter_hash is not null or user_id is not null)
);

-- SINGLE-SELECT dedupe: one live vote per browser, and (later) one per account.
-- Partial unique indexes so the null side never collides. cast_vote's ON CONFLICT
-- targets exactly these predicates.
create unique index if not exists votes_voter_hash_key
  on public.votes (voter_hash) where voter_hash is not null;
create unique index if not exists votes_user_id_key
  on public.votes (user_id) where user_id is not null;

create index if not exists votes_option_id_idx on public.votes (option_id);

-- ---------------------------------------------------------------------------
-- 2. Seed the options (edit labels/meta here or via content.json for display).
--    ON CONFLICT keeps counts intact on re-run; it refreshes label/meta/sort.
-- ---------------------------------------------------------------------------
insert into public.vote_options (id, label, meta, sort) values
  ('full_warmup',    'Full warmup',                   'Long tones, lip slurs, flexibility — the whole routine', 1),
  ('byo_session',    'Build your own session',        'Stack your routine + upload the PDFs you''re practicing', 2),
  ('track_progress', 'Track your progress over time', 'Streaks, logs, watch your reps add up',                  3),
  ('other',          'Something else',                'Tell me what to build — type it in',                     4)
on conflict (id) do update
  set label = excluded.label, meta = excluded.meta, sort = excluded.sort;

-- ---------------------------------------------------------------------------
-- 3. Row-level security: lock the tables, expose nothing to anon directly.
--    (Tables are NOT force-RLS, so the security-definer functions below — owned
--    by the postgres role that owns these tables — bypass RLS as intended.)
-- ---------------------------------------------------------------------------
alter table public.vote_options enable row level security;
alter table public.votes        enable row level security;
-- No policies are created on purpose: anon/authenticated get zero direct access.

-- ---------------------------------------------------------------------------
-- 4. RPCs (security definer). search_path is pinned to defeat hijacking.
-- ---------------------------------------------------------------------------

-- get_vote_tallies() — every option with its live count (left join so zero-count
-- options still show). Ordered by sort for stable board layout; the client
-- re-sorts by count for display.
create or replace function public.get_vote_tallies()
returns table (option_id text, label text, meta text, sort int, count bigint)
language sql
security definer
set search_path = public, pg_temp
stable
as $$
  select o.id, o.label, o.meta, o.sort, count(v.id) as count
  from public.vote_options o
  left join public.votes v on v.option_id = o.id
  group by o.id, o.label, o.meta, o.sort
  order by o.sort;
$$;

-- cast_vote(p_option_id, p_voter_hash, p_note) — single-select upsert.
--   * Validates the option exists (clean error instead of a raw FK violation).
--   * If a logged-in caller exists (auth.uid()), dedupes on user_id; otherwise
--     dedupes on voter_hash. Either way a repeat cast MOVES the vote.
--   * p_note is only stored for option 'other' (ignored elsewhere).
--   * Returns the refreshed tallies so the client repaints in one round-trip.
create or replace function public.cast_vote(
  p_option_id  text,
  p_voter_hash text default null,
  p_note       text default null
)
returns table (option_id text, label text, meta text, sort int, count bigint)
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
  v_uid  uuid := auth.uid();                       -- null for anon callers
  v_note text := case when p_option_id = 'other'
                      then nullif(btrim(p_note), '')
                      else null end;
begin
  if not exists (select 1 from public.vote_options where id = p_option_id) then
    raise exception 'unknown option_id: %', p_option_id using errcode = '22023';
  end if;

  if v_uid is not null then
    -- authed path (post-M3): identity = user_id
    insert into public.votes (option_id, user_id, note)
    values (p_option_id, v_uid, v_note)
    on conflict (user_id) where user_id is not null
    do update set option_id = excluded.option_id,
                  note       = excluded.note,
                  created_at = now();
  else
    -- anon path (now): identity = voter_hash
    if nullif(btrim(coalesce(p_voter_hash, '')), '') is null then
      raise exception 'voter_hash required for anonymous votes' using errcode = '22023';
    end if;
    insert into public.votes (option_id, voter_hash, note, ip)
    values (p_option_id, p_voter_hash, v_note, inet_client_addr())
    on conflict (voter_hash) where voter_hash is not null
    do update set option_id = excluded.option_id,
                  note       = excluded.note,
                  ip         = excluded.ip,
                  created_at = now();
  end if;

  return query select * from public.get_vote_tallies();
end;
$$;

-- ---------------------------------------------------------------------------
-- 5. Grants: anon (and future authenticated) may ONLY execute the two RPCs.
-- ---------------------------------------------------------------------------
revoke all on function public.get_vote_tallies()               from public;
revoke all on function public.cast_vote(text, text, text)      from public;
grant execute on function public.get_vote_tallies()            to anon, authenticated;
grant execute on function public.cast_vote(text, text, text)   to anon, authenticated;

-- ============================================================================
-- ADMIN — read the "Something else" write-ins (run as owner / service_role):
--
--   select v.note, v.created_at
--   from public.votes v
--   where v.option_id = 'other' and v.note is not null
--   order by v.created_at desc;
--
-- Full tally (same as the app sees):   select * from public.get_vote_tallies();
-- ============================================================================
