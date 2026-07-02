# Woodshed Lite

The public, hosted demo of the Woodshed — the page that runs the validation funnel
(M0 → M3). One scroll: a hook, two live stations (Warmup + Jam), a funnel.

**Full spec:** [`../docs/woodshed-lite-spec.md`](../docs/woodshed-lite-spec.md)

---

## The one rule: no fork, no drift

Lite is **not** a copy of the Woodshed. It is a *thin landing shell* that mounts the
**same engine** the full app uses, plus a build step that bundles a PD-safe subset for
static hosting.

- The engine (band, comping, drums, metronome, chart rendering) has **one home**:
  the canonical `../index.html`. Lite mounts it — it never re-implements it.
- The musical content is a **filter, not a copy**: `lite.config.js` is an allowlist of
  tune/warmup IDs that already live in `../charts/`.
- You hand-maintain only the **marketing chrome** (hero/funnel copy) and the **~6-line
  config**. Everything musical flows from canonical on rebuild.
- Lite is a **build target, not a branch.** Change the Woodshed → re-run the build →
  redeploy. Never hand-edit the engine in two places.

If you ever find yourself copy-pasting engine code into this folder, stop — that's the
drift this whole design exists to prevent.

---

## Files

| File | Hand-maintained? | What it is |
|---|---|---|
| `index.html` | ✅ yes | Landing shell — hero, pitch, funnel, footer, station *slots*. Marketing chrome only. |
| `lite.config.js` | ✅ yes | Which tunes/warmup Lite shows + funnel embed IDs + copy knobs. |
| `src/landing.css` | ✅ yes | Marketing-chrome styles (inherits the Blue Note look). |
| `src/mount.js` | ✅ yes | Mounts the shared engine into the two station slots. |
| `src/votes.js` | ✅ yes | Live Supabase vote board (single-select, write-in, graceful fallback). |
| `supabase/migrations/0001_voting.sql` | ✅ yes | Voting schema + RLS + RPCs. Run once in the Supabase SQL editor. |
| `build-lite.sh` | rarely | Extract engine + assemble + run gates → `dist/`. |
| `dist/` | ❌ never | Build output. Regenerated every build. Disposable. Do not hand-edit. |

---

## Build & deploy

```sh
# from the Trumpet project root:
./woodshed-lite/build-lite.sh        # → woodshed-lite/dist/  (runs the gates)
```

The build:
1. Extracts the marked engine spans from `../index.html` → `dist/engine.js`
2. Copies the curated PD-safe charts + warmup data → `dist/`
3. Copies shared vendor libs + PD assets for the chosen tunes → `dist/`
4. Copies the real drum-loop audio (~41 MB) → `dist/assets/drums/trim/`
5. Assembles `dist/index.html` (shell + `lite.config.js` + `mount.js` + `votes.js`)
6. **Gates** (step 6) — two gates, different scopes, only one blocks Lite:
   - **`verify_public_safe.py` (HARD STOP):** Lite's copyright gate. Scans
     `lite.config.js`; any lead-sheet melody must be public-domain (year ≤ 1930).
     Never weaken this.
   - **`../publish.sh` → `ci_check.py` (ADVISORY):** the *main-app* Real Book
     page-coverage gate. Unrelated to the Lite bundle; its pre-existing coverage
     warning is printed but does **not** block a Lite deploy.

Then deploy `dist/` to **Cloudflare Pages** (see below). The gates certify the
bundle; they never publish. Deploy stays a manual, decoupled step.

---

## Live voting (Supabase)

The vote board (`#wsl-votes-slot`) is backed by Supabase — real tallies that
persist across reloads and browsers. It is **brick #1 of the real backend**
(see [`../docs/STACK-AND-SEQUENCING.md`](../docs/STACK-AND-SEQUENCING.md)),
designed Auth-ready from day one.

**Model:** single-select — one vote per browser total; clicking a different
option *moves* your vote. Anti-abuse is a localStorage voter hash + a DB unique
constraint (spamming clicks can't inflate a count). Option **"Something else"**
captures a free-text write-in (stored server-side in `votes.note`).

**One-time setup (Chris):**
1. Create a Supabase project. In **Project Settings → API**, copy the
   **Project URL** and the **anon public** key.
2. Paste them into `lite.config.js` → `funnel.votes.supabaseUrl` /
   `supabaseAnonKey`. *(The anon key is public-safe — it's built to ship in the
   browser and is protected by RLS. **Never** put the `service_role` key or DB
   password here.)*
3. In the **Supabase SQL editor**, run
   [`supabase/migrations/0001_voting.sql`](supabase/migrations/0001_voting.sql)
   once. It creates the RLS-locked `vote_options` / `votes` tables and the two
   security-definer RPCs (`get_vote_tallies`, `cast_vote`), and seeds the 4
   options. Safe to re-run (won't wipe votes).
4. Rebuild (`./build-lite.sh`) and redeploy.

Until the keys are set the board **degrades gracefully** to the static seed
counts — it never looks broken.

**Read the "Something else" write-ins** (run in the SQL editor as owner):
```sql
select note, created_at from public.votes
where option_id = 'other' and note is not null
order by created_at desc;
```

---

## Deploy to woodshed-music.com (Cloudflare Pages)

Deploy is **decoupled from GitHub** — direct Wrangler upload of `dist/`
(GitHub is version control, not the deploy pipeline). Git-connected Pages
auto-deploy is a later upgrade, once the build is CI-friendly.

**One-command redeploy** (from the project root, after `./woodshed-lite/build-lite.sh`):
```sh
npx wrangler pages deploy woodshed-lite/dist --project-name woodshed-lite --commit-dirty=true
```
- Auth: `wrangler login` (interactive) **or** `CLOUDFLARE_API_TOKEN` scoped to
  **Pages:Edit**. The first deploy creates the `woodshed-lite` Pages project.
- `dist/` is ~42 MB (41 MB drum audio) — within Pages limits (25 MB/file, 20k files).

**Custom domain (Chris does this in the dashboard — one time):**
1. Cloudflare dashboard → **Workers & Pages → woodshed-lite → Custom domains**.
2. Add **`woodshed-music.com`** and **`www.woodshed-music.com`**. Because the
   domain's DNS is already on Cloudflare, records auto-provision
   (CNAME → `woodshed-lite.pages.dev`) and SSL issues automatically.
3. Verify `https://woodshed-music.com` serves over HTTPS and `www` works.

*(Claude Code does not modify DNS or account settings autonomously — it produces
the exact steps; you confirm the attach.)*

---

## Before the first real build — two Day-1 spikes

Both are flagged in the spec §3 and §8. Resolve them before building anything else:

1. **Engine boots without app state.** Confirm the extracted engine renders a chart +
   moving playhead and plays the band when handed a bare `{abc, bars, bpm, style}` —
   no `S`, no `todaysPicks`, no curriculum. The chart renderer is the risk.
2. **Audio works statically.** Confirm the band plays from `dist/` served by a dumb
   static server with `woodshed_server.py` **off**. The audio is client-side, so it
   should — but verify, don't assume.

These are the single biggest technical risks in the plan. One session resolves both.

---

## Status

**M0 — live voting + deploy wiring (Jul 2, 2026).** Supabase voting is built
(schema migration + `src/votes.js` client, single-select, write-in, graceful
fallback). Build gates are scoped (Lite copyright = hard, main-app coverage =
advisory). Repo is versioned at `github.com/chrisrl112/woodshed`.

**Remaining for a live launch (Chris):**
1. Create the Supabase project; paste URL + anon key into `lite.config.js`; run
   `supabase/migrations/0001_voting.sql`.
2. `./woodshed-lite/build-lite.sh` then the Wrangler deploy command above.
3. Attach `woodshed-music.com` in the Pages dashboard.
