# Woodshed Lite — Fix & Ship Plan (2026-07-03)

Action plan for your notes on the live demo. Grounded in the actual repo (`woodshed-lite/src/shell.html`, `src/mount.js`, `lite.config.js`, `votes.js`, `supabase/migrations/0001_voting.sql`) — file/line refs below are current as of today. Hand this whole doc to Claude Code as the work order; sequencing matters (§0 unblocks §4).

**Architecture reminder:** Lite is a *build target*, not a fork — `build-lite.sh` mounts the canonical engine (`../index.html`, `../charts/`) and injects `shell.html` + `mount.js` + `votes.js` + `lite.config.js` into `dist/index.html`. Edit the `src/` files and config, never `dist/` directly.

---

## 0. Pre-flight — Autumn Leaves has no chart data yet (do this first)

**You're right that it's in iReal** — I dug further and confirmed it: the source playlist (`archive/standalone-exports/Jazz 1460.html`) has a real "Autumn Leaves" entry (Kosma, key `G-` = G minor concert in iReal's own key choice). It just never made it into `charts/charts-ireal.js`, because `pyRealParser` throws `substring not found` on this specific song's bracket/repeat notation (`4T{A*...}[B*}[*]`) and `scripts/ireal_import.py` silently drops anything that fails to parse — confirmed by direct reproduction, and it explains why the file has 1459 entries instead of 1461 (Autumn Leaves + the trailing playlist-footer sentinel are the two casualties).

Downstream, `scripts/build_curated.py` pulls the curated tune list from `index.html`'s `TUNES[]` (so it does see `autumnlv`/"Autumn Leaves"), then looks up each one's `bars` by title-match against `charts-ireal.js` — finds nothing, prints `(no iReal match for curated tune: Autumn Leaves)`, and drops it. So simply re-running `build_curated.py` will **not** fix this; the gap is upstream in the importer, not a stale-regen problem.

Good news: **your F-minor concert version already exists, hand-authored**, in `index.html` `TUNES[]` (id `autumnlv`, `keyPc:5, minor:true`, `bars` array present) — the code comment there literally says "Autumn Leaves is transposed to F-minor concert per request." That's a deliberate transposition off iReal's default G minor, not a data gap, and it matches what you just confirmed (concert F minor).

**Fix (fast path, recommended):** don't chase the `pyRealParser` bug for one tune — patch `build_curated.py` so that when a curated tune has no iReal match, it falls back to that tune's own `bars` already sitting in `TUNES[]` (parse them straight out of the `index.html` literal, same way the June 28 add-12 verification already did in node) instead of silently dropping it. Then regenerate `charts-curated.js`. This also hardens the pipeline so a future `pyRealParser` hiccup on some other tune can't quietly vanish it the same way.
*(Slower alternative, not recommended for this pass: debug the `{A*...}` repeat-bracket parsing in `pyRealParser` itself and re-import — more "correct" pipeline-wise, but you'd still end up re-keying it to F minor by hand afterward anyway.)*

---

## 1. Practice Block — kill the black background

`woodshed-lite/src/shell.html` `.ptimer` (~line 514): `background:var(--ink)` (near-black `#1a150f`), white text. Swap to `var(--surface)`/`var(--paper)` with ink text, and re-check contrast on the child elements that currently assume a dark background (`.pt-lab`, `.pt-sub`, `.pt-btn.ghost` all use light-on-dark colors right now).

---

## 2. Station 1 — Warmup layout on small screens

`.warmup-grid` (~line 185) only has one breakpoint: `max-width:880px` → collapses 2 columns to 1, full stack. That's the whole problem — no real mobile design, just a column collapse.

Target layout per your spec:
- Clarke study stays the dominant panel.
- Timer, Metronome, Reps become three panels of equal height to the Clarke panel, each ~1/6 of the screen width, stacked in a column beside it (tablet/desktop).
- Metronome tempo readout: shrink font ~4x (currently `.metro .bpm` is a large display number — check its current size and cut it hard).
- Metronome slider: convert to vertical. Native `<input type=range>` vertical styling is flaky cross-browser (especially iOS Safari) — build a custom vertical fill-bar control instead of fighting `writing-mode`/`-webkit-appearance` hacks.
- Mobile: the Timer/Metronome/Reps trio moves to a horizontal row across the bottom, Clarke full-width on top. Whole station should fit one viewport (`100dvh`) if possible.
- "4 lines of Clarke" — confirm scope: `clarke-warmups-lite.js` currently only has Ex.27 + Ex.28 (2 lines). Adding 2 more exercises means transcribing them first (score-to-woodshed skill), not just a layout change.

This is a real rebuild of `.warmup-grid`/`.warmup-side`, not a CSS tweak — treat it as its own pass, verify on real devices (see checklist).

---

## 3. No sound on mobile/tablet (metronome AND backing band)

Likely cause: WebAudio gesture-unlock. `AC.get()` (`index.html` ~line 1276) lazily creates the `AudioContext` and calls `.resume()` — on iOS Safari this MUST happen synchronously inside the tap handler, with nothing `await`ed first, or the unlock silently fails and audio stays muted for the rest of the session.

**Action:**
- Trace the click chain from `warmup-play`/`jam-play` buttons to `AC.get()`. If anything async (fetch, decode, Promise) runs before the first `AC.get()`/`resume()` call, that's the bug — move the unlock to the very first synchronous line of the tap handler.
- Check whether drum/soundfont audio buffers are fetched+decoded lazily on first play vs. pre-loaded on page load. Decoding on first tap can slip outside the gesture window on mobile even if the AudioContext itself unlocked correctly. Prefer pre-loading buffers when the station scrolls into view.
- Test only on real iOS Safari + Android Chrome — desktop devtools device emulation does not reproduce the gesture-unlock restriction.

---

## 4. Station 2 tune set — swap to Autumn Leaves / Blue Bossa / Solar

`woodshed-lite/lite.config.js`, `jam.tunes` array (~lines 47–56). Requires §0 done first.

Remove the Blue Monk entry, add:
```js
{ id: 'autumnlv', label: 'Autumn Leaves', type: 'changes',
  composer: 'Kosma / Mercer', descriptor: 'F MINOR', feel: 'MEDIUM SWING',
  bpm: 160, groove: 'swing', compFeel: 'garland' },
```
Blue Bossa and Solar entries stay as-is (already at bossa/evans/160 and brushes/jamal/150 respectively — matches your spec). Flag: confirm you want a `year` field shown or omitted (Autumn Leaves' French original is 1945, the English lyric/US standard is usually dated 1947–50 — pick one or drop the year like the other changes-only tunes do inconsistently right now).

---

## 5. Station 2 layout on mobile/tablet (the "one long scroll" problem)

Same root issue as §2: `.jam-grid` (~lines 258–259) collapses to a single column under 920px — tune list, then chart card, then config all stack vertically with no height budget. That's why it scrolls instead of feeling "full screen."

Needs an actual compact mobile layout, not a breakpoint collapse:
- Condense the 3 tune tiles into a horizontal scroller or segmented control instead of 3 stacked full-width rows.
- Trim chart-card padding and the config block (see §7).
- Cap the whole station at `100dvh` on mobile with internal scroll only where truly needed (e.g. inside the chord grid if the form is long), not the whole page.

---

## 6. Chord bar overlap (the ugliest bug)

`shell.html` `.bar` CSS (~lines 304–323) + `mount.js` `renderBarHTML()` (~lines 47–59).

Current structure: `.chord` sits in the bar's normal flow, `.slash` is **absolutely positioned** bottom-right of the same `.bar` box. On narrow bars (4-per-row grid, mobile width) the chord label's own text runs into the absolutely-positioned slash marks — that's the overlap you're seeing. Multi-chord bars already get a different, better structure (`.bar-split-row` / `.bar-split-cell`, lines 328–332) — the single-chord path just never got the same treatment.

**Fix (matches what you described):** restructure every bar — single- or multi-chord — into two sibling containers:
1. A chord-name row (middle, left-justified) — one cell per chord, `flex:1` each, so a 2-chord bar just adds a second cell instead of overlapping.
2. A full-width bottom row of slash marks, one strip per chord matching its share of the row.

Unify `renderBarHTML()` so single-chord and multi-chord bars emit the same two-container markup (right now they're two different code paths — that's why the split-cell version already looks fine and the single-chord version doesn't). Use `clamp()`/container-relative font sizing so chord text autofits as the bar shrinks, same pattern already used in `.bar-split-cell .chord` (line 330).

---

## 7. Config panel height + copy trims

`shell.html` jam-right block (~lines 840–929).

- Copy fix (exact string, line ~916): `<span class="who">straight 8ths</span>` under the Bossa button → `Straight`.
- The tempo/drummer/feel config block between the tune name and the chord chart reads roughly 3 song-tiles tall right now; target ~1.5x. Concrete levers: `.seg button` padding (8px 14px → ~5px 10px), tighten `.feel` top margin (14px), `.transport`/`.transpose-row`/`.subdiv-row` vertical margins (14–16px each) — these five spacing values are most of the excess height. Cut them roughly in half and re-measure against the 3 tune tiles rather than eyeballing.
- Note: the tune list and chart card are separate grid columns (`.jam-grid`, 1fr / 1.35fr) — they don't share a height axis today. If the "1.5 tiles" comparison is meant literally (config block height vs. tune-tile stack height), that's the metric to hit; flag back if you meant something else once you see it rebuilt.

---

## 8. "Now Playing" wrong font

`.tunes-lab` (line 855, shared class with "Tonight's set") is styled `font-family:var(--osw)` (Oswald) in current `src/shell.html` — same as its sibling label, so on paper this should already match. Most likely explanation: **the deployed `dist/` has drifted from `src/`.** Per your own build notes, the sandbox's `rm -rf dist` gets blocked, so recent rebuilds patched `dist/index.html` in place rather than regenerating clean — that's exactly the kind of gap that lets an old font rule survive a source edit.

**Action:** do a real clean rebuild (delete `dist/` for real, not an in-place patch — do this from a normal shell where `rm` isn't restricted) and diff the live site's "Now playing" element against `src/shell.html` before assuming this needs a code fix at all.

---

## 9. Votes always show 0

`supabase/migrations/0001_voting.sql` + `src/votes.js` + `lite.config.js` `funnel.votes`.

The code itself is architecturally sound — RLS-locked tables, two security-definer RPCs, optimistic UI, and a deliberate silent-fallback-to-static-board on any error (`votes.js`, `.catch` blocks). That last part is exactly why this could be failing invisibly: the fallback board's seed counts are all 0, and any failure — network, auth, schema — quietly shows that same board with no visible error. Check in this order:

1. **Confirm migration 0001 actually ran** against the live Supabase project (`doavobhtmetfmugpjgrt`). A correct local `.sql` file that was never executed reproduces exactly "always 0, every browser, every time."
2. **Key format:** `lite.config.js` (line 80) uses the newer `sb_publishable_...` key format. `votes.js` (line 59) loads `@supabase/supabase-js@2` — a *floating* major-version tag off jsdelivr. If that resolves to an older 2.x minor that predates publishable-key support, every RPC call fails auth, gets swallowed by the catch, and falls back to the zero board. Pin an exact known-good version instead of floating `@2`.
3. **Open the browser console on the live site** — `votes.js` logs a specific `console.warn` on every failure path (`"Supabase not configured"` vs. `"votes offline"` vs. an RPC error). That message tells you which of (1)/(2) it is in about 10 seconds, faster than guessing.

---

## 10. Strikethrough reliability ("Six disconnected apps and files")

`.pitch-flow .strike::after` (~lines 409–410) + `.line-strike` (~lines 562–564).

Current approach draws one absolutely-positioned diagonal bar across the whole `.strike` span's bounding box. The moment the text wraps to 2+ lines — which happens differently on every viewport — the bar only crosses part of it, or floats in the wrong spot. That's the tablet/iPhone symptom exactly.

**Fix:** drop the pseudo-element bar entirely, use native `text-decoration:line-through` with `text-decoration-color:var(--brass)` and `text-decoration-thickness` (solid support incl. iOS Safari 15+). The browser draws the strike per wrapped line automatically — it can't overlap or miss a line regardless of how the text wraps.

---

## 11. Warmup carousel — 3 exercises (Clarke, Arban lip slur, Arban short etude)

New scope, added 2026-07-03: Station 1 becomes a carousel of three warmups instead of one fixed Clarke study. Left/right arrows switch the exercise; the metronome's default tempo/range and the exercise panel content update with it (rep tracker stays generic across all three unless you want per-exercise goals).

**What I found in `pipelines/arban-source/` (already indexed, per `arban-index.json`):**

- **Lip slur pick:** Part II, "Studies on Slurring or Legato," section file `sections/06-studies-on-slurring-or-legato.pdf` (printed pp. 39–57, 19 pages, 46 numbered exercises). I previewed pp. 39–41 — **Exercise 3 (printed p.39, key of F)** is the strongest fit: exactly 2 systems, simple stepwise octave slurs ascending then descending, the same "classic long-tone lip slur" shape most method books derive from Clarke/Arban. Short, unambiguous, intermediate-appropriate. (Exercises 1–2 on the same page are busier/more chromatic if you want something with more movement instead — flag which you prefer.)
- **Specialty short-etude pick:** Part I, "First Studies," section file `sections/02-first-studies.pdf` (printed pp. 11–22). Page 11 has six short 2-system etudes with fingerings already marked. **Exercise 3 or 4 (key of C)** reads as a genuine mini-etude rather than a pure long-tone drill — interval leaps instead of scalar motion, still only 2 systems (~8 bars), fits your "3–4 lines" cap exactly.
- One thing to confirm: your note said the lip slur should "go up to [unclear — possibly 'high G']." Exercise 3 above tops out around the top line of the staff, not into extreme range — good for an intermediate warmup, but say the word if you meant something that pushes higher and I'll pull a later exercise from the same section (they get progressively wider-ranging through ex. 12).

**Implementation shape:**

1. **Phase 1 (ship now, screenshots):** crop just the target exercise (not the full page) out of the two section PDFs into images — e.g. `assets/warmups/arban-slur-03.png`, `assets/warmups/arban-first-studies-03.png` — matching the existing `assets/{leadsheets,warmups,...}` convention. Drop them into the carousel as static images alongside the existing ABCJS-rendered Clarke panel.
2. **Phase 2 (later, engrave):** run both through the `score-to-woodshed` transcription pipeline (same homr OMR → ABC path used for Clarke) so all three warmups render the same way (ABCJS, consistent branded styling) instead of two screenshots next to one real engraving.
3. **Config surface:** generalize `lite.config.js`'s single `warmup: {...}` object into a `warmups: [...]` array (mirrors the `jam.tunes` pattern already used for Station 2) — each entry carries `id`, `label`, `type: 'abc' | 'image'`, `src`, `defaultBpm`, `bpmMin`, `bpmMax`, `reps`. Keeps the no-fork/config-driven convention consistent across both stations instead of introducing a one-off pattern for the carousel.
4. **Markup/JS:** add prev/next controls + a position indicator (e.g. "1 / 3") to the exercise panel header, next to the existing PD badge. On arrow click: swap the rendered content (ABCJS re-render for Clarke, straight `<img>` swap for the two Arban screenshots), and re-seed the metronome's default BPM/min/max from the active `warmups[]` entry.
5. This interacts directly with §2 (Station 1 mobile layout) — do the carousel controls and the mobile layout rework together rather than sequentially, since the exercise panel's header/chrome changes either way.

---

## Build & ship checklist

1. Confirm the two Arban exercise picks (§11) before cropping/building anything — cheap to redirect now, wasted work if I build the wrong exercise.
2. Regenerate `charts-curated.js` (§0) — unblocks §4.
3. Crop the two confirmed Arban exercises into `assets/warmups/` and wire the carousel (§11), alongside the rest of the Station 1 rework (§1–2).
4. Make the remaining `src/shell.html`, `src/mount.js`, `lite.config.js` edits (§1–2, §4, §6–7, §10, §11).
5. Fix the audio-unlock path (§3) and the vote board (§9) — these are behavior bugs, not layout, so budget separate testing time.
6. Run `./build-lite.sh` from `woodshed-lite/` as a **real clean rebuild** — delete `dist/` for real this time (not an in-place patch) so drift like §8 can't hide again.
7. `verify_public_safe.py` must pass — Autumn Leaves is changes-only (chords), and both Arban exercises are pre-1893 public domain, so all fine under the existing PD-safe rule.
8. Test matrix before calling it done — iPhone Safari (portrait), iPad Safari (portrait + landscape), Android Chrome, desktop Chrome at 3 widths. On every device: tap Start Metronome → audible click; tap jam Play → audible band; cast a vote → count increments and survives a reload; carousel arrows swap exercise + metronome default correctly.
9. Deploy `dist/` to host.
10. Re-check the live vote board from two different real browsers after deploy — this is the one bug that can look fixed locally and still fail live if the gap is Supabase-project-side (§9.1).

---

## Suggested Claude Code execution order

Sequence matters — confirm scope, then data dependencies, then layout, then the two behavior bugs, then rebuild:

1. Confirm the §11 Arban exercise picks with Chris (cheap now, wasted work later if wrong).
2. §0 (regenerate charts-curated.js)
3. §4 (swap tune list)
4. §11 (crop Arban exercises, wire carousel) together with §1, §2 (Station 1 rework — same surface)
5. §5, §6, §7, §10 (remaining CSS/markup pass — can batch together)
6. §3 (audio unlock — needs real-device testing)
7. §9 (votes — needs Supabase dashboard access, not just code)
8. §8 (verify after clean rebuild, don't fix code speculatively)
9. Build & ship checklist
