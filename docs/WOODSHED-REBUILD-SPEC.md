# Woodshed Rebuild — Focus/Tab Unification Spec

**Decision needed:** approve or edit the merge calls below, then I build the full sweep in one pass.
**Date:** June 11, 2026

---

## 1. The actual problem (one diagnosis)

The portal has **two parallel rendering systems** for the same content:

| Concept | Focus Mode renderer | Tab renderer |
|---|---|---|
| Tunes | `renderTuneFocus()` (modes: learn/guides/memorize/solo) | `renderTuneDetail()` (full two-column) |
| Vocab | `renderLickPanel()` | `renderLickPanel()` — **already shared ✅** |
| Gym | `FocusRender.warmup/ladder/clarke/bootcamp/pyramid` | `PAGES.gym` (all tools, one page) |
| Ears | `FocusRender.intervals/transcribe` | `PAGES.ears` |
| Lore/Journal | `FocusRender.lore` | (lives on the Today page) |

When you edited the Jazz Standards layout in Focus Mode, `renderTuneDetail` didn't change — it's literally a different function. Same content, two implementations, guaranteed drift.

**The proof the fix works:** Vocab Lab already uses ONE shared component (`renderLickPanel`) for both the tab and Focus Mode. Edit it once, both update. We make Tunes, Gym, and Ears work the same way.

---

## 2. The architecture (one renderer per section)

For each section, **one** component:

```
renderSection(host, scope, context)
   scope   = { itemId, mode }        // which tune/lick/exercise + which step
   context = 'tab' | 'focus'         // controls chrome only, never content
```

- **Tab** calls it inside a library shell (pickers, grid, browse-all) and defaults `scope` to today's prescribed item.
- **Focus Mode** calls the *same* component, `scope` locked to the day's block, wrapped in the timer/next/prev chrome.

`FocusRender.*` and `PAGES.*` both become thin wrappers. The detailed layout lives in exactly one place.

---

## 3. Nav reorder (to match session flow)

Every day's session runs in this module order: **Gym → Gym → Vocab → Tunes → Ears → Lore**.

**New tab order:**

`Today` · `The Gym` · `Vocab Lab` · `Tune Vault` · `Ears & Lore` · `Progress` · `Manifesto`

- **Today** stays first (dashboard / launchpad — "Start the Session").
- **Gym → Vocab → Tunes → Ears** now mirror the session order exactly.
- **Progress + Manifesto** stay at the end as reference.

*Current order is Today · Vocab · Tunes · Gym · Ears — Gym jumps from 4th to 2nd.*

---

## 4. "Tab lands on today's section" (your Q1 answer)

Each content tab opens **on today's prescribed item**, full Focus-Mode-grade detail, with pickers to deviate. Library/browse sits below.

| Tab | Lands on | Pickers below |
|---|---|---|
| The Gym | Today's warmup (today's Cichowicz group + key + range target) then today's technical block (ladder / Clarke / bootcamp / pyramid per the day) | Full toolkit: tempo ramp, gap trainer, single-tongue test, Clarke circuit |
| Vocab Lab | Today's lick, preloaded *(already does this)* | Category filter + all-licks list + cycle machine |
| Tune Vault | Today's primary tune, preloaded *(already does this)* | Tune grid (Jam Dozen + Expansion), integrations, jam set, My Charts |
| Ears & Lore | Today's ears block (intervals or transcription per the day) | Canon table + lore deck |

---

## 5. Per-section merge calls (best-of-both — your Q2 answer)

Recommendation is the **✅ Keep** column. Strike anything you want dropped; add notes inline.

### 5A. TUNES — the one you flagged

Canonical layout = your Focus Mode structure (the per-step modes you've been tuning). The tab adds library extras around it.

| Element | Source | Call |
|---|---|---|
| Per-step modes: **learn / guides / memorize / solo** (show only what the step needs) | Focus | ✅ Keep — canonical |
| Two-column hero: **book page LEFT, chart + band + memo RIGHT** | Tab | ✅ Keep for tab/full view; Focus uses single-column scoped to the step |
| Skeleton + Etude play-along lines (notation + band) | Both | ✅ Keep (Focus's `guides` mode = this) |
| Inline mixer (bass/drums/piano/click) | Both | ✅ Keep |
| Memorize rungs (2/day cap, 3-day verify gate) | Both | ✅ Keep |
| iReal QR + "all 24" import + forScore CSV | Tab | ✅ Keep — tab only (library utility) |
| Story / videos (with save) / listening embeds / page-fix | Tab | ✅ Keep — tab only, collapsed `<details>` |
| `solo` mode = "BOOK CLOSED, 3 choruses, record one" | Focus | ✅ Keep |
| Tune grid browser + "this week" badge | Tab | ✅ Keep — tab only |
| Jam Set runner (3 tunes) | Tab + Focus `jamset` | ✅ Keep — unify into one runner |

**Open question for you:** in the unified tune panel, should the **book page** show in Focus Mode too (it does in the tab's two-column), or stay hidden in `solo`/`memorize` steps to force memory? *My rec: show in learn/guides, hide in memorize/solo.*

### 5B. GYM

Split the monolith `PAGES.gym` into the same per-block panels Focus uses, then the tab stacks today's blocks + a collapsed toolkit.

| Element | Source | Call |
|---|---|---|
| Warmup panel: today's Cichowicz group (real page) + drone + slurs + range arc | Focus `warmup` (daily-rotating) | ✅ Keep as the shared warmup panel |
| Subdivision Ladder (5 choruses, live caller) | Focus `ladder` (5-chorus) | ✅ Keep — Focus version (tab's was only 4) |
| Clarke ramp (real page + PR protocol) | Focus `clarke` | ✅ Keep |
| 16th-triplet Bootcamp (3 stages) | Both | ✅ Keep |
| Subdivision pyramid | Focus `pyramid` | ✅ Keep |
| Tempo Ramp + Gap Trainer | Tab only | ✅ Keep — tab toolkit (collapsed) |
| Single-Tongue Speed Test + Clarke Circuit links | Tab only | ✅ Keep — tab toolkit |
| 3-column "Hear it / One note / Moving line" bootcamp layout | Tab | ✅ Keep as the bootcamp panel's layout |

### 5C. EARS

| Element | Source | Call |
|---|---|---|
| Interval Trainer (game) | Both | ✅ Keep — one shared widget |
| Transcription Corner (loop → sing → find → play, 0.5× tip) | Both | ✅ Keep — Focus's embedded-player version is richer |
| Sing → Play protocol note | Tab | ✅ Keep |
| Listening Canon table (inline embeds) | Tab only | ✅ Keep — tab only |
| Lore Deck (grid) | Tab only | ✅ Keep — tab only |

### 5D. LORE / JOURNAL

| Element | Source | Call |
|---|---|---|
| Lore card + commute assignment + 3-sentence journal | Focus `lore` | ✅ Keep as shared component |
| Surfaced where on the tab? | — | **Rec:** fold into the bottom of **Ears & Lore** (it's the session's closing block and already shares that tab's name) |

---

## 6. Explicitly NOT touched

Toolbar (metronome/tuner/drone), Band audio engine, curriculum/`CURRICULUM` block data, the Today dashboard cards (hero, This Week, the 6-block grid, release notes), Progress page, Manifesto, score-to-woodshed pipeline, localStorage schema. Pure presentation refactor — no data migration.

---

## 7. Build sequence (full sweep, post-approval)

1. Extract shared section components (Tunes, Gym panels, Ears) — Vocab is the template.
2. Repoint `FocusRender.*` wrappers at them (context='focus').
3. Rebuild `PAGES.gym/tunes/ears` as library shells calling the same components, defaulting to today (context='tab').
4. Reorder nav + Today stays home.
5. Verify: headless render parity (tab vs focus produce identical section DOM), nav-order assertion, console-clean, screenshots.

**Risk:** it's a 232KB single file; the refactor touches ~600 lines across 4 sections. Mitigation = the parity test in step 5 proves tab and focus render the same thing before you re-test live.

---

## 8. Your call

1. Approve the nav order (§3)?
2. Any **strike/keep** edits to the merge tables (§5)?
3. The two open questions: **book page visibility in Focus** (§5A) and **where Lore lives on the tabs** (§5D)?
