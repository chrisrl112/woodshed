# `plan-override.json` — Contract (wood-9)

**Status:** Reader BUILT in `index.html` (`loadPlanOverride()` + `applyPlanOverride()`). Writer
(the nightly feedback agent) is **wood-15, NOT built here**.
**Governing spec:** `FEEDBACK-LOOP-SPEC.md` §4 (night-agent incorporation) — this file is the
DECIDED output shape from §5. **Sibling conventions:** `mission-control.schema.json` (schemaVersion,
ISO `generatedAt`, ISO `date`, camelCase).
**Author:** Opus build subagent · 2026-06-14

---

## 1. Purpose

A small, optional sibling file the Woodshed app reads at load. When present **and dated for today**,
it bends **today's served plan only** — block **minutes**, **order**, **inclusion**, plus an optional
**pinned tune**. It overrides nothing else. The static `CURRICULUM[dow]` is the starting point; this
file is the day's steer.

**Hard rule:** with no `plan-override.json` present (or one dated for any other day, or malformed),
the app behaves **exactly as before** — the static curriculum is served unchanged. The reader never
throws; failures log a quiet `console.info` and no-op.

## 2. Where it lives & how it's read

- **Location:** `Projects/Trumpet/plan-override.json` — same folder as `index.html`, fetched
  relative (`fetch('plan-override.json')`).
- **When:** once, during boot (`DOMContentLoaded`), after `loadState()`, **before** the first plan
  render. The handler `await`s it so the initial Today's-6 reflects the steer.
- **Gate:** applied **only if** `date === todayKey()` (today, YYYY-MM-DD). A stale or future date is
  ignored. Absent / 404 / non-JSON / non-object → ignored.
- **Application point:** `todaysPicks()` returns a **derived copy** of the day's plan when an override
  is active. `CURRICULUM` is **never mutated**; a reload with the file removed restores the static
  plan instantly. Every consumer (Today's-6 grid, the session Runner, the gym/ears pages, the day
  log, the feedback-capture card) reads `todaysPicks().plan`, so all stay consistent.

## 3. Fields

### 3a. Top-level

| Field | Type | Required | Meaning |
|---|---|---|---|
| `schemaVersion` | string | yes | Contract version, `"1.0"`. Bump on field changes. |
| `generatedAt` | string (ISO-8601) | yes | When the night agent emitted this. `new Date().toISOString()`. |
| `date` | string (YYYY-MM-DD) | **yes** | The day this override applies to. **The gate key** — must equal `todayKey()` or the whole file is ignored. |
| `dow` | integer 0–6 | optional | Day-of-week (0=Mon), for the agent's bookkeeping. Not used for gating (date is authoritative). |
| `focus` | string | optional | Replaces the day's `focus` theme label for the steered day. Cosmetic. |
| `pinnedTune` | string \| null | optional | Tune id to pin as today's served **primary** (shaky-tune lever, §4.6). **In-memory only — NOT persisted to `S.pin`.** Honored only if the id exists in `TUNES`; else ignored. *(Pin-write authority is an open `[confirm:]` in spec §5 — this reader deliberately does not persist.)* |

Then **exactly one** plan-shaping form:

- **Replacement form** — provide `blocks` (a full steered block list). Wins outright if present & non-empty.
- **Patch form** — provide any of `setMinutes` / `dropModules` / `addBlocks` / `order` / `scaleToMinutes`. Applied in that deterministic order. (Preferred: it's compact and easy for the agent to emit.)

### 3b. Replacement form — `blocks`

Array of steered blocks for the day. Each block mirrors the existing curriculum block fields
`{min, module, title, why}` (plus optional `preset`). Unknown fields on a block are merged from the
matching static block (matched by `module`, and `title` if given) so the agent can emit minimal blocks.

| Block field | Type | Meaning |
|---|---|---|
| `module` | string | One of the real module ids: `gym` / `vocab` / `tunes` / `ears` / `today`. Required. |
| `min` | integer | Minutes. **Floored at 5.** Required (falls back to matched static `min`, else 5). |
| `title` | string | Block title. Falls back to matched static block's title, else the module id. |
| `why` | string | The cue/intent line. The agent can carry a forwarded `note` here (spec §4.2). |
| `preset` | string | Optional — the block's interactive preset (`warmup`, `ladder`, …). Inherited from the matched static block when omitted. |

### 3c. Patch form fields

| Field | Type | Lever (spec §4) | Behavior |
|---|---|---|---|
| `setMinutes` | object `{module:int}` | demote too_easy / extend too_hard (§4.1, §4.2) | Sets every block of that module to the given minutes. Floored at 5. |
| `dropModules` | array of module ids | `dropTomorrow` hard demote (§4.3) | Removes all blocks of those modules from today. |
| `addBlocks` | array `{module,title,min,why,preset?}` | `moreOfThis` hard promote (§4.4) | Appends steered blocks. `min` floored at 5. |
| `order` | array of module ids | reorder (§4, "steers … order") | Reorders blocks by module rank; modules not listed keep their relative order and trail after the listed ones. |
| `scaleToMinutes` | integer | scale to `timeTomorrow` (§4.5) | Scales **total** block minutes to fit, preserving order, flooring each block at 5. |

### 3d. Safety floors (enforced by the reader)

- Every block is floored at **5 minutes** (`MIN_FLOOR`).
- **No new block types are invented and no metrics are fabricated** — the reader only moves minutes,
  inclusion, order, and the served primary tune.
- If an instruction references a module/tune **not present today**, that instruction is **skipped
  gracefully** (e.g. `setMinutes` for an absent module is a no-op; an unknown `pinnedTune` is ignored).
- `applyPlanOverride()` is wrapped in try/catch; any internal failure returns the **static day**.

## 4. Example

A concrete, valid example lives in `plan-override.example.json` (dated 2026-06-14, patch form). It
is named `.example.json` so it is **never fetched** by the app — only a file literally named
`plan-override.json` and dated for today fires. To test live, copy the example to
`plan-override.json` and set `date` to today.

Inline example (patch form):

```json
{
  "schemaVersion": "1.0",
  "generatedAt": "2026-06-14T04:50:00.000Z",
  "date": "2026-06-14",
  "dow": 5,
  "focus": "Jam Simulation (steered)",
  "setMinutes": { "gym": 6 },
  "dropModules": ["vocab"],
  "addBlocks": [
    { "module": "tunes", "title": "Recorda Me — bridge repair", "min": 12, "why": "Carried from yesterday: bridge still shaky. Slow the ii-V to 0.5x and own it before adding speed." }
  ],
  "order": ["gym", "tunes", "ears", "today"],
  "scaleToMinutes": 40,
  "pinnedTune": "recordame"
}
```

How the reader applies the above to Saturday's static plan: gym blocks drop to 6 min each, the
`vocab` block is removed, a steered `tunes` repair block is appended (carrying the note as its `why`),
blocks reorder gym → tunes → ears → today, the whole day is then scaled to total 40 min (each block
floored at 5), and Recorda Me is held as today's served primary for the render only.

## 5. Open `[confirm:]` items (carried from spec §5)

- **Pin authority** — this reader applies `pinnedTune` in-memory only (no `S.pin` write). If Chris
  wants the night agent to *persist* a pin, that's a separate, deliberate change.
- **Patch vs replacement** — both supported; the night agent (wood-15) should pick one per day.
  Patch form is recommended (compact, diff-like).
