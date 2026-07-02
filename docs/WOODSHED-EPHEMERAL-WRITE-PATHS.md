# Woodshed EPHEMERAL Mode — Write-Path Inventory & Central-Gating Design Spec

**Task:** wood-42 · **Milestone:** M3 · **Priority:** P1 · **Date:** 2026-06-27
**Purpose:** Inventory every state-write path in `index.html` and specify a minimal, central set of chokepoint guards so a single `EPHEMERAL` flag turns the app read-only for the published/public build.

> **STATUS: SPEC ONLY — code apply is GATED on wood-32 (supervised renderSection merge). Do not apply unsupervised.**
> This document is the planning half of wood-42. The actual edits to `index.html` / `woodshed_server.py` stay for a supervised run after wood-32 lands. Nothing here changes app behavior.

---

## 1. The core insight

The app has **~30 raw write paths** (≈20 localStorage calls, 3 server POSTs, 4 file-export sites, 1 IndexedDB handle write, 1 state-load read to redirect). They are not 30 independent problems. They **funnel through 5–6 chokepoints**:

| Chokepoint | Raw paths collapsed | index.html line |
|---|---|---|
| `saveState()` | ~20 localStorage writes | L1631 |
| `saveToServer()` | 3 disk POSTs | L2134 |
| `downloadBlob()` + 3 standalone export fns | 4 file exports | L2124 / L893 / L911 / L3278 |
| `PDFV.load()` book-access + `PDFV.saveHandle()` | IndexedDB write + local-PDF open | L1731 / L1726 |
| `loadState()` → snapshot seed | 1 read (redirect, not block) | L1625 |

**Guard the chokepoint, never the ~20 call sites.** A single `if(EPHEMERAL) return;` at the top of `saveState()` neutralizes all 20 persistence calls at once. This is the keystone of the design.

---

## 2. The EPHEMERAL flag

A single top-of-script constant, defaulting to **FALSE** so Chris's private local build is byte-for-byte unaffected, and **impossible to flip on accidentally** in the local build.

```js
// near the top of the main inline <script>, before loadState()
const EPHEMERAL = (document.querySelector('meta[name="woodshed-mode"]')?.content === 'ephemeral');
```

### Flag-source options

| Option | How it's set | Default-false? | Accidental-flip risk | Notes |
|---|---|---|---|---|
| **A. `<meta name="woodshed-mode" content="ephemeral">`** (recommended) | Public build's `index.html` `<head>` carries the meta; local build omits it. | Yes — absent ⇒ false | Very low — Chris's local file never has the tag | Explicit, greppable, build-step-friendly, zero runtime ambiguity |
| B. Build-time constant | A build script rewrites `const EPHEMERAL=false` → `true` when emitting the public build | Yes | Low, but requires a build pipeline that doesn't exist yet | More machinery than the single-file workflow uses today |
| C. `location` check (hostname ≠ localhost / file://) | Infer from where it's served | Yes-ish | **Medium** — any non-localhost preview (e.g. LAN IP, ngrok) silently goes read-only; fragile | Rejected: too implicit, surprises during local testing |

**Recommendation: Option A (meta tag).** It is explicit, requires no build pipeline, survives the current "one file" workflow, and is trivially auditable (grep for `woodshed-mode`). The local `index.html` simply never carries the tag, so EPHEMERAL is structurally false there.

---

## 3. Full write-path inventory

State store shape (L1623 `DEFAULT_S`): `{streak,lastDay,sessions,prs,tuneStatus,lickKeys,journal,pageOver,vids,writtenView,bpm,earBest,mix,pin,week,blocksDone,blockLogs,feedback,config}`. `let S=DEFAULT_S` (L1624).

### Category 1 — localStorage state writes (primary persistence)

| Symbol / site | index.html line(s) | Persists | Neutralized by |
|---|---|---|---|
| `saveState()` **(def)** | **L1631** `localStorage.setItem('woodshed_v1',…)` | Entire `S` blob | **Guard here** → covers all below |
| Metro.setBpm | L1116 | bpm | via saveState |
| logMinutes | L1638 | sessions/streak | via saveState |
| written-toggle | L1694 | writtenView | via saveState |
| (misc) | L1858 | — | via saveState |
| day-note save | L2068 | journal | via saveState |
| block save | L2089 | blockLogs/blocksDone | via saveState |
| band-mix sync | L2323 | mix | via saveState |
| mix oninput | L2465 | mix | via saveState |
| vidsave | L2494 | vids | via saveState |
| pagesave | L2495 | pageOver | via saveState |
| (misc) | L2717 | — | via saveState |
| lick keys | L2963 | lickKeys | via saveState |
| (misc) | L3074, L3078, L3087 | — | via saveState |
| rung status | L3095 | tuneStatus | via saveState |
| pin | L3096 | pin | via saveState |
| PR log | L3103 | prs | via saveState |
| import (overwrites S then saves) | L3281 | full S | via saveState (also see Cat 5 / §8) |
| config applyLive | L3350 | config | via saveState |
| `beforeunload` → saveState | **L3446** | full S on unload | via saveState |

> All 20 sites call `saveState()`. One guard at L1631 = all 20 neutralized.

### Category 2 — server POSTs (write to disk via woodshed_server.py)

| Symbol / site | index.html line | Endpoint → server effect (woodshed_server.py do_POST L166) | Neutralized by |
|---|---|---|---|
| `saveToServer()` **(def)** | **L2134** `fetch(endpoint,{method:'POST',…})` | — | **Guard here** |
| save-brain | L2208 | `/save-brain` → writes mission-control.json verbatim | via saveToServer |
| save-day | L2214 | `/save-day` → writes logs/<date>.md | via saveToServer |
| save-feedback | L2331 | `/save-feedback` → APPENDS one NDJSON line to feedback.jsonl | via saveToServer |

> Public build won't run the server, so these would fail anyway — but gating `saveToServer()` is cheap defense-in-depth and removes the download-fallback side effects too (see Cat 3).

### Category 3 — blob downloads / file exports

| Symbol / site | index.html line(s) | Exports | Neutralized by |
|---|---|---|---|
| `downloadBlob()` **(def)** | **L2124** | (used as server-offline fallback L2209/L2215/L2332; config export L3427) | **Guard here** (per Chris decision §8) |
| `downloadIrealHTML()` | **L893** (Blob+click L907–908) | iReal Pro chart HTML | guard fn head |
| `downloadForscoreCSV()` | **L911** (Blob+click L918–919) | forScore CSV | guard fn head |
| `#exp` backup-export | **L3278–3279** `new Blob([JSON.stringify(S)])` → woodshed-backup-<date>.json | full S backup | guard at site |

> **Decision needed (§8):** exports only emit the visitor's *ephemeral in-memory S* (nothing server-side), so they are arguably harmless publicly. But wood-42 next_action explicitly says "short-circuit exports." The config-export at L3427 is described in the UI (L3384) as a tool to "hand the same setup to the public build" — so it may *want* to stay enabled.

### Category 4 — IndexedDB book-handle persistence (ties to M0/M3 content policy)

| Symbol / site | index.html line | Effect | Neutralized by |
|---|---|---|---|
| `PDFV.openIDB()` | L1720 | opens `indexedDB.open('woodshed',1)`, store 'handles' | short-circuited via load() gate |
| `PDFV.getHandle(key)` | L1723 | reads persisted handle | short-circuited |
| `PDFV.saveHandle(key,h)` | **L1726** `…objectStore('handles').put(h,key)` | **the IndexedDB WRITE** | guard fn head + load() gate |
| `PDFV.load(fileKey)` | **L1731** | branch (1) relative-URL fetch; (2) File System Access **persisted handle** + `showOpenFilePicker` (L1738) then `saveHandle` (L1739); (3) plain file-input fallback (L1744) | **Guard the book-access branches** |

> In EPHEMERAL the app must **not open local source PDFs at all**. It renders only the pre-rendered per-tune page images in `public-assets/pages/` (M0 content policy + wood-44/wood-45 page-manifest). So EPHEMERAL must short-circuit `PDFV.load()`'s branches (2) and (3) and the IndexedDB write. This is the wood-42 ↔ wood-72 handshake (§6).

### Category 5 — reads relevant to ephemeral SEEDING (not writes, but the spec must address)

| Symbol / site | index.html line | Behavior today | EPHEMERAL behavior |
|---|---|---|---|
| `loadState()` | **L1625** reads `localStorage('woodshed_v1')` | seeds S from local storage | **Seed S from published read-only `snapshot.json`** (wood-43 pipeline in public-assets/; schema `snapshot.schema.json`), never write back |
| plan-override fetch | L2518 `fetch('plan-override.json')` | read | keep as-is |
| config fetch | L2618 `fetch('woodshed-config.json')` | read | keep as-is |
| soundfont fetch | L1075 | read | keep as-is |

---

## 4. Central-gate design (the 5–6 chokepoints)

All changes are **additive and minimal** — a guard at the top of an existing function. No call-site edits. Pseudocode only; **do not write into index.html here.**

**4.1 `saveState()` — L1631 (keystone)**
```js
function saveState(){ if(EPHEMERAL) return;            // ← add this line
  S.bpm=Metro.bpm; try{ localStorage.setItem('woodshed_v1',JSON.stringify(S)); }catch(e){} }
```
Neutralizes all ~20 Category-1 paths and `beforeunload`.

**4.2 `saveToServer()` — L2134**
```js
async function saveToServer(endpoint,text,mime){
  if(EPHEMERAL) throw new Error('ephemeral: server writes disabled');  // ← reject so callers no-op cleanly
  const res=await fetch(...); ... }
```
Throwing (vs returning) preserves the existing try/catch fallback contract; but in EPHEMERAL the fallback `downloadBlob` must ALSO be gated (see 4.3) so no file is emitted. Alternatively make it a silent no-op returning `{ok:true}` to suppress the download fallback entirely — **recommended**, simpler, no exfil.

**4.3 `downloadBlob()` + 3 standalone exports — L2124 / L893 / L911 / L3278**
Per Chris's §8 decision. Default recommendation (option below): guard `downloadBlob()`, `downloadIrealHTML()`, `downloadForscoreCSV()`, and the `#exp` backup site with `if(EPHEMERAL) return;` at each head, **except** the config-export at L3427 which is gated by a separate sub-flag so it can stay enabled if Chris wants the "hand setup to public build" tool live.

**4.4 `PDFV.load()` book access + `PDFV.saveHandle()` — L1731 / L1726**
```js
async saveHandle(key,h){ if(EPHEMERAL) return; ... }   // L1726
async load(fileKey){
  if(this.docs[fileKey]){...return true;}
  // branch (1) relative-URL fetch of pre-rendered asset stays
  if(EPHEMERAL) return false;   // ← skip branches (2)+(3): no getHandle/showOpenFilePicker/file-input
  ... }
```
In EPHEMERAL the viewer falls back to the per-tune page images in `public-assets/pages/`; the full source PDF is never opened. (Confirm the page-image render path is wired by wood-44/wood-45 before relying on the `return false`.)

**4.5 `loadState()` → snapshot seed — L1625**
```js
function loadState(){
  if(EPHEMERAL){ /* fetch published snapshot.json (sync-seeded or await before first render),
                    validate vs snapshot.schema.json, S={...DEFAULT_S,...snapshot}; never persist */ }
  else { try{ S={...DEFAULT_S,...JSON.parse(localStorage.getItem('woodshed_v1')||'{}')}; }catch(e){ S={...DEFAULT_S}; } }
  ... migrate/mix lines unchanged ... }
```
Note: snapshot load is async (fetch) whereas current `loadState()` is sync (called at L3433). The apply must sequence the first render after the snapshot resolves, or pre-inline the snapshot. **Flag this sequencing detail to the supervised apply.**

---

## 5. (reserved — see §6 handshake)

## 6. The wood-42 ↔ wood-72 handshake

wood-72 ("block full-PDF access at serve time") needs exactly the mechanism in §4.4: in the public build the app must never open the full source PDF, only pre-rendered page images. The `EPHEMERAL` guard on `PDFV.load()` branches (2)/(3) + `saveHandle()` IS that block on the client side; wood-72 adds the serve-time enforcement so the PDFs aren't shipped at all. **They should land together** — gating `PDFV.load()` without the page-image fallback (wood-44/45) would leave EPHEMERAL unable to show charts; shipping wood-72's serve-time block without §4.4 would leave a dead client code path trying to open files that aren't there. Sequence: wood-44/45 page assets → wood-42 §4.4 client gate → wood-72 serve-time block.

## 7. Apply checklist (future supervised run, post wood-32)

1. **Back up** `index.html` → `index.html.bak-YYYYMMDD`.
2. Confirm wood-32 (renderSection merge) has landed; re-verify the line numbers in §3 still resolve (the merge may shift them).
3. Add the `EPHEMERAL` flag constant (§2 Option A) near the top of the main inline script, before `loadState()`.
4. Guard each chokepoint (§4.1–4.5). Prefer chokepoint guards; touch no call sites.
5. Wire the snapshot seed in `loadState()` (§4.5) and resolve the async-sequencing detail before first render.
6. Decide & implement the exports gate per §8.
7. Add the `<meta name="woodshed-mode" content="ephemeral">` tag to the **public** build's `<head>` only (never the local file).
8. `node --check` every inline `<script>` block (extract & validate) to confirm no syntax breakage.
9. **Test matrix:**
   - **EPHEMERAL=false** → behavior byte-identical to today: localStorage writes, server POSTs, exports, PDF open, IndexedDB handle all work.
   - **EPHEMERAL=true** → no localStorage writes (verify storage untouched after edits/reload); no server POSTs; exports per §8 decision; no local PDF open / no IndexedDB write (only `public-assets/pages/` images render); S seeded from `snapshot.json` and never persisted.

## 8. Open decisions / [confirm: Chris]

| # | Decision | Options | Recommended default |
|---|---|---|---|
| D-1 | **Exports in EPHEMERAL** (Cat 3) | (a) disable all 4 export paths; (b) disable personal/backup exports but **keep config-export** (L3427), since it only touches ephemeral state and is the documented "hand setup to public build" tool; (c) keep all | **(b)** — honor "short-circuit exports" for personal/backup data while keeping the config-export tool live behind a sub-flag. Defer-with-context if Chris wants all-off. |
| D-2 | **Flag source** (§2) | A meta tag / B build constant / C location check | **A — meta tag.** Explicit, no build pipeline, default-false, accident-proof. |
| D-3 | **saveToServer in EPHEMERAL** (§4.2) | throw (keeps fallback) vs silent no-op (suppresses download fallback) | **Silent no-op returning `{ok:true}`** — no file emitted, no exfil, simplest. |
| D-4 | **Snapshot seeding async sequencing** (§4.5) | await snapshot before first render vs pre-inline snapshot into the page | Await-before-first-render unless build can pre-inline; surface to supervised apply. |

## 9. Why this waits on wood-32

The wood-32 renderSection merge restructures the render/state surface — the same region of `index.html` where several Category-1 call sites and the render path live. Gating now risks adding guards to code that is about to move or be refactored, creating merge conflicts and stale line references. **The inventory and chokepoint design in this spec are durable** regardless of that refactor (the chokepoint functions — `saveState`, `saveToServer`, `downloadBlob`, `PDFV.load`, `loadState` — are stable anchors). Only the *apply* waits, so wood-42 can proceed the moment wood-32 merges, with §7's step 2 re-verifying line numbers first.
