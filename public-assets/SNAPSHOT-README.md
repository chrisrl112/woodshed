# public-assets/ — public read-only progress snapshot (wood-43 / M3)

This documents the **data** sibling of the page-image bundle (`render_pages.py` /
`page-manifest.json`). Where that bundle ships the exact method-book pages as
images, this ships **Chris's real practice progress** as a clean, public,
**read-only** JSON the live Woodshed site loads to show streak / week / tunes /
PRs / weekly-objective progress — with **nothing private leaked**.

It is the "his real progress shown READ-ONLY" half of the v2 public POC. The
public site is ephemeral (visitors save nothing); only Chris's progress is shown,
and only through this published snapshot.

## Files (all new, additive)

- **`snapshot.schema.json`** — draft-07 JSON Schema; the stable PUBLIC contract.
  Documents every included field's source and, in its `$omitted` block, exactly
  what is intentionally excluded and why.
- **`render_snapshot.py`** — stdlib-only generator. Projects the practice brain
  into the public snapshot, validates its own output, writes the artifacts.
- **`snapshot.json`** — the live artifact the site loads (the generated output;
  in production this reflects the live export — see Pipeline).
- **`snapshot.example.json`** — the committed, **illustrative** reference output,
  produced by running the generator off `mission-control.example.json`. Its
  `__comment__` banner and `source.illustrative: true` flag mark it as NOT live
  data.

## Privacy / read-only policy

The snapshot is a **whitelist projection**: `render_snapshot.py` reads named
public fields only, never the whole upstream object, so a new private field added
upstream cannot silently flow through. The generator's `validate()` also runs a
forbidden-key sweep as defense in depth.

### Included (PUBLIC progress)

| Field | What it is |
|---|---|
| `schemaVersion`, `generatedAt` | Contract version + when the snapshot was generated. |
| `source.{input,exportedAt,illustrative}` | Provenance: which input was projected, the upstream export time, and whether this is the illustrative fallback. |
| `streak`, `lastDay` | Consecutive-day count and the last counting date. |
| `week.{index,displayNumber,focus}` | Week number and the day's curriculum focus theme. |
| `primaryTune`, `rotation` | This week's primary tune id and the rotation pool (ids). |
| `tunes[id].{title,rungStatus,memorized,verified,isPrimary}` | Per-tune progress: rung COUNT (0-5), memorized + verified booleans, primary flag. |
| `weeklyObjectives[].{label,current,target,met}` + `weeklyObjectivesSummary.{met,total}` | Weekly contract progress and a roll-up badge. |
| `prTargets[id].{best,goal,lastLogged,pctToGoal}` | PR ladders: best vs goal bpm, last-logged date, derived % to goal. |

### Intentionally OMITTED (and why)

These never appear in the snapshot (also catalogued in `snapshot.schema.json`
`$omitted`):

- **`tunes[].rungDates`** (raw 5-element array of the calendar date each rung was
  cleared) — reduced to `rungStatus` (count). *Precise per-rung dates expose a
  fine-grained activity calendar with no public value.*
- **`tunes[].verifiedDate`** — boolean-ized to `verified`. *Same activity-calendar
  concern; a yes/no badge is enough.*
- **`pinnedTune` / `tunes[].pinned`** — *internal steering control, not progress.*
- **`reviewTunes` / `reviewSchedule`** (review lick ids, exam text) — *internal
  curriculum mechanics.*
- **`monthlyObjectives`** — *flagged `[confirm:]` upstream and may carry free-text
  steering prose; not stable public progress.*
- **`appStateKey`** — *localStorage key / identifier detail.*
- **Any journal / lore / notes / per-block log free-text / feedback / device id /
  file path** — *the core privacy line. None of these exist on the
  mission-control object by construction, but they are called out explicitly so a
  future upstream addition can't leak.*

## Pipeline (input -> output)

```
mission-control.json  (live export, written by woodshed_server.py /save-brain)
        |  (preferred input when present)
        v
   render_snapshot.py  --project named public fields only, validate-->  snapshot.json
        ^
        |  (fallback when no live export is on disk — the normal case today)
mission-control.example.json  --> snapshot.json + snapshot.example.json
```

- In **production**, the app's Export-Sync card POSTs the running browser state
  (localStorage `woodshed_v1`, the object `S`) to `woodshed_server.py`, whose
  `/save-brain` route writes `mission-control.json` (see wood-18). That live file
  is the generator's input.
- On disk **today** there is no live export (live numbers live only in the
  browser), so the generator falls back to `mission-control.example.json`. The
  output is therefore the **illustrative** `snapshot.example.json` — clearly
  labeled, never mistaken for live data.

## How to regenerate

```bash
cd "Projects/Trumpet"
python3 public-assets/render_snapshot.py
```

- stdlib only — no pip installs.
- **Reproducible / idempotent**: `generatedAt` is anchored to the input's own
  `generatedAt` (not a fresh wall-clock), so re-running produces byte-identical
  output. (`--generated-at` overrides if needed.)
- The script **validates** its output against `snapshot.schema.json` before
  writing (required keys, core types, per-tune required keys, forbidden-key
  sweep). It exits non-zero on any violation, so a bad projection never ships.

## How the future hub embed (wood-46/47/48) should consume it

- Fetch **`snapshot.json`** only — it is the single, stable public contract.
  Never read `mission-control.json` or the browser state directly.
- **Guard on `schemaVersion`** before rendering; if it is higher than the embed
  was built for, degrade gracefully rather than mis-rendering.
- **Honor `source.illustrative`**: when `true`, label the display as a sample /
  demo (the data is representative shape, not Chris's live numbers).
- Suggested surfaces map 1:1 to fields: streak chip (`streak`/`lastDay`), week
  banner (`week`), tune cards (`tunes` — rung count, memorized/verified badges),
  PR bars (`prTargets.pctToGoal`), and a goals badge
  (`weeklyObjectivesSummary` -> "M of N goals met").
- Treat the snapshot as **read-only**: the embed displays it; it never writes back.

## `[confirm:]` items

- If a future live `mission-control.json` lacks a `generatedAt`, the generator
  writes `generatedAt: "[confirm: input had no generatedAt timestamp]"` rather
  than fabricating a timestamp — surface that for Chris to resolve the upstream
  export.

## Guardrails honored

- `index.html` and `charts.js` were **not** touched (read-only; another task owns
  index.html).
- Purely **additive**: only new files created under `public-assets/`.
- No live numbers invented — the example output is a deterministic projection of
  `mission-control.example.json`, which is itself illustrative.
- No external/irreversible actions.
