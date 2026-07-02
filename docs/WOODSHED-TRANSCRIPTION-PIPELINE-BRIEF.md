# Woodshed Transcription Pipeline — Build Brief

**Task:** wood-12 (build the sheet-music read/transcribe pipeline) → feeds wood-3 (A4 vocab licks). Milestones M2 / A4.
**Date:** 2026-06-23 · **Owner:** Chris · **Status:** scoping only — *no app code written by this brief.*
**Decision context:** Chris rejected both quick lick-entry options (6/22) and chose to BUILD a real read/transcribe pipeline so he never hand-transcribes. He **de-gated** it (must NOT block other Woodshed work) and asked: *"Scope the transcription build step-by-step as a set of tasks… test each subcomponent, iterate; start from a clean slate; write a brief outlining the first task set + check-in cadence before night agents build."* This brief is that deliverable.

---

## 1 · Objective & non-goals

**Objective.** Stand up an incremental, testable pipeline that turns a **printed page of single-line music** (PDF or photo — a Real Book page, a lead sheet, an etude line) into the Woodshed's internal notation so it renders, plays, transposes to any key, and adjusts tempo — without Chris hand-transcribing. Build it as discrete, individually-evaluated subcomponents so any supervised/night run can pick up the next task and prove it before moving on.

**Hard guardrails (from `TRANSCRIPTION-POSTMORTEM.md` — the A3 lesson, non-negotiable):**
- **Never engrave from a performance or audio.** Every approach that tried to convert real performance micro-timing into a clean staff failed (over-sustain, choppy 16ths, spurious accidentals). This pipeline reads **printed notation only** — the clean-source case. WJazzD / audio sources are out of scope for this build.
- **Never fabricate notation where a real page exists.** Read what is on the page; do not "engrave from imagination." A transcription that has not been re-rendered and visually diffed against the source is a guess (`score-to-woodshed` step 4).
- **Misreads fall back to manual, never silent.** Chris would never blind-pick option A. When the engine's confidence is low or it hits a scope limit, the pipeline **stops and surfaces the bar**, offering the manual `score-to-woodshed` crop-read-verify loop (option B). Pitch is sacred; a wrong note is worse than a missing ornament.

**Non-goals (this build):** audio/performance transcription; bulk vocabulary sourcing; multi-voice/piano grand staff; bass/alto clef; triplets; ornaments. These are either out of scope or routed to manual fallback (§6).

---

## 2 · Pipeline decomposition

Seven discrete, individually-testable subcomponents — exactly the steps Chris named. "Engine/skill" column names what does the work: **omr-engine** (`omr.py`, deterministic, eval-backed), **score-to-woodshed** (LLM crop-read-verify loop), or **new glue** (thin scripts to be written).

| # | Stage | Input | Output | Engine / skill | Scope limit that bites here |
|---|-------|-------|--------|----------------|------------------------------|
| a | **Ingest** page | PDF page # or photo file | Normalized PNG (~150 dpi, gray, deskewed/normalized) | New glue around `pdftoppm` / ImageMagick `convert` (both skills already prescribe this) | Faded scans need `--thr 180` not 140; portal page = printed page − 1 (poppler offset) |
| b | **Locate** notation region | Normalized page PNG | Bounding boxes of the staff systems on the page | omr-engine (`transcribe()` already detects systems/staff lines) for the staves; **new glue** to isolate the *region* vs. title/text/chord-symbol band | Chord symbols sit *above* the staff — omr-engine ignores them (no chord reading); page-pass layout read is an LLM/manual job |
| c | **Cut/segment** each staff line | Page PNG + system boxes | One PNG strip per system | omr-engine handles internally; `score-to-woodshed/render_strips.sh` is the manual analog | None major for single-staff; multi-staff pages must be declined to top-line only |
| d | **Measures / key / chords** | System strips | Key signature; bar boundaries; chord-symbol text | **Key:** omr-engine (eval-backed, G5/G6 green; propagates key across continuation systems). **Measures:** omr-engine bar detection. **Chords:** **not done by omr-engine** — `score-to-woodshed` LLM read, or new OCR glue | **omr-engine reads NO chord symbols and NO time signature** `[confirm: time-sig detection]`. Chords are the biggest gap — see §6 |
| e | **Pitches / durations / beats / accents / ties** | System strips (+ key from d) | `(x, pitch, dur16)` event list per system | omr-engine — the core competency (≈100% engraved pitch, ~92% accidentals, dotted-quarter 100%) | **No triplets; no tie-duration merging** (two tied notes return as two notes, not one summed value); dotted-eighth-in-beam ~66%; **accents/articulation not read** `[confirm: accents]` |
| f | **Emit internal notation** | Event list + key | ABC (omr-engine `events_to_abc`) **and** the app's native `beats[]`/`bars[]` structures | omr-engine emits ABC; **new glue** converts ABC/events → the app's `LICKS.beats` (rhythm token + semitone-offset arrays) and tune `bars[]` (concert chord arrays) | App stores two distinct shapes — see "Internal format" below; tie-merge and triplet gaps from (e) propagate here |
| g | **Render into Woodshed** | ABC + `beats`/`bars` | Live entry: playable, transposable to any key, tempo-adjustable | `score-to-woodshed` import path (append to `charts.js` / `LICKS`); app already renders ABC via abcjs and plays a generated band | Transposition: concert chords = written − 2 for the B♭ Real Book — one wrong guess makes all playback wrong |

**The app's real internal notation format (so stage f/g target the truth, not a guess):**
- **Tunes** (`index.html`, the `TUNES`-style array, e.g. line ~700+) store **`bars:[ ['Cm7'], ['Fm7','Bb7'], … ]`** — one array per bar of **concert-pitch chord symbols**. This is what the backing band plays. They carry no melody notation; melody is referenced by `page`/`soloId`.
- **Licks** (`const LICKS=[…]`, line ~570) store melody as **`beats:[{p:'<rhythm token>', n:[<semitone offsets from the I root>]}, …]`** plus **`chords:[[<beatIndex>,'ii-7'], …]`**. Rhythm tokens seen in-file: `'4'` (quarter), `'r4'` (qtr rest), `'r8'` (eighth+?), `'_tt'`/`'ttt'` (triplet group), `'ssss'` (four 16ths), `'1'`/`'2'` (whole/half). `[confirm: full rhythm-token grammar — derive from the renderer, not guessed]`
- **Imported charts** (`charts.js`, `window.USER_CHARTS`) store a full **`abc:`** string + `bars:[…]` concert chords — the `score-to-woodshed` shape. This is the lowest-friction landing zone for a transcribed *tune*; `LICKS.beats` is the landing zone for a *vocabulary lick*.

> **Note the triplet collision:** `LICKS` already contains triplet tokens (`_tt`, `ttt` — see L1), but omr-engine **cannot read triplets**. So a transcribed lick containing triplets cannot be fully produced by the engine and must route to manual fallback at stage (e). This is the single sharpest tension between the engine and the lick format.

---

## 3 · Test strategy per subcomponent

The discipline is the postmortem's core lesson made mechanical: **every stage gets a small, known-answer eval, and a human/agent confirmation checkpoint before the output is trusted.** omr-engine is already eval-backed (gates G1–G7, each with a documented pass threshold and a known failure tail) — reuse that posture for the new glue.

| Stage | Eval (known input → expected output) | Confirm checkpoint |
|-------|--------------------------------------|--------------------|
| a Ingest | A known PDF page + photo → byte-stable normalized PNG at expected dpi/dims | Visual: strip is legible, deskewed |
| b Locate | A page with N systems → N boxes, no title/text captured | Overlay boxes on page, eyeball |
| c Segment | Same page → N strips, each one staff line | Read each strip; no clipped staves |
| d Key/measures/chords | A page of known key/bar-count → exact key + bar count (reuse omr `rb_eval.py` G6: 6/6 pages). Chords: known chart → expected symbol list | Diff against the printed key sig & chord row |
| e Notes | Reuse omr gates: engraved seeds (G2/G5 13/13), accidentals (G3 ~92%), hand-drawn line (G4 22/22), dotted (G7) | **The crop-read-verify checkpoint** — re-render the events and diff bar-by-bar vs. source (the `score-to-woodshed` step-4 loop). A run that hasn't been diffed is a guess. |
| f Emit | A known event list → expected ABC **and** expected `beats[]` (round-trip golden file) | Validate ABC syntax (`verify_abc.mjs`, exit 2 = syntax error); validate `beats[]` against the app's existing lick validator (spans/note-counts) |
| g Render | Import the entry → it renders in abcjs, plays, transposes, changes tempo | Chris/agent loads the portal and confirms playback in ≥2 keys + 2 tempos |

**Rule inherited from omr-engine:** no stage's glue ships without re-running its eval on **fresh** inputs; any regression means revert and rethink, and any *new* failure must be shown to belong to a known tail class (not a silent new bug) before it's accepted.

---

## 4 · The FIRST task set (smallest end-to-end vertical slice)

"Start from a clean slate" + "smallest slice that produces real value." The realistic simplest first input is a **clean, single-staff, treble-clef line with no triplets and no ties** — the omr-engine happy path (its 100%-pitch regime). Build the thin spine a→e→f→g on that one line before touching anything harder.

**Recommended first input:** one engraved or clean hand-lettered single-line melody — e.g. a short etude line, or a Real Book *head* line known to be triplet-free and tie-free (Chris picks the page; the engine's G6 already verified Real Book key reading on his B♭ scan). Avoid dense solos.

| # | Task | Acceptance criteria |
|---|------|---------------------|
| **T1** | **Stand up ingest + isolate one staff line.** Glue `pdftoppm`/`convert` → normalized PNG; run omr-engine to detect the system; emit one clean strip. | Given the chosen page, produces a deskewed, legible single-staff PNG at the tested ~150 dpi / sp≈11.8 regime. Reproducible from a one-line command. |
| **T2** | **Read the line into events with omr-engine; verify.** Run `omr.py --json` and `--abc`; run the crop-read-verify diff against the source strip. | Pitches match the printed line 1:1 by eyeball diff; key signature correct; any rhythm uncertainty flagged by bar. No triplets/ties present (input chosen to avoid them). Meets omr's pitch-sacred bar. |
| **T3** | **Glue: events/ABC → the app's internal format.** Convert to a `LICKS.beats[]` lick (or a `charts.js` `abc:`+`bars[]` tune) and pass the app's existing validator. | Output validates (spans/note-counts; ABC syntax exit 0). Round-trip golden file: re-render the emitted notation and it matches the engine's events. |
| **T4** | **Land it in the Woodshed and prove the four properties.** Import the entry; load the portal. | Entry renders in abcjs; plays; **transposes to ≥2 keys**; **tempo adjusts**. (This is the real-value proof Chris asked for.) Chris reviews before any wider rollout. |

This slice deliberately excludes chords-over-staff, triplets, ties, and multi-staff — all of which are §6 risks routed to manual fallback or a later task.

---

## 5 · Check-in cadence (what's Chris's call, when he reviews)

- **CK-1 — after T2 (first verified read).** Show Chris the source strip beside the re-rendered events. *Decision:* does the read clear his bar? This is the go/no-go on the engine's accuracy for his real pages.
- **CK-2 — after T4 (first full vertical slice lands).** Chris loads the portal, confirms render/play/transpose/tempo. *Decision:* is the end-to-end value real enough to invest in the harder stages? This is the natural de-gated pause point.
- **CK-3 — at each scope-limit boundary.** Before building anything for **chords-over-staff, triplets, ties, or multi-staff/grand-staff**, stop and ask Chris how to handle it: **manual `score-to-woodshed` fallback** vs. **declare out-of-scope** vs. **invest in extending the engine** (the omr-engine `PLAN.md` roadmap lists tied-half recovery, dotted-eighth, triplets as open). These are explicitly Chris's calls, not an agent's.
- **CK-4 — before wiring anything into `index.html` directly.** index.html and charts.js are the live app; any write there gets Chris's sign-off first (and a `.bak` per workspace protocol). Prefer landing tunes via `charts.js` (additive `USER_CHARTS`) over editing the in-file `TUNES`/`LICKS` arrays until Chris approves the format.

**Decisions that are Chris's, made explicit:**
1. How to handle pages the engine can't read (multi-voice/grand staff, triplet-heavy solos): manual fallback vs. out-of-scope.
2. Whether a transcribed lick with triplets is worth the manual cost, or whether the lick library stays triplet-free.
3. The landing format for the first results: `LICKS.beats[]` (vocab) vs. `charts.js` tune — likely both eventually, but which first.

---

## 6 · Risks & open questions

| Risk / gap | Where it bites | Plan routes around it by… |
|------------|----------------|---------------------------|
| **No chord-symbol reading** in omr-engine | Stage d — chords sit above the staff | Read chords via `score-to-woodshed` LLM page-pass, or add OCR glue; for the first slice, pick a line where chords are simple/known or hand-entered. `[confirm: build chord-OCR glue vs. always manual]` |
| **No triplets** | Stage e — and `LICKS` already uses triplet tokens | First slice is triplet-free by selection; triplet inputs route to manual fallback (CK-3). Engine extension is a separate, later, Chris-approved task. |
| **No tie-duration merging** | Stage e/f — two tied notes return as two notes | Flag tied bars at the verify checkpoint; merge manually in stage f, or pick tie-free first input. omr `PLAN.md` lists tied-half recovery as roadmap. |
| **Dotted-eighth-in-beam ~66%; durations "close-enough"** | Stage e | Verify checkpoint catches it; pitch is the sacred bar, rhythm gets human confirm on flagged bars. |
| **Multi-voice / grand staff** | Stages b–e | Decline to top-line only (both skills already do this); Chris decides per page (CK-3). |
| **Full-tune accuracy on real Real Book melodies is UNMEASURED** | Whole pipeline | The published omr figures are per-stage (notes-only, keys, dotted), **not** whole-solo. Do not assume a whole-page read is trustworthy until the verify loop confirms it. Build a whole-line gate as part of T2. |
| **Transposition error** | Stage g | B♭ Real Book → concert = written − 2; one wrong guess breaks all playback. Make transposition explicit and confirmed in T3/T4. |

**`[confirm:]` items flagged for Chris:**
- `[confirm: time-signature detection]` — omr-engine SKILL.md documents key-sig reading but does **not** claim time-signature detection. Confirm whether bar/measure detection alone is enough or a time sig is needed for the app.
- `[confirm: accents/articulation]` — the engine reads pitch/dur/dots/rests; **accents and articulation are not in its documented scope.** Chris named "accents" in his ask; confirm these are manual-only for now.
- `[confirm: full LICKS rhythm-token grammar]` — derive the exact `p:` token set from the app's renderer before writing stage-f glue, rather than inferring from samples.
- `[confirm: chord-OCR glue vs. always-manual chords]` — biggest scope gap; Chris's call whether to build it.
- `[confirm: whole-line accuracy gate]` — no whole-tune eval exists yet; recommend building one in T2.

---

## 7 · Folds-into note

**wood-3 (A4 vocab licks) consumes this pipeline once the first slice (T1–T4) works.** The moment a clean single line reliably becomes a validated `LICKS.beats[]` entry that renders, plays, and transposes, the A4 vocabulary effort can source idiomatic lines **from trusted printed method-book pages** (Aebersold / Coker / Bergonzi — the postmortem's recommended clean sources) through this exact pipeline, instead of hand-authoring "in the style of" lines or engraving from performance. The pipeline does not pick the phrase (a human ear still does — postmortem lesson 3); it removes the hand-transcription step Chris wanted gone. Until the slice is proven, **A4 vocab and all other Woodshed work proceed independently — this build is de-gated and must not block them.**
