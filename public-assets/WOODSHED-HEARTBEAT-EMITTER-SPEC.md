# Woodshed Heartbeat Emitter — Drop-in Build Spec (wood-47)

*Drop-in prep · 2026-06-25 · Owner: night-shift-woodshed · Board: wood-47 · Milestone M4 · Env: code-build (STAGE ONLY)*
*Depends on: **ph-5** (Supabase `heartbeats` table + RLS + §4 push contract on the hub side) — that table must exist before this emitter has anything to POST to.*
*Source grounding (real host artifacts, read 2026-06-25):*
- *Push contract: `Projects/Portfolio Hub/build-prep/SUPABASE-HEARTBEATS-SPEC.md` §4 (payload shape, upsert via `Prefer: resolution=merge-duplicates`, service_role key in `apikey` + `Authorization`).*
- *Sanctioned sibling pattern mirrored here: `Projects/Portfolio Hub/build-prep/GROWROOM-HEARTBEAT-EMITTER-SPEC.md` (the approved Growroom emitter drop-in).*
- *Woodshed manifest (slug + the 3 heartbeat metric keys): `public-assets/manifest.json`.*
- *The state file this emitter PIGGYBACKS ON: `public-assets/snapshot.json` (produced by `render_snapshot.py`, wood-43), its schema `snapshot.schema.json`, and the illustrative `snapshot.example.json`.*

> **Apply this in Claude Code / on Chris's host, not here.** The night shift cannot deploy, run external POSTs, or touch Supabase. This is the complete drop-in: the emitter script, its git-ignored config, a launchd job, and the apply note. It ships **after** the hub's Supabase `heartbeats` table (ph-5) exists.

---

## 1. What this is (and what it deliberately is NOT)

The hub built the **table + the site read** (ph-5). wood-47 wires the **Woodshed producer**: a push-only emitter on Chris's host that POSTs one upsert row to Supabase, flipping the Woodshed card on `chrisliquin.com` from "awaiting first report" to a live reporting dot with real metric values. This is the **heartbeat leg** of the hub's manifest + heartbeat + changelog ingestion contract; the **manifest (wood-48)** and **snapshot (wood-43)** already shipped.

**Design principle — piggyback, don't re-export.** The pipeline **already** produces the public state file `snapshot.json` via `render_snapshot.py` (wood-43). The emitter does **not** re-run the practice brain, re-export from the browser, or duplicate any projection logic. It **reads the file the proven pipeline already produces** and forwards a tiny heartbeat. This keeps the emitter ~100 lines, dependency-free, and impossible to break the snapshot pipeline with.

**Explicitly out of scope:** any change to `render_snapshot.py` / `snapshot.json` / `manifest.json` / `index.html` / `charts.js` (this drop is **additive only** — NEW files only); sending tunes / PRs / objectives detail (the heartbeat carries only the 3 manifest-declared metric keys); the hub site display (ph-5 already renders it); a Vercel rebuild trigger (optional, §7).

---

## 2. The contract it targets (from ph-5 §4 — do not change)

One upsert row, keyed on `project_slug = "the-woodshed"`:

```json
{
  "project_slug": "the-woodshed",
  "last_report":  "2026-06-13T08:40:00Z",
  "last_activity":"2026-06-13T08:40:00Z",
  "status": "live",
  "metric_values": { "streak_days": 6 },
  "note": "illustrative snapshot — not live data"
}
```

POST to `"$SUPABASE_URL/rest/v1/heartbeats"` with `Prefer: resolution=merge-duplicates` (upsert on the PK), using the **service_role** key in `apikey` + `Authorization: Bearer`. (Verbatim mechanics in SUPABASE-HEARTBEATS-SPEC.md §4.)

**Metric keys are fixed by the manifest** (`metrics[].key` where `source:"heartbeat"`): `streak_days`, `sessions_total`, `hours_total`. The site only renders keys the manifest declares — and the emitter emits **only the metric keys it has a real source for** (today: just `streak_days`; see §3).

---

## 3. Field derivation — where each value comes from (grounded, no invented numbers)

The emitter reads `snapshot.json` (`json.loads`) and derives:

| Heartbeat field | Source on host | Derivation | Confidence |
|---|---|---|---|
| `streak_days` | `snapshot.streak` (integer) | Pass through, cast `int`. Matches manifest "Current streak". **Always emitted.** | **high (REAL)** |
| `sessions_total` | **no real source field exists** — not in `snapshot.json`, not in the upstream brain (`mission-control.json` / `.example.json`) on disk | **OMITTED** from `metric_values`. The site renders an honest em-dash for an undeclared value. **Never backfilled with a literal.** | **[confirm:]** |
| `hours_total` | **no real source field exists** (same as above) | **OMITTED** from `metric_values`. | **[confirm:]** |
| `last_report` | `snapshot.source.exportedAt` (the brain's real last-export time), falling back to `snapshot.generatedAt` if `exportedAt` is null | The **file's own timestamp, NOT wall-clock `now()`** — see §4. Normalized to UTC ISO-8601 `Z`. | high |
| `last_activity` | same as `last_report` | The last real sign-of-life is the last export. | high |
| `status` | constant `"live"` | Informational only — the **badge authority stays with the manifest**, and the hub's staleness guard independently degrades a stale card. | high |
| `note` | `null`, **unless** `snapshot.source.illustrative` is `true` → `"illustrative snapshot — not live data"` | Keeps the public number honest about provenance so an illustrative figure is never misrepresented as live. | high |

### The headline open item — the `sessions_total` / `hours_total` source gap

This is the one judgment call in the whole drop, and it is a **manifest-vs-data mismatch, not an emitter bug**:

> The Woodshed manifest declares **three** heartbeat metric keys — `streak_days`, `sessions_total`, `hours_total` — but **only `streak_days` has a real source field** anywhere on disk. `snapshot.json` exposes `streak` (and week/tunes/PRs/objectives), but **no sessions count and no hours total**; the upstream brain (`mission-control.json` / `.example.json`) currently has only `streak` too. So today the card can honestly show one of its three numbers and an em-dash for the other two.

Two clean ways to close it (Chris/Code picks one):

- **(a) Add the data** — extend the brain export + `render_snapshot.py` to project a real `sessions` count and `hours` total into `snapshot.json`, then the emitter maps them straight through (one-line additions in `build_payload`). This is the better long-term answer if those numbers exist in the app's state.
- **(b) Drop the two keys** — remove `sessions_total` and `hours_total` from `manifest.json`'s `metrics[]` so the card declares only what it can source. A small, honest manifest edit.

> Until one of those lands, the emitter **omits both keys** rather than ship a default literal (HARD GUARDRAIL: never invent a metric). If/when the snapshot gains the fields, the emitter starts emitting them automatically once `build_payload` is extended — it never guesses in the meantime.

---

## 4. The honesty mechanism — why `last_report` = the file timestamp, not `now()`

This is the most important line in the spec. **`last_report` must be the snapshot's own export timestamp (`source.exportedAt`, falling back to `generatedAt`), NOT the wall-clock time the emitter runs.**

Why: the hub derives "reporting" from `last_report ≤ 1h` and flips to `stale`/`dormant` past `DORMANT_DAYS = 14` (ph-15 guard). If the emitter stamped `now()`, then *even if Chris stopped practicing and exporting days ago*, the heartbeat would keep saying "fresh" and a dead project would render `live` on the public site. By forwarding the **snapshot's real export time**, the chain stays honest by construction: practice/export stops → `snapshot.source.exportedAt` freezes → `last_report` freezes → the hub degrades the card on its own. The emitter **cannot** make a dead project look alive. This directly serves the charter landmine *"Don't let the site lie."*

Corollary: if `snapshot.json` is **missing or unparseable**, the emitter **skips the POST entirely** (logs + exits 0) so the last good `last_report` stands and naturally ages into stale. It never POSTs a fabricated freshness. **Every error path returns 0 (fail-soft)** so a cron/launchd never red-flags. (Verified in §9.)

---

## 5. The emitter — `woodshed_heartbeat.py` (drop into `public-assets/`)

Python 3 **stdlib only** (`json, os, sys, datetime, urllib`), matching `render_snapshot.py` / `verify_public_safe.py`'s zero-dependency posture. Reads creds from a **git-ignored** local config (§6).

Key functions (mirroring `growroom_heartbeat.py`):
- `load_snapshot()` — `json.load` of `snapshot.json`; raises on missing/bad so `main()` fails soft.
- `to_utc_iso(s)` — normalize an ISO-8601 string (the snapshot's `Z` timestamps) to canonical second-precision UTC `Z`; returns `None` on unparseable input.
- `build_payload(snap)` — emits `streak_days` from `snapshot.streak`; **omits** `sessions_total` / `hours_total`; sets honest `last_report` == `last_activity` from the file timestamp; sets the illustrative `note` when `source.illustrative`.
- `post(payload, local)` — `urllib` POST, `Prefer: resolution=merge-duplicates` upsert, service_role key in `apikey` + `Authorization`.
- `main()` — all fail-soft paths: missing file → skip; unparseable → skip; no honest timestamp → skip (never `now()`); no creds → print payload + skip; HTTP/network error → log + return 0.

CLI: `--once` (default) builds + prints the payload and attempts the POST; **with no creds it prints the payload and skips the POST (exit 0)**. The two `[confirm:]` notes live inline in the module docstring and at the omission site in `build_payload`.

**Verified dry-run output** (run against the real `snapshot.json` with NO creds present):

```json
{
  "project_slug": "the-woodshed",
  "last_report": "2026-06-13T08:40:00Z",
  "last_activity": "2026-06-13T08:40:00Z",
  "status": "live",
  "metric_values": {
    "streak_days": 6
  },
  "note": "illustrative snapshot — not live data"
}
[woodshed-heartbeat] supabase creds not set -> skip POST (dry run; nothing external happened)
```

`streak_days: 6` matches `snapshot.streak`; `sessions_total` / `hours_total` are absent (no source); `last_report` == `last_activity` == the snapshot's `exportedAt` (`2026-06-13T08:40:00Z`, **NOT** the current time); the POST is cleanly skipped; exit 0.

**Why these choices:** stdlib-only (no `pip` on the host, same as the snapshot generator); reads the already-written file (no brain re-export, no contention with the snapshot pipeline); every failure path `return 0` so a bad heartbeat never red-flags launchd; omits a metric rather than inventing it; `last_report` from the file (honesty).

> **Note on the snapshot timezone:** unlike the Growroom dashboard (which writes *local naive* timestamps), `render_snapshot.py` emits ISO-8601 **UTC `Z`** timestamps already, so `to_utc_iso()` is a clean parse-and-canonicalize with no host-tz ambiguity. If `render_snapshot.py` ever changes to a naive local stamp, revisit this (treat as host-local, then convert) — but as shipped it is unambiguous.

---

## 6. Config + secrets (OPSEC)

Creds live in a **NEW git-ignored** file `public-assets/heartbeat.config.local.json` (the emitter reads `supabase_url` + `supabase_service_role_key`):

```json
{
  "supabase_url": "https://<project-ref>.supabase.co",
  "supabase_service_role_key": "<service_role JWT — bypasses RLS, NEVER commit>"
}
```

- **Git-ignore it before adding the key.** Add `public-assets/heartbeat.config.local.json` (or `*.config.local.json`) to `.gitignore` and verify with `git check-ignore public-assets/heartbeat.config.local.json`. Let `gitleaks` gate commits.
- The **service_role key** is the only secret. It bypasses RLS and lives **only** on Chris's host, in the ignored config — never in any repo, never in Vercel, never client-side. It is correct for it to bypass RLS — that is exactly how the push side works; the public site only ever uses the read-only `anon` key.
- The payload carries **only** `streak_days` + timestamps + `status` + an honest `note`. **No tunes/PR/journal detail, no private free-text, no identifiers** — consistent with the snapshot's own privacy posture (`snapshot.schema.json $omitted`). Push-only outbound; nothing inbound to Chris's machine.

---

## 7. Cadence — launchd job

Heartbeats move on minutes-to-hours; **every 5 minutes is plenty** and avoids hammering the free tier. Run it as its **own** launchd job — `com.woodshed.heartbeat.plist`:

```xml
<!-- com.woodshed.heartbeat.plist  ->  ~/Library/LaunchAgents/ -->
<plist version="1.0"><dict>
  <key>Label</key><string>com.woodshed.heartbeat</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/Users/chris/REPLACE-ME/public-assets/woodshed_heartbeat.py</string>
    <string>--once</string>
  </array>
  <key>StartInterval</key><integer>300</integer>   <!-- every 5 min -->
  <key>RunAtLoad</key><true/>
  <key>StandardErrorPath</key><string>/Users/chris/REPLACE-ME/public-assets/heartbeat.log</string>
  <key>StandardOutPath</key><string>/Users/chris/REPLACE-ME/public-assets/heartbeat.log</string>
</dict></plist>
```

`launchctl load ~/Library/LaunchAgents/com.woodshed.heartbeat.plist`. **Fix the two `/Users/chris/REPLACE-ME/...` placeholder paths** to the real host path where `woodshed_heartbeat.py` lives. (Loading it before creds exist is harmless — the script just prints + exits 0.)

**Optional freshness nicety (defer):** since the hub bakes heartbeats at **build time** (ph-5 §5), the public numbers only refresh on redeploy. A Vercel **Deploy Hook** pinged by this job (or a daily cron) re-bakes them. Not required for the DoD — recommend a simple daily rebuild to start.

---

## 8. Apply note (for Claude Code / the host) — ordered

1. **Prereq — the hub's Supabase table must be live (ph-5):** the Supabase project + `heartbeats` table + RLS exist, and `PUBLIC_SUPABASE_*` are on Vercel. If not, do ph-5's apply note first (SUPABASE-HEARTBEATS-SPEC.md §8). Until then this emitter has nothing to POST to.
2. Copy `woodshed_heartbeat.py` into `public-assets/` (already present from this drop).
3. Create `public-assets/heartbeat.config.local.json` with `supabase_url` + `supabase_service_role_key`. **First** add it to `.gitignore` and verify `git check-ignore` flags it.
4. **Resolve the headline `[confirm:]`** with Chris: the `sessions_total` / `hours_total` source gap — **(a)** add session/hours tracking to the brain export + snapshot, **or (b)** drop those two keys from `manifest.json`. (§3.)
5. Dry-test: `python3 woodshed_heartbeat.py --once` → prints the payload, skips the POST until creds are set. With creds set it prints the payload + a `200/201`; then check the Supabase row (Table editor) shows `the-woodshed`.
6. Rebuild/redeploy the hub (or wait for the next build) → confirm the **Woodshed card flips** from "awaiting first report" to a reporting dot with `streak_days` (and an honest em-dash for the two undeclared metrics, until the gap is closed).
7. Load the launchd job (§7). Confirm `heartbeat.log` shows clean runs on the 5-min cadence.
8. **Honesty smoke test:** stop exporting so `snapshot.source.exportedAt` ages; confirm the emitter keeps forwarding the **frozen** timestamp and the hub card correctly goes **stale** past the window (never stuck on `live`).

On ship: move wood-47 to ✅ Shipped with the host note + append a `handoff_inbox.jsonl` line (`project: woodshed`, `milestone: M4`).

---

## 9. Definition of Done

- [ ] `woodshed_heartbeat.py` on the host; `heartbeat.config.local.json` carries the service_role key (git-ignored, never committed; `git check-ignore` / `gitleaks` clean).
- [ ] A real upsert row for `the-woodshed` exists in Supabase with `last_report` = the snapshot's real export time and `streak_days` from `snapshot.streak`.
- [ ] The Woodshed card on `chrisliquin.com` shows a **reporting** dot + the live `streak_days`; an honest em-dash for the two undeclared metrics until the §3 gap is closed.
- [ ] `last_report` is **file-derived, not `now()`** — verified by the §8.8 honesty smoke test (exports stop → card goes stale on its own). *(The dry-run already shows `last_report` = the snapshot's `exportedAt`, not the current time.)*
- [ ] Service_role key is **only** on the host — not in any repo, Vercel, or committed file.
- [ ] Payload carries **only** real-sourced metrics + timestamps + status + honest note — no fabricated `sessions_total` / `hours_total`, no private detail.
- [ ] The emitter **fail-softs** every error path (missing file, bad parse, no timestamp, network, HTTP error) — never crashes the host, never fabricates a value. *(Verified: `py_compile` passes; `--once` no-creds prints + skips; missing-snapshot and unparseable-snapshot both skip + exit 0.)*

---

## 10. Open `[confirm:]` flags (carried up for Chris)

- **`[confirm: sessions_total]` / `[confirm: hours_total]` — the headline open item.** The manifest declares these two heartbeat keys, but **no real source field exists** in `snapshot.json` or the brain on disk. The emitter **omits** them (never fabricates). Close the gap by **(a)** adding session/hours tracking to the brain export + snapshot, **or (b)** dropping the two keys from `manifest.json`. §3.
- `[confirm: ph-5 live]` — the hub's `heartbeats` table/RLS/env must exist before this can POST. That is a Chris/Code step on the Portfolio Hub side. §8.1.
- `[confirm: snapshot timezone, low-risk]` — `render_snapshot.py` emits UTC `Z` timestamps today, so `to_utc_iso()` is unambiguous. Only revisit if the snapshot ever switches to a naive local stamp. §5.
- `[confirm: build-refresh]` — daily rebuild to start, or wire an emitter→Vercel-Deploy-Hook for tighter freshness? §7.
