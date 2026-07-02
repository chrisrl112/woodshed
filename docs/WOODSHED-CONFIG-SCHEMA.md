# `woodshed-config.json` — Contract (wood-30)

**Status:** SPEC ONLY. No reader/writer built yet. The config **page** (wood-39) writes this file;
a config-driven **session** (wood-31 / wood-40) reads it. This document is the DECIDED output shape
those tasks build against.
**Sibling contracts:** `plan-override.schema.md` (the nightly steer) and `mission-control.schema.json`
(the state export). This config is their persistent, user-set sibling. Conventions match: `schemaVersion`
string `"1.0"`, ISO-8601 `generatedAt`, camelCase fields, graceful degradation, safety floors, an open
`[confirm:]` section.
**Author:** Opus build subagent · 2026-06-19

---

## 1. Purpose

A small, optional sibling file the Woodshed app reads at load. It is the **transparency layer**: the
persistent, **user-set** picture of what gets served — which exercises appear, which Cichowicz page,
which Clarke section, the song of the week, the warm-up key, and the range top. Where `plan-override.json`
is the **night agent's one-day steer** (minutes / order / inclusion for *today only*), this config is
**Chris's standing intent** that holds across days until he changes it.

The spine of the contract is a single top-level **`auto`** boolean:

- **`auto: true`** (default) → the app behaves **exactly as it does today**: every field is computed from
  the date (day-of-week and day-index rotations). The config object is read but its per-exercise selections
  are **ignored** — only `auto` and bookkeeping fields matter. This is the date-driven status quo.
- **`auto: false`** → the config's **explicit selections win**. For each field the user set, the app serves
  that fixed value instead of the date-driven default. Any field left `null` (or omitted) falls back to its
  date-driven value even in manual mode — so manual mode is **per-field**, not all-or-nothing.

**Hard rule (graceful degradation):** with no `woodshed-config.json` present (or one that is malformed,
or with `auto:true`), the app behaves **exactly as before** — date-driven. The reader never throws; failures
log a quiet `console.info` and no-op. Nothing about this file can make the app serve *less* than a valid day.

## 2. Where it lives & how it's read

- **Location:** `Projects/Trumpet/woodshed-config.json` — same folder as `index.html`, fetched relative
  (`fetch('woodshed-config.json')`).
- **When:** once, during boot, after `loadState()` and **before** the first plan render, alongside
  `loadPlanOverride()`.
- **No date gate.** Unlike `plan-override.json` (which fires only when `date === todayKey()`), this config is
  **persistent** — it applies every day until rewritten. There is no `date` field; `generatedAt` is bookkeeping
  only, never a gate.
- **Application point:** the config supplies the **base** date-driven values' replacements; an active
  `plan-override.json` then steers *on top* (see §5, precedence). Like the override reader, the config reader
  returns a **derived copy** — `CURRICULUM`, `CICH_SECTIONS`, `CLARKE_SECTIONS`, `TUNES`, `CYCLE4` are
  **never mutated**. Removing the file restores pure date-driven behavior on reload.

## 3. Fields

### 3a. Top-level

| Field | Type | Required | Default | Meaning |
|---|---|---|---|---|
| `schemaVersion` | string | yes | `"1.0"` | Contract version. Bump on field changes. |
| `generatedAt` | string (ISO-8601) | yes | — | When the config page last wrote this. `new Date().toISOString()`. Bookkeeping only — **not** a gate. |
| `auto` | boolean | yes | `true` | **The spine.** `true` = date-driven status quo (config selections ignored). `false` = config's explicit per-field selections win; `null`/omitted fields still fall back to date-driven. |
| `config` | object | yes | see §3b | The per-exercise selections. Read only when `auto:false`. |

### 3b. `config` — per-exercise selections

Every field here is **optional and nullable**. `null` (or omitted) means "no opinion — use the date-driven
default for this field," even when `auto:false`. A non-null value is honored **only** when `auto:false` **and**
the value is valid against its domain (else it's ignored gracefully and the date-driven default stands).

| Field | Type | Default (date-driven) | Domain / valid values | Controls | Source in `index.html` |
|---|---|---|---|---|---|
| `exercisesShown` | array of module ids | `null` (all of the day's blocks shown) | subset of `["gym","vocab","tunes","ears","today"]` | Which curriculum **modules** appear in the served day. A subset filters the day's blocks to those modules; safety floor below prevents an empty day. | Module ids `gym`/`vocab`/`tunes`/`ears`/`today` — `CURRICULUM[].blocks[].module` (line ~959+). |
| `cichowiczPage` | string \| null | `null` (rotates `CICH_SECTIONS[dayIdx % 7]`) | one of the `CICH_SECTIONS` names: `"Long Tones — Group A"`, `"Group B"`, `"Group C"`, `"Group D"`, `"Group E"`, `"Group F"`, `"Group G"`, `"Set 2 — Groups A–G"` | The warm-up's Cichowicz group/page. Pins one group instead of the daily rotation. The page render uses that section's `pdf` index into `Cichowicz.pdf`. | `CICH_SECTIONS` array (line ~860–861); selected at `CICH_SECTIONS[P.di.dayIdx%7]` (line 1863). Group D → `pdf:14`. |
| `clarkeSection` | string \| null | `null` (rotates `CLARKE_SECTIONS[[0,2,3,2,0,3,2][dow]]`) | one of the `CLARKE_SECTIONS` names: `"First Study (sotto voce!)"`, `"Etude I"`, `"Second Study"`, `"Third Study"`, `"Fourth Study"`, `"Fifth Study"` | The Clarke ramp's study/section. Pins one study instead of the daily rotation. Render uses that section's `pdf` (and `pages` for the multi-page Second Study) into `CLARKE_FILE`. | `CLARKE_SECTIONS` array (line ~857–858); selected at `CLARKE_SECTIONS[[0,2,3,2,0,3,2][P.di.dow]]` (line 1901). |
| `songOfWeek` | string \| null | `null` (rotation primary, or `S.pin` if set) | any `TUNES[].id` (e.g. `"recordame"`, `"autumn"`, `"blues"`, `"bossa"`, `"atrain"`, `"attya"`, `"four"`, `"solar"`, `"oleo"`, `"footprints"`, `"stella"`, …) | The week's **primary** tune (the one actively built). A persistent, user-set parallel to `S.pin` / `plan-override.pinnedTune`. Honored only if the id exists in `TUNES`. | `TUNES[].id` (line 617+, e.g. `recordame` line 819). Primary resolution in `pickTunes()` (lines ~2499–2501); pin via `S.pin`. |
| `warmupKey` | integer (0–11) \| null | `null` (rotates `mod12(CYCLE4[dayIdx % 12])`) | pitch-class 0–11 (written key; `0`=C, `5`=F, `10`=B♭, `7`=G, …). Concert = `mod12(key-2)`. | The warm-up / drone key. Pins one key instead of the circle-of-fourths daily rotation. The drone plays concert = `key-2`. | `CYCLE4=[0,5,10,3,8,1,6,11,4,9,2,7]` (line 370); key = `mod12(CYCLE4[P.di.dayIdx%12])` (line 1862). |
| `rangeTop` | integer \| null | `21` (A5) | semitones above middle-C (MIDI 60). Sensible set: `16` (E5), `19` (G5), `21` (A5), `22` (B♭5). `fundRange()` arcs through `[0,4,7,12,16,19,21,22]` capped at this value. | The day's range-arc target note. Pins one ceiling instead of the per-dow array. | Today: `[19,19,21,21,22,22,16][P.di.dow]` (line 1864) → 21 = A5. **wood-37 is concurrently fixing this to a fixed `21` (A5)**, so the config default is `21`. `fundRange(top)` (line 584). |

#### Default value summary (the values the example file ships)

| Field | Shipped default | Why |
|---|---|---|
| `exercisesShown` | `null` | Show all of the day's blocks (status quo). |
| `cichowiczPage` | `null` | Keep daily Cichowicz rotation. |
| `clarkeSection` | `null` | Keep daily Clarke rotation. |
| `songOfWeek` | `null` | Keep weekly tune rotation. |
| `warmupKey` | `null` | Keep circle-of-fourths key rotation. |
| `rangeTop` | `21` | A5 — the fixed target wood-37 is standardizing; a real, safe ceiling rather than a per-day guess. |

With `auto:true` (the shipped default), **all of these are ignored anyway** and the app is fully date-driven —
so the example is a safe no-op that documents the shape without changing behavior.

### 3c. Safety floors (to be enforced by the reader — wood-31/wood-40)

- **Never empty the day.** If `exercisesShown` would remove every block (empty array, or a subset matching no
  block in today's plan), the filter is **skipped** and the full day is served. The app must never render a
  day with zero blocks.
- **Validate against real domains.** A `cichowiczPage` / `clarkeSection` / `songOfWeek` / `warmupKey` /
  `rangeTop` value that is not in its documented domain is **ignored**, and that field falls back to its
  date-driven default. No new sections, tunes, keys, or notes are invented.
- **No fabricated notation or metrics.** The reader only *selects among existing* exercises, pages, sections,
  tunes, keys, and the existing range-arc ceiling. It never synthesizes musical content.
- **`rangeTop` clamp.** Honored values should clamp to the `fundRange()` arc set (`≤ 22`, `≥` a sane floor such
  as `12`); out-of-range values fall back to the default (`21`).
- **Never throws.** The whole reader is wrapped in try/catch; any internal failure returns the **date-driven
  day** unchanged.

## 4. Example

A concrete, valid example lives in `woodshed-config.example.json`. It is named `.example.json` so it is
**never fetched** by the app — only a file literally named `woodshed-config.json` is read. To go live, copy
the example to `woodshed-config.json` and set `auto:false` plus whatever fields you want to pin.

Inline example (the shipped, safe no-op default — `auto:true`):

```json
{
  "schemaVersion": "1.0",
  "generatedAt": "2026-06-19T05:00:00.000Z",
  "auto": true,
  "config": {
    "exercisesShown": null,
    "cichowiczPage": null,
    "clarkeSection": null,
    "songOfWeek": null,
    "warmupKey": null,
    "rangeTop": 21
  }
}
```

Inline example (manual mode — Chris pins a focused day):

```json
{
  "schemaVersion": "1.0",
  "generatedAt": "2026-06-19T05:00:00.000Z",
  "auto": false,
  "config": {
    "exercisesShown": ["gym", "tunes"],
    "cichowiczPage": "Group D",
    "clarkeSection": "Second Study",
    "songOfWeek": "recordame",
    "warmupKey": 5,
    "rangeTop": 21
  }
}
```

How the reader applies the manual example: the day is filtered to `gym` + `tunes` blocks only (other modules
hidden, but never to an empty day); the warm-up shows Cichowicz **Group D** (`Cichowicz.pdf` page 14) instead
of the daily group; the Clarke ramp shows the **Second Study** (the two-page study) instead of the daily
section; **Recorda Me** is held as the week's primary tune; the warm-up/drone runs in written **F** (`5`),
concert E♭ (`mod12(5-2)=3`); and the range arc targets **A5** (`21`).

## 5. Composition with `plan-override.json` (precedence)

These two files are **siblings with different jobs and different lifetimes**:

| | `woodshed-config.json` (this) | `plan-override.json` (wood-9) |
|---|---|---|
| Author | Chris, via the config page (wood-39) | The night agent (wood-15) |
| Lifetime | **Persistent** — every day until rewritten | **One day** — gated to `date === todayKey()` |
| Job | *Transparency layer* — what is served by default | *Steer* — bend today's minutes / order / inclusion |
| Gate | none (`auto` flag instead) | `date` must equal today |

**Precedence (lowest → highest):**

1. **Date-driven defaults** — the static `CURRICULUM[dow]` plus the daily rotations
   (`CICH_SECTIONS`, `CLARKE_SECTIONS`, `CYCLE4`, the per-dow `rangeTop`, the rotation primary tune).
2. **`woodshed-config.json` (when `auto:false`)** — replaces the date-driven *base selections* per field
   (which modules, which Cichowicz page, which Clarke section, which tune, which key, which range top).
   When `auto:true`, this layer is a no-op.
3. **`plan-override.json` (when dated for today)** — the night agent's steer applies **last, on top of**
   whatever base the config produced. The override's levers (`setMinutes` / `dropModules` / `addBlocks` /
   `order` / `scaleToMinutes` / `pinnedTune` / `blocks`) operate on the config-selected day, not the raw
   date-driven day.

So: **config sets the stage (persistent intent); the override directs today's scene (one-day steer).** They
do not conflict — they stack. The config never overrides the override; the override never edits the config.

**Boundary note:** the config's `songOfWeek` and the override's `pinnedTune` both touch the primary tune.
Precedence resolves it cleanly — if both are present and valid for today, the override's `pinnedTune` wins for
today (it is the higher, day-specific layer); the config's `songOfWeek` resumes the next day when no override
fires. Like the override reader, neither persists to `S.pin` unless a separate, deliberate decision says so
(see `[confirm:]` below).

## 6. Open `[confirm:]` items

- **`[confirm: pin-write authority]`** — does setting `songOfWeek` *persist* to `S.pin` (the app's real pin
  store), or stay in-memory like the override's `pinnedTune`? Default assumption here: **in-memory for the
  served render only**, matching the override reader's deliberate non-persistence. Confirm whether the config
  page should write `S.pin` directly.
- **`[confirm: warmupKey representation]`** — pitch-class integer 0–11 (written key) is used here to match
  `CYCLE4`/`mod12` in code. If the config **page** (wood-39) should present keys by name (e.g. "F", "B♭"),
  that is a UI mapping over the same stored integer — confirm the stored type stays the integer.
- **`[confirm: cichowiczPage / clarkeSection key form]`** — fields store the section **name** string (the
  human label already in `CICH_SECTIONS`/`CLARKE_SECTIONS`). An alternative is a numeric index into those
  arrays. Name strings are chosen here for transparency/readability; confirm before wood-39 builds the picker.
- **`[confirm: rangeTop UI units]`** — stored as semitones above middle-C (the code's unit). The config page
  should present it as a note name (E5 / G5 / A5 / B♭5). Confirm the stored unit stays semitones.
- **`[confirm: exercisesShown granularity]`** — this filters by **module** (`gym`/`vocab`/`tunes`/`ears`/
  `today`), not by individual block/preset. If Chris wants to toggle *individual named warm-up exercises*
  (flow / lip slurs / range arc / Cichowicz / drone) independently, that is a finer-grained field not yet
  modeled — confirm whether module-level is enough for v1.
