# Woodshed Feedback Agent — the WRITER half of the loop (wood-15, M5)

**Status:** Built, tested, NOT scheduled. Additive only — writes one file (`plan-override.json`),
touches nothing else. Awaiting Chris's manual approval to go live.
**Author:** Opus build subagent · 2026-06-25

---

## What it does

The Woodshed practice loop has three parts. Two already shipped (wood-9):

1. **Capture** (in `index.html`) — the end-of-session card exports a `feedback.jsonl` line:
   how today actually *felt* (per-module reactions, drop/more flags, energy, time tomorrow,
   shaky tunes, forwardable block notes).
2. **Reader** (in `index.html`) — `loadPlanOverride()` + `applyPlanOverride()` read an optional
   sibling `plan-override.json` at boot and bend **today's served plan only** (minutes, inclusion,
   order, pinned tune). It floors every block at 5 min, ignores unknown modules/tunes gracefully,
   and gates the whole file on `date === todayKey()`.

This script is **the missing middle (the writer):** overnight it reads *yesterday's* feedback line
plus the read-only mission-control brain and emits a patch-form `plan-override.json` dated for the
upcoming day, conforming exactly to `plan-override.schema.md`. It performs **no external or
irreversible action** — it only writes that one JSON file.

If there's no feedback for yesterday, or the feedback is neutral, it writes nothing and the app
serves the static curriculum unchanged (the reader's date gate also discards any stale override).

---

## The §4 lever → reader-field mapping

Every lever uses ONLY fields the reader supports. Source: `FEEDBACK-LOOP-SPEC.md` §4 and
`plan-override.schema.md` §3c.

| Feedback signal (spec §4) | Emitted reader field | Rule applied |
|---|---|---|
| `dropTomorrow` contains module | `dropModules` | Hard demote; removes the module. Beats `too_easy`. |
| `moreOfThis` contains module | `addBlocks` (one promote block) | Second pass for that module; `min` = the module's baseline. |
| module `too_easy` (explicit, or inferred when every logged block advanced) and NOT dropped/promoted | `setMinutes[m] = max(5, round(baseline*0.7))` | Demote ~30%. |
| module `too_hard` (explicit, or inferred when a block is logged-but-not-advanced) **with** a forwardable block note | `addBlocks` (one repair block, `why` = "Carried from yesterday: <note>", `min` = round(baseline*1.25)) | Repeat/extend + carry the note forward; intent visible (§4.2). No `setMinutes` for that module. |
| module `too_hard` **without** a note | `setMinutes[m] = round(baseline*1.25)` | Extend ~25% (the no-note fallback). |
| `timeTomorrow` present and != 60 | `scaleToMinutes = timeTomorrow` | Reader does the scaling math (§4.5). |
| `energy == "low"` and no explicit `timeTomorrow` | `scaleToMinutes = 45` | Trim the day. |
| `energy == "low"` | `order` puts `gym` first | Keep the warmup, demote the rest (§4.8). |
| `energy == "high"` | (no trim) | Allow the day to run long. |
| `shakyTunes[0]` | `pinnedTune` (pass-through) | Reader validates against `TUNES`; unknown ids ignored (§4.6). |
| `too_hard` + `moreOfThis` modules | `order` (those modules ranked first) | Reflects priority; energy-low forces gym first. |
| top-level | `schemaVersion:"1.0"`, `generatedAt` (now, ISO-8601), `date` (the steered day), `dow` (0=Mon), `focus` ("<feedback.focus> (steered)") | Bookkeeping + cosmetic. |

Levers are emitted **only when they carry a signal**, so the patch stays compact and diff-like.
`order` is only emitted when it actually differs from the observed block order.

### The baseline-minutes choice (documented decision)

The reader floors at 5 min and curriculum days total ~60 min, but **this script never parses
`index.html`** (per the guardrails). So **per-module baseline minutes are derived from
yesterday's observed `blocks[].min` in the feedback line** — sum the module's block minutes.
If a module has no logged blocks in the line, the baseline falls back to **10 min**. This keeps
every emitted minute value source-grounded (it reflects what was actually served yesterday)
without reading the app file, and the reader's own 5-min floor + `scaleToMinutes` rebalancing
provide the final safety net. No metric is ever fabricated.

### Other documented choices / assumptions

- **`mission-control.json` is read-only context.** It is loaded if present (optional; the agent
  runs feedback-only without it) but no field is currently fabricated or derived from it into the
  override. It is accepted now so a future revision can use rungs/objectives to refine steering
  without a CLI change.
- **Neutral = NO-OP.** All `on_point`, energy `ok`, `timeTomorrow` 60/absent, no drop/more/shaky →
  the script writes nothing and says so. It never writes a no-op override.
- **Inference is a fallback** (spec §2a): explicit `moduleReactions` always win; inference fills
  gaps only when a module has clear advance/no-advance evidence.
- **Multiple lines per day → last wins** (spec §5): the script reads the *last* line whose `date`
  matches `today-1`.
- **Fail-soft everywhere:** malformed JSON lines are skipped; a bad `--today`, unreadable file, or
  any internal error prints a message and exits 0 with **no write** — mirroring the reader's
  "never break the day" ethos.
- **`dow`** uses Python's `date.weekday()` (0=Mon..6=Sun), matching the spec convention. The reader
  treats `dow` as cosmetic bookkeeping; gating is by `date` only.

---

## CLI

```
python3 woodshed_feedback_agent.py [options]

  --feedback PATH          feedback.jsonl  (default: next to this script)
  --mission-control PATH   mission-control.json  (default: next to this script; OPTIONAL)
  --out PATH               output  (default: plan-override.json next to this script)
  --today YYYY-MM-DD       the day being STEERED (default: system local date).
                           The feedback join key is today-1.
  --dry-run                print the override JSON to stdout, write nothing.
```

stdlib only — no `pip install`, no network.

### Dry-run command + expected output

Using the shipped fixture (`feedback.example.jsonl`, whose first line is dated 2026-06-13), steer
the next day:

```
python3 woodshed_feedback_agent.py \
  --feedback feedback.example.jsonl \
  --mission-control mission-control.example.json \
  --today 2026-06-14 --dry-run
```

Expected (a valid patch-form override; `generatedAt` will reflect run time):

```json
{
  "schemaVersion": "1.0",
  "generatedAt": "2026-06-25T23:32:33.000Z",
  "date": "2026-06-14",
  "dow": 6,
  "focus": "Jam Simulation (steered)",
  "dropModules": ["gym"],
  "addBlocks": [
    { "module": "tunes", "title": "Tune — extra pass", "min": 12, "why": "More of this (flagged yesterday): second pass to consolidate." },
    { "module": "tunes", "title": "Tune — repair & extend", "min": 15, "why": "Carried from yesterday: bridge still shaky" }
  ],
  "scaleToMinutes": 40,
  "pinnedTune": "recordame"
}
```

(gym is dropped → its `too_easy` is suppressed; `tunes` gets both a `moreOfThis` promote block and
a `too_hard` repair block carrying the note; `timeTomorrow:40` → `scaleToMinutes`; `shakyTunes[0]`
→ `pinnedTune`.)

No-op example (no line for the join date):

```
python3 woodshed_feedback_agent.py --feedback feedback.example.jsonl --today 2026-06-19 --dry-run
# -> no feedback for 2026-06-18; serving static curriculum   (exit 0, no write)
```

---

## TO GO LIVE (Chris approves)

**This agent is NOT scheduled and writes ONLY `plan-override.json`.** It performs no external or
irreversible action. To activate the loop, Chris confirms the open items below, then registers it
as a nightly task.

### Register via the schedule skill (only after approval)

Schedule a nightly run shortly before the morning plan render, e.g.:

```
cd /Users/chrisliquin/Documents/Claude/Projects/Trumpet
python3 woodshed_feedback_agent.py
```

(defaults resolve `feedback.jsonl`, `mission-control.json`, and `plan-override.json` next to the
script; `--today` defaults to the system date, so the nightly run steers *that* day from the
prior day's line). Use the `schedule` skill / scheduled-tasks tool to create the recurring task —
**do this only when Chris approves**; this subagent deliberately did not register anything.

### Open `[confirm:]` items (from spec §5) — resolve before going live

1. **Schedule time / coexistence.** Pick the nightly run time and confirm it lands *before* the
   morning plan render and does not collide with the existing morning-rebuild loop or the 5:20am
   program-clerk. Spec suggests ~4:50am.
2. **Pin-write authority.** The reader applies `pinnedTune` **in-memory only** (it does NOT persist
   to `S.pin`). This agent only *emits* a `pinnedTune` suggestion in the override; it never writes
   app state. If Chris wants the pin persisted, that's a separate, deliberate change.
3. **`feedback.jsonl` append mechanics.** The capture surface downloads a line to the browser
   Downloads folder; *something* must append it to `Trumpet/feedback.jsonl` for this agent to read.
   Today that append is manual. A tiny appender helper is a possible follow-on task.
4. **Multiple lines per day.** Confirmed rule, implemented: the **last** line for the join date
   wins (latest reactions).

---

## Files

- `woodshed_feedback_agent.py` — the writer (this tool).
- `feedback.example.jsonl` — a 2-line NDJSON test fixture (line 1: rich signal dated 2026-06-13;
  line 2: neutral dated 2026-06-14). Intentionally named `.example.jsonl`, **not** `feedback.jsonl`
  — no real feedback data exists yet.
- `WOODSHED-FEEDBACK-AGENT-README.md` — this file.
