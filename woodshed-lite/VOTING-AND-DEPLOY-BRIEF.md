# Woodshed Lite — Live Voting + Cloudflare Deploy Brief

**For:** Claude Code
**Owner:** Chris
**Goal:** Turn the static vote board into a real Supabase-backed voting feature, then ship the site to **woodshed-music.com** (already owned, DNS on Cloudflare).

**Target stack (direction — see `docs/STACK-AND-SEQUENCING.md`):** Astro + Supabase (Auth/Postgres/storage) + Stripe + Cloudflare Pages. **Right now we are only at M0** (static demo + list + votes). No Astro, no login, no billing in this task. **But Supabase is the through-line** — the votes backend here is brick #1 of the real backend, so design the schema **Auth-ready** (see A1). Astro migration is a Phase-1 shell decision and must NOT block this launch.

---

## Context (read first)

- Woodshed Lite is a **static single-page** demo. Source of truth: `woodshed-lite/src/shell.html` (structure+CSS), `src/mount.js` (interactive JS), `lite.config.js` (config/allowlist), `content.json` (copy, symlinked into dist). Build with `woodshed-lite/build-lite.sh` → `woodshed-lite/dist/`.
- **Waitlist email** already works via a hosted MailerLite embed (leave it alone).
- **Vote board** is currently fake: `#wsl-votes-slot` in `shell.html` has 4 hardcoded `.vote` rows with static counts and bar widths. `lite.config.js` → `funnel.votes` is stubbed as `provider: 'canny'` with `embedId: 'TODO'`. We are replacing this with Supabase, not Canny.
- The 4 options today: **More tunes**, **Build-your-own session**, **Loop a section**, **Mobile app** (see `content.json` → `ask.vote_*` and `shell.html`).
- **No git remote** on this repo → deploy is **direct Wrangler upload of `dist/`**, not Git-connected Pages.
- **Known build gotcha:** `build-lite.sh` step 6 runs `publish.sh`→`ci_check.py` as a hard stop, and it currently **FAILS on ~4 pre-existing main-app Real Book page-coverage gaps** that are unrelated to Lite. Lite's own safety check (`woodshed-lite/verify_public_safe.py`) passes. You'll need to handle this (see Workstream B, step 0).

---

## Workstream 0 — GitHub repo + hygiene (DO THIS FIRST)

Chris created a **private** GitHub repo and wants the project versioned properly for ongoing development (this is the public *alpha*). The Trumpet folder is ~2.6 GB — almost all of it is production masters and copyrighted material that must **not** enter git history.

**Critical ordering — do not `git add` anything until the ignore rules are in place**, or copyrighted PDFs / secrets can end up in history even if deleted later.

**Repo boundary = the web app only (~60 MB), not the 2.6 GB folder.** Keep the folder layout as-is (woodshed-lite builds from the parent engine/charts via relative paths — do NOT copy files into a new folder; that would fork the engine). The `.gitignore` defines what's tracked.

1. `.gitignore` and `.gitattributes` already exist at the Trumpet root. Review them first. They TRACK: `index.html` (engine), `charts/`, `vendor/`, `woodshed-lite/` source, `assets/` (incl. runtime drum mp3s via **Git LFS**), `docs/`, and the small build/gate scripts. They EXCLUDE:
   - `reference/` — **copyrighted** (Real Book.pdf, Technical Studies.pdf, etc.). Never commit.
   - `pipelines/` — the media-production workspace (reels, drum processing, score engine; ~2.3 GB of raw `.mov`/`.aif` + venvs). Separate concern; keep local or give it its own repo later.
   - `public-assets/pages/` — 72 MB of regenerable page renders (the small gate scripts + `page-manifest.json` stay tracked).
   - `woodshed-lite/dist/` — build output (regenerable), plus secrets/venvs/node_modules/OS junk and `*.mov/*.aif/*.wav/*.onnx` anywhere.
   - Runtime audio `assets/drums/trim/*.mp3` is kept via **Git LFS** (see `.gitattributes`), not ignored.
2. `git init` at the Trumpet root (it is NOT currently a git repo). `git lfs install` (git-lfs required — verify it's present; ~41 MB of drum mp3s will be LFS-tracked).
3. **Verify before first commit:** `git status --ignored` must show `reference/`, `pipelines/reels/archive/`, `pipelines/drum-source/`, and `woodshed-lite/dist/` as ignored, and must NOT stage any `.pdf`, `.mov`, `.aif`, or secret. Sanity-check `git ls-files | grep -iE 'reference/|\.pdf$|\.mov$|\.aif$'` returns nothing.
4. First commit, add the remote Chris created, push to `main`. Confirm the repo is **Private** on GitHub before pushing.
5. Deployment stays **decoupled** from GitHub for now (Wrangler direct upload — Workstream B). Git-connected Cloudflare Pages auto-deploy is a later upgrade, once the build is CI-friendly (41 MB audio + the gate). Note this in `README.md`.

**Chris does:** create the repo (done), confirm it's Private, run `gh auth login` (or supply a token) so the push can happen.
**Claude Code does:** review ignore rules, `git init` + `git lfs install`, verify nothing sensitive is staged, commit, add remote, push.

---

## Workstream A — Supabase-backed voting

### A1. Data model (generate SQL as a migration for Chris to run in the Supabase SQL editor)
**Design Auth-ready from day one** — this is brick #1 of the real backend (`docs/STACK-AND-SEQUENCING.md`). Use the `public` schema, snake_case, `created_at timestamptz`, and leave a clean seam for future `auth.users`.
- `vote_options(id text primary key, label text, meta text, sort int)` — seed the 4 current options.
- `votes(id uuid default gen_random_uuid() primary key, option_id text references vote_options(id), voter_hash text, user_id uuid references auth.users(id), created_at timestamptz default now())`.
  - **Now:** anonymous voters identified by `voter_hash` (random UUID in localStorage); `user_id` stays null.
  - **Later (post-M3):** logged-in votes set `user_id`; the anon `voter_hash` seam remains for logged-out visitors. Don't build auth now — just don't preclude it.
- Dedupe: `unique(option_id, voter_hash)` so a browser can upvote **several** features but each **once** (recommended "multi-select" model — confirm with Chris). Add a partial `unique(option_id, user_id) where user_id is not null` so the same dedupe holds once accounts exist.
- Expose logic through **`security definer` RPCs**, keep tables locked under RLS (no direct anon table access):
  - `get_vote_tallies()` → returns `option_id, label, meta, sort, count` (left join so zero-count options still appear).
  - `cast_vote(p_option_id text, p_voter_hash text)` → inserts (idempotent via the unique constraint / `on conflict do nothing`), returns the refreshed tallies. Optionally also record `inet_client_addr()` as a second dedupe signal.
- RLS: enable on both tables; grant `execute` on the two RPCs to `anon`; grant nothing else to `anon`.

### A2. Client wiring
- Add `SUPABASE_URL` + `SUPABASE_ANON_KEY` to `lite.config.js` under `funnel.votes` (set `provider: 'supabase'`). **The anon key is public-safe** — it's designed to ship in the browser and is protected by RLS. **Never** put the `service_role` key anywhere in the static site.
- Load `@supabase/supabase-js` (CDN/esm build, same async-safe pattern as the existing abcjs/soundfont loads in `shell.html`).
- New `src/votes.js` (or a section in `mount.js`) that:
  - On load: call `get_vote_tallies()`, render into the existing `.vote` markup — real counts, `.vbar` widths proportional to the max, sort desc, `.lead` class on the top row. Preserve the current visual design exactly.
  - Per-browser identity: random UUID in `localStorage['woodshed_voter']`.
  - On `.vote` click: call `cast_vote(...)`, optimistically bump the row, re-sort, mark that option voted (disable re-click, persist voted set in localStorage), animate.
  - Graceful failure: if Supabase is unreachable, fall back to the static seed counts so the board never looks broken.
- Keep it dependency-light and framed by the existing tokens/CSS.

### A3. Anti-abuse (confirm scope with Chris)
- MVP: localStorage voter hash + unique constraint. Trivially bypassable but fine for low-stakes feature voting.
- Optional hardening (only if Chris wants it now): **Cloudflare Turnstile** in front of `cast_vote`. Recommend shipping without it and adding later if spammed.

### A4. Acceptance criteria
- Votes persist across reloads and across browsers (real backend, not localStorage-only).
- A browser can't inflate a single option's count by spamming clicks.
- Board renders correct live tallies on first paint; degrades gracefully offline.
- No secrets beyond the anon key in the shipped bundle; `verify_public_safe.py` still passes.

---

## Workstream B — Ship to woodshed-music.com (Cloudflare Pages, Wrangler)

### B0. Unblock the build
- `build-lite.sh` won't complete because of the pre-existing, unrelated `ci_check.py` coverage failure. Choose one and note it in a commit:
  - **Preferred:** scope the Lite build's gate to Lite-only safety (`verify_public_safe.py`) and make the main-app coverage check non-blocking / a warning for this target; **or**
  - add a `--deploy-existing` path that skips re-running the failing gate and ships the already-assembled `dist/` (the `dist/` in the repo is current and correct).
- Do **not** weaken `verify_public_safe.py` — that's the real copyright gate for the public bundle.

### B1. Deploy
- Direct upload (no git remote): `npx wrangler pages deploy woodshed-lite/dist --project-name woodshed-lite --commit-dirty=true`.
- Auth via `wrangler login` (interactive, Chris) **or** `CLOUDFLARE_API_TOKEN` env with a token scoped to **Pages:Edit** (Chris creates it).
- `dist/` is ~42MB (41MB drum audio); within Pages limits (25MB/file, 20k files) — fine.

### B2. Custom domain
- In the Pages project, add custom domains **woodshed-music.com** and **www.woodshed-music.com**. Because the domain's DNS is already on Cloudflare, records auto-provision (CNAME → `<project>.pages.dev`) and SSL issues automatically.
- **Chris must do / confirm the domain attach and any DNS record** — Claude Code should not modify DNS or account settings autonomously; it can generate the exact records/steps.

### B3. Acceptance criteria
- `https://woodshed-music.com` serves the site over HTTPS; `www` redirects/works; assets (engine.js, drum mp3s, abcjs CDN) load; audio plays; voting works against Supabase from the live domain.
- A repeatable one-command redeploy is documented in `woodshed-lite/README.md`.

---

## Secrets & guardrails
- Public-safe (OK in the bundle): `SUPABASE_URL`, `SUPABASE_ANON_KEY`.
- **Never** in the bundle, committed, or in git history: Supabase `service_role` key, DB password, `CLOUDFLARE_API_TOKEN`. These are covered by `.gitignore`, but double-check they never get committed.
- `reference/` (copyrighted PDFs) must never be committed or deployed — see Workstream 0.
- Chris runs the SQL migration and creates accounts/tokens; Claude Code produces the SQL, client code, and exact dashboard/CLI steps.

## Suggested order
Workstream 0 (repo hygiene + push) → A (voting) → B (deploy). Get the repo clean and pushed first so all subsequent work is versioned.

---

## Open decisions (Claude Code should confirm before building)
1. **Vote model:** multi-select (one vote per option per browser) — recommended — vs single-select (one vote total).
2. **Turnstile now, or later?** Recommend later.
3. **Final option list/labels** — keep the current 4, or edit?
