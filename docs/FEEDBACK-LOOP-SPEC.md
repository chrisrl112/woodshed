# Woodshed Feedback Loop — Spec (wood-9)

**Status:** Capture surface BUILT (this slice). Night agent NOT built — Chris-owned, spec'd below.
**Sibling contract:** `mission-control.schema.json` / `mission-control.example.json` (wood-7).
**Author:** Opus build subagent · 2026-06-13

---

## 1. Purpose

Close the practice loop. Today the curriculum is **static**: `CURRICULUM[dow]` defines a fixed
6-block plan per weekday, and `pickTunes()` advances the primary tune on a fixed rotation. The app
already captures rich per-session reactions — per-block notes, a "ready to advance" checkbox, the
"one line for tomorrow" day note — but nothing **reads them back** to steer tomorrow.

The feedback loop fixes that. Each session end, the app emits one append-only `feedback.jsonl`
line capturing how today actually *felt*. Overnight, a scheduled **night agent** reads yesterday's
line(s) plus `mission-control.json` and adjusts tomorrow's served plan: demote what was too easy,
repeat/extend what was too hard, honor "drop this," scale block minutes to tomorrow's available
time. The static curriculum becomes a starting point the loop bends toward Chris's real reactions.

Two halves, two owners:
- **Capture** (this slice, done): a 15-second surface in the closing block → `feedback.jsonl` line.
- **Incorporation** (Chris wires later): a scheduled night-agent prompt that consumes the line.

---

## 2. `feedback.jsonl` schema (append-only, one JSON object per line)

Newline-delimited JSON (NDJSON), mime `application/x-ndjson`. Each session appends **one line**.
Never rewritten in place — the night agent reads the **last line whose `date` matches yesterday**
(or the tail N lines). Conventions mirror `mission-control.schema.json`: `schemaVersion`,
ISO-8601 `generatedAt`, ISO `date`, camelCase keys.

| Field | Type | Source / meaning |
|---|---|---|
| `schemaVersion` | string | Contract version, `"1.0"`. Bump on field changes. |
| `date` | string (YYYY-MM-DD) | The practice day. Source: `todayKey()`. The night agent's join key. |
| `generatedAt` | string (ISO-8601) | When the line was exported. Source: `new Date().toISOString()`. |
| `weekIndex` | integer | Zero-based week. Source: `dayInfo().weekIdx`. Lets the agent align with mission-control. |
| `dow` | integer 0–6 | Day-of-week, 0=Mon. Source: `dayInfo().dow`. |
| `focus` | string | Day's curriculum theme. Source: `todaysPicks().plan.focus`. |
| `primaryTune` | string | Tune id worked today. Source: `todaysPicks().tune.id`. |
| `blocksLogged` | integer | Count of blocks with a note or advance flag. Source: `compileDayLog()` filter. |
| `blocksTotal` | integer | Planned block count today. Source: `todaysPicks().plan.blocks.length`. |
| `blocksLoggedRatio` | number 0–1 | `blocksLogged / blocksTotal`, rounded to 2dp. A completeness signal. |
| `moduleReactions` | object | Per-module reaction map (see below). Keys = module ids present today. |
| `blocks` | array | Per-block detail (see below). Derived from `compileDayLog()` + the day's plan. |
| `dropTomorrow` | array of strings | Module ids Chris flagged "drop tomorrow." Explicit demote signal. |
| `moreOfThis` | array of strings | Module ids Chris flagged "more of this." Explicit promote signal. |
| `energy` | string enum | `"low" \| "ok" \| "high"` — how today felt. Default `"ok"`. |
| `timeTomorrow` | integer (minutes) | Minutes available tomorrow. Enum-backed selector: 20/40/60/75. Default 60. |
| `ownedTunes` | array of strings | Tune ids that felt **owned** today. Derived: memorized OR a tune-block with `advance`. |
| `shakyTunes` | array of strings | Tune ids that felt **shaky**: a tune-block logged but **not** advanced. |
| `oneLineForTomorrow` | string | The freeform `#fo-day` day note. Source: `S.blockLogs[k].day.note`. |

### 2a. `moduleReactions` object

Keyed by module id (`gym`, `vocab`, `tunes`, `ears`, `today` — whichever appear in today's plan).
Each value is one of `"too_easy" | "on_point" | "too_hard"`. Default `"on_point"` for any module
the user doesn't touch (sensible no-op default so the loop never starves).

```json
"moduleReactions": { "gym": "too_easy", "vocab": "on_point", "tunes": "too_hard", "ears": "on_point", "today": "on_point" }
```

A module's reaction can ALSO be inferred when not set: if every block in a module is marked
`advance`, treat as `too_easy`-leaning; if a block is logged-but-not-advanced, `too_hard`-leaning.
The explicit selector wins; inference is a fallback so the line is useful even on a 15-second exit.

### 2b. `blocks` array

One object per planned block, so the night agent can act at block granularity, not just module:

```json
{ "idx": 1, "title": "Subdivision Ladder", "module": "gym", "min": 14, "logged": true, "advance": true, "note": "hit 168, ceiling felt soft" }
```

Source: `compileDayLog()` returns `{idx,title,module,min,log}`; `note`/`advance` come from `log`.
`note` is included verbatim (it's the richest signal for an LLM agent) — strip nothing.

### 2c. Concrete example line (valid JSON, validates against this schema)

```json
{"schemaVersion":"1.0","date":"2026-06-13","generatedAt":"2026-06-13T22:05:00.000Z","weekIndex":22,"dow":4,"focus":"Jam Simulation","primaryTune":"recordame","blocksLogged":4,"blocksTotal":6,"blocksLoggedRatio":0.67,"moduleReactions":{"gym":"too_easy","vocab":"on_point","tunes":"too_hard","ears":"on_point","today":"on_point"},"blocks":[{"idx":0,"title":"Sound & Flow","module":"gym","min":10,"logged":true,"advance":true,"note":"easy, could shorten"},{"idx":1,"title":"Subdivision Ladder","module":"gym","min":14,"logged":true,"advance":true,"note":"hit 168"},{"idx":3,"title":"Tune of the Week — melody & roots","module":"tunes","min":12,"logged":true,"advance":false,"note":"bridge still shaky"},{"idx":4,"title":"Daily Ears — transcription","module":"ears","min":5,"logged":true,"advance":false,"note":"got the first phrase"}],"dropTomorrow":["gym"],"moreOfThis":["tunes"],"energy":"ok","timeTomorrow":40,"ownedTunes":["valentine"],"shakyTunes":["recordame"],"oneLineForTomorrow":"Slow the Recorda Me bridge to 0.5x and own the ii-V before adding speed."}
```

---

## 3. Capture surface (BUILT this slice)

**Where it lives:** the closing block (`FocusRender.lore`, the "Lore + day review" card, `index.html`
~line 1853-1869) — the same surface that already holds the Day Review and `#fo-day` "one line for
tomorrow" textarea. That is the natural end-of-session moment.

**How it's built (mirrors the export bridge exactly):**
- `buildFeedback()` — sibling to `buildMissionControl()`. Pure read of live `S` + the closing-block
  inputs; returns the structured object above. No localStorage writes of its own (it reads `S`).
- `mountFeedbackCapture(host)` — sibling to `mountExportSync()`. Renders a `card` with a `details`
  summary, the quick controls, and the export button. Reuses existing classes: `card`, `kicker`,
  `sub`, `pill`, `row`, `tiny`.
- New inputs persist into `S.feedback[todayKey()]` via `saveState()` — exactly like `S.blockLogs`,
  so they survive reload. Added `feedback:{}` to `DEFAULT_S`.

**Quick controls (default sensibly → 15-second action):**
- Per-module reaction pills (`too_easy` / `on_point` / `too_hard`), default `on_point`.
- "Drop tomorrow" / "More of this" toggles per module.
- `energy` selector (low / ok / high), default ok.
- `timeTomorrow` selector (20 / 40 / 60 / 75 min), default 60.
- Everything else (blocks, owned/shaky tunes, one-line) is **derived** so the user re-enters nothing.

**Serialization & merge:** an export button
`⬇ Export feedback.jsonl line` →
`downloadBlob('feedback.jsonl', JSON.stringify(buildFeedback())+'\n', 'application/x-ndjson')`
with a toast. Framing in-card: *"append this line to `Trumpet/feedback.jsonl` for tonight's loop."*
The file downloads to the browser Downloads folder; Chris (or a helper) **appends** it to the
project's `feedback.jsonl`. No server endpoint — this device writes files only via Blob download,
identical to the mission-control export.

---

## 4. Night-agent incorporation (NOT built — Chris wires later, out of tonight's scope)

This is a **scheduled prompt** to be created via the scheduled-tasks tool. It is intentionally left
for Chris: it's a recurring external action + a steering decision, not a code increment. Spec'd here
so it's fully teed up.

**Schedule:** nightly, before the morning rebuild loop runs (e.g. ~4:50am, ahead of the existing
program-clerk at 5:20am — `[confirm: exact time / coexistence with morning rebuild]`).

**Inputs:**
- `Trumpet/feedback.jsonl` — read the **last line where `date` == yesterday** (`todayKey()-1`).
  If no line for yesterday, **no-op** (no feedback → don't bend the plan; serve curriculum as-is).
- `Trumpet/mission-control.json` — the backend brain (primary tune, rungs, weekly objectives,
  PR targets). Read-only context for *what* is being served.

**Output:** a steered plan for tomorrow. Two viable shapes (`[confirm: which Chris prefers]`):
1. **`plan-override.json`** — a small sibling file the app reads at load to override
   `CURRICULUM[dow]` block minutes / order / inclusion for that one day (cleanest; additive; the app
   would need a tiny `loadPlanOverride()` reader — a follow-on task). **Recommended.**
2. **Direct `index.html` state edit** — write tomorrow's adjustments into `S`/curriculum. Heavier,
   touches the app file nightly; riskier for an unsupervised agent. Not recommended.

**Algorithm — name the REAL levers that already exist in the app:**

1. **Module too_easy** (`moduleReactions[m]=="too_easy"` or every block in `m` advanced):
   *demote* — cut that module's block minutes (e.g. −30%, floor 5 min) so time frees up for harder work.
2. **Module too_hard** (`moduleReactions[m]=="too_hard"` or a block logged-but-not-advanced):
   *repeat/extend* — keep tomorrow's same-module block, add minutes (e.g. +25%), and carry the block
   `note` forward as the block's `why`/cue so the agent's intent is visible.
3. **`dropTomorrow` contains m:** remove that module's blocks from tomorrow's plan entirely (hard
   demote, beats the soft too_easy rule).
4. **`moreOfThis` contains m:** add minutes / a second block for that module (hard promote).
5. **`timeTomorrow`:** scale **total** block minutes to fit. Curriculum days total ~60 min
   (10+14+14+12+5+5). If `timeTomorrow=40`, scale blocks ×(40/total) preserving order, floor each at
   5 min; if `timeTomorrow=75`, distribute the surplus into the `too_hard` / `moreOfThis` modules first.
6. **`shakyTunes`:** keep the shaky tune in tomorrow's `tunes` block (don't let rotation flip away
   from it). `mission-control.json.pinnedTune` is the real lever — the agent can set/suggest a pin so
   `pickTunes()` holds the primary on the shaky tune until it's owned. (`[confirm: agent allowed to
   write S.pin / pinnedTune, or only suggest?]`)
7. **`ownedTunes`:** safe to let rotation advance past these; surface them only for spaced review.
8. **`energy=="low"`:** bias toward shorter total + keep `gym` warmup; trim `ears`/`vocab` first.
   **`energy=="high"`:** allow total to run long; push the `too_hard` module hardest.

**Real fields/levers referenced (all exist in index.html today):**
`CURRICULUM[dow].blocks[].{min,module,title,why}`, `todaysPicks()`, `pickTunes()`,
`S.pin` / `mission-control.json.pinnedTune`, `S.week['w2-'+weekIdx]` (week snapshot that locks
primary), `weeklyObjectives`, `prTargets`, `ensureWeek()`. The agent steers **minutes, inclusion,
order, and the pinned primary** — it does NOT invent new block types or fabricate metrics.

**Guardrails for the night agent (when Chris writes it):** additive only (prefer `plan-override.json`
over editing `index.html`); back up before any edit; never fabricate PRs/numbers; if feedback is
absent or malformed, no-op and serve the static curriculum.

---

## 5. Open `[confirm:]` items

- `[confirm:]` **Night-agent output shape** — `plan-override.json` (recommended) vs direct `S` edit.
  If override file: a small `loadPlanOverride()` reader in index.html is a **follow-on task**.
- `[confirm:]` **Schedule time** and coexistence with the existing morning-rebuild / program-clerk.
- `[confirm:]` **Pin authority** — may the agent write `S.pin` / `pinnedTune`, or only suggest?
- `[confirm:]` **feedback.jsonl append mechanics** — Blob download lands in Downloads; who/what
  appends it to `Trumpet/feedback.jsonl`? (Manual drop tonight; a tiny appender helper is a possible
  follow-on, but the device cannot write to the project folder directly from the browser.)
- `[confirm:]` **Multiple lines per day** — if Chris exports twice in a day, the night agent should
  take the **last** line for that `date` (latest reactions win). Documented here as the rule.
