# Woodshed Copy Map — Spec & Wiring Plan (wood-33, M1)

**Status:** Extraction slice complete. **No `index.html` change was made tonight.**
Output is two new files only: `woodshed-copy.json` and this README.

---

## (a) Purpose

wood-33 (milestone **M1**, the foundational refactor) is "centralize the scattered
copy." Coaching copy in the Woodshed currently lives inline inside `index.html` —
40 `why:` rationales baked into the day-plan templates, plus dozens of static
`<div class="sub">` coaching lines scattered through the section renderers and the
Lore deck. That makes the copy hard to find, edit, review, or reuse, and impossible
to treat as a single source of truth.

`woodshed-copy.json` is that single source of truth: **one structured map, every
string keyed by block/exercise**, with a source-line reference for each entry so the
follow-on wiring pass is fully traceable.

This slice is **additive and read-only**: it catalogues the copy. It does **not**
change how `index.html` renders today — that's the deferred, supervised slice
(section (d) below).

---

## (b) Keying scheme (and why)

Two stable, hierarchical key families, both derived from structure already present in
the code:

1. **Day-plan backbone — `day.<weekday>.<module>.<preset>.why`**
   The 39 `why:` strings live in `CURRICULUM` (`index.html` ~L966–1011), one per
   day × block. Each block already carries `module` and `preset` fields — exactly the
   "block/exercise" keying the task asks for. The same `module/preset` pair (e.g.
   `gym/warmup`) recurs across multiple days **with different text**, so the weekday
   is included in the key to disambiguate variants without guessing.
   Examples: `day.monday.gym.warmup.why`, `day.tuesday.gym.clarke.why`,
   `day.sunday.ears.transcribe.why`.

2. **Static section coaching — `<section>.<exercise|tool>.<role>`**
   The clean, non-interpolated `<div class="sub">` coaching lines in the section
   renderers and the Lore deck. Keyed by the section/module they belong to plus the
   card/tool and an optional role suffix (`.coach`, `.howto`, named principle).
   Examples: `gym.tool.clarkePR.coach`, `vocab.matrix.coach`,
   `lore.principle4.soundFirst`, `lore.jam.onStand.coach`.

Why this shape: keys are **stable** (they track durable structure — module/preset and
section, not line numbers), **hierarchical** (group cleanly by block/section), and
**self-documenting** (you can read the key and know where it renders). Every entry
also stores `source: "index.html ~L<line>"` and a human `context` string so the wiring
pass can locate the exact site to replace.

Entry shape:
```json
"day.monday.gym.warmup.why": {
  "text": "Cichowicz first: wind before fingers. Tone is the product; everything else is packaging.",
  "source": "index.html ~L967",
  "context": "CURRICULUM / Monday / gym.warmup block — one-line 'why' coaching rationale"
}
```

**Text fidelity:** stored text is the *human-readable* string. JS source-escapes
(`week\'s`) are decoded to their literal character (`week's`); curly quotes, em-dashes
(—), and special glyphs are preserved exactly as authored. No copy was paraphrased,
trimmed, or "improved" — this is extraction, not editing.

---

## (c) Coverage summary

**71 strings extracted total.**

| Section | Key family | Count |
|---|---|---|
| Day-plan `why:` rationales | `day.<weekday>.<module>.<preset>.why` | **39** |
| Gym / Full Workout (cards + toolkit) | `gym.*` | 12 |
| Vocab (lick-of-day, 12-key matrix) | `vocab.*` | 2 |
| Tunes (jam-set rule) | `tunes.*` | 1 |
| Ears (intervals, transcription, canon, home) | `ears.*` | 4 |
| Lore deck (6 principles + 12-week arc + 6 jam-craft cards) | `lore.*` | 13 |
| **Total** | | **71** |

Day-plan `why:` breakdown by day: Mon 6, Tue 6, Wed 6, Thu 6, Fri 6, Sat 4, Sun 5 = 39.
(The Woodshed has 7 day templates; Saturday and Sunday run fewer blocks.)

**Deferred (catalogued in `_meta.deferred`, not extracted as flat text):**
- **Dynamic override `why`** (`index.html` ~L2635, `why: nb.why || ''`) — a runtime
  value in the plan-override builder; it *consumes* copy, it doesn't define any. Not a
  string to centralize.
- **Interpolated `class="sub"` strings** containing `${...}` — e.g. the interval
  side-tool (~L2039), the Saturday/pinned-tune line (~L2882), the session-log empty
  state (~L3319). These splice variables and should be wired with a tokenized format
  (placeholders), not extracted as flat text. Deferred to the wiring pass.
- **Empty-state / status placeholders** (~L2553, ~L2563, ~L3080) — borderline UI
  microcopy; safe to fold in later once the loader exists.
- **Section `<h3>` headers and button labels** — out of scope for this coaching-copy
  slice; catalogue in a later pass if desired.

---

## (d) Wiring plan (the follow-on **supervised** slice)

> This slice was NOT done tonight. It edits `index.html` and must be done supervised,
> ideally serialized against any other `index.html` work to avoid clobbering.

**1. Add a tiny COPY loader to `index.html`.** Embed or fetch `woodshed-copy.json`,
then expose a lookup:
```js
const COPY = (k) => (WOODSHED_COPY.copy[k]?.text ?? `‹missing:${k}›`);
```
Decide load strategy: simplest is to inline the JSON as a `const WOODSHED_COPY = {…}`
script block (no network, works from `file://`); alternatively `fetch()` it at boot.
Inlining is recommended given the app already runs as a single self-contained file.

**2. Replace inline copy with lookups, key by key.**
- Day-plan: change each `why:'…literal…'` to `why: COPY('day.monday.gym.warmup.why')`,
  using the `source` line in the JSON to find each site.
- Section coaching: replace the inner text of each catalogued `<div class="sub">…</div>`
  with `${COPY('<key>')}` (these sites are inside template literals already).

**3. Do it in small, verifiable batches** (e.g. the 39 `why:` first, then one section
at a time), not one giant sweep.

**Risks to manage:**
- **String-match exactness / escape handling.** The source uses JS-escaped apostrophes
  (`week\'s`) and the JSON stores the decoded form (`week's`). The loader returns the
  decoded string, which is what the DOM should show — so the *rendered* output stays
  identical, but a naive find/replace on raw source text will miss escaped sites. Use
  the `source` line references, not blind text search.
- **Special characters.** Em-dashes (—), curly quotes, and the `×`/`·`/`→` glyphs must
  survive the round-trip (UTF-8 throughout). Verify after wiring.
- **`auto`/date-driven day templates.** `CURRICULUM` is selected by weekday at runtime;
  whichever day renders must resolve its `why` from the map. Test across all 7 days
  (or stub the date) so every day's keys are exercised, not just today's.
- **Interpolated lines (deferred set).** Don't try to flatten `${…}` strings into the
  map this pass — leave them inline until a tokenized format is added.

**Recommended test — byte-identical render before/after.**
1. Before wiring, capture the rendered text of each affected card (e.g. snapshot the
   `why` lines and section `.sub` text for all 7 day templates).
2. After wiring, re-render and diff. The visible copy must be **byte-identical** — the
   refactor changes the source of the string, never the string itself.
3. Spot-check the special-character entries (the `week's` / em-dash / curly-quote ones)
   explicitly, since those are where an escape bug would surface.

---

## Verification done in this slice
- `python3 -c "import json; json.load(open('woodshed-copy.json'))"` → parses cleanly (71 entries).
- Spot-checked keys map to the exact original source strings:
  `day.monday.gym.warmup.why` (L967), `day.tuesday.gym.clarke.why` (L975),
  `day.sunday.ears.transcribe.why` (L1009, present in source in its escaped form),
  `lore.principle4.soundFirst` (L3339), `vocab.matrix.coach` (L3303).
- Coverage count in this README (71 = 39 + 32) matches the JSON entry count.
