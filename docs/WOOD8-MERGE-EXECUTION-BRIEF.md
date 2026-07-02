# WOOD8 — Merge Execution Brief (TABS-CANONICAL, corrected)

**Board task:** wood-8 · **Priority:** P0 · **Project:** woodshed · **Type:** research/audit slice (no app code changed) · **Date:** 2026-06-15
**Source of truth for direction:** Chris's locked wood-8 decision (quoted in §1). **Source of truth for code facts:** `Projects/Trumpet/index.html` (single file, currently ~2,944 lines). Every code claim below was re-grepped against the *live* file on 2026-06-15 (the line numbers in MODE-CONFLICTS.md are stale — the file shrank after wood-13/wood-14). Anything unverified is marked `[confirm: …]`.

---

## 1 · The contradiction this brief exists to fix

There are **two documents pointing in opposite directions**, and a build agent must not execute the wrong one.

- **MODE-CONFLICTS.md §4/§5** (dated 2026-06-13) recommends: *"Winner: the Session (`Runner` + `FocusRender`) is the primary, canonical surface. The Dashboard tabs survive only as a thin reference/library layer."* The STATUS **Key Facts** block (`status/woodshed.md`, line 8) repeats this: *"a full-screen timed Session … is the primary/canonical surface; the tabbed Dashboard … is demoted to a thin reference/library shell."*
- **Chris OVERRODE that.** His locked wood-8 decision is the governing direction:

> "NOT session-primary. Best-of-breed: keep the **DASHBOARD TABS as the canonical surface** (the override); Session/Focus mode just **SEQUENCES you THROUGH those same tabs**. Make the two surfaces **IDENTICAL** (no divergent state) and fix the dead code. The wood-14 dead-code sweep is approved either way."

And the board next_action:

> "Execute the decided merge: **dashboard TABS are canonical**; rebuild Session/Focus mode as a **guided walk THROUGH the tabs** (same components, same state — no separate session-only widgets). **Eliminate divergent/duplicated state** so both surfaces are identical."

**Therefore:** MODE-CONFLICTS.md §4/§5 and the STATUS Key Facts block now point the **wrong way**. If a build agent executes §5 as written it will demote the tabs and build the Session-primary architecture Chris explicitly rejected. **This brief supersedes §4/§5.** MODE-CONFLICTS.md §3 (the 15-row conflict inventory) is *direction-agnostic and still valid* — it is reused below, with each row's *winner* re-projected onto tabs-canonical. A SUPERSEDED banner was added to MODE-CONFLICTS.md (and the STATUS Key Facts block needs the same correction — flagged in §6; the parent owns STATUS).

---

## 2 · Target architecture (tabs-canonical)

**The Dashboard TABS own the canonical component instances and their state. Session/Focus mode is a thin SEQUENCER that drives the user *through the same tab components/state* in timed order. Session must NOT instantiate separate session-only widgets or hold separate state.**

This is the *inverse* of MODE-CONFLICTS.md §4 (which made `Runner`/`FocusRender` primary and tabs thin). The mechanism that makes it cheap is already specified in **WOODSHED-REBUILD-SPEC.md §2**: one `renderSection(host, scope, context)` per section, where `context` controls chrome only and *never* content. Vocab Lab (`renderLickPanel`, line 2525) already proves the pattern works.

### Where the parallel/duplicate instances live today (verified line numbers)

| Section | Tab renderer (canonical owner under this brief) | Focus/Session renderer (must become a thin caller) | Today/rail third view |
|---|---|---|---|
| **Tunes** | `PAGES.tunes` (2610) → `renderTuneDetail` (2708) → `renderTune(host,id,{context:'tab'})` (2045) | `FocusRender.tuneweek/guides/memorize/solo` (1745–1748) → `renderTune(host,P.tune.id,{mode,context:'focus'})` — **already the same renderer ✅**, only `mode`/`context` differ | Today `blockSnapshot` case (2436+) re-derives a preview |
| **Vocab** | `PAGES.vocab` (2486) → `renderLickDetail` (2574) → `renderLickPanel(host,**Vocab**,…)` (2525) — binds the **module-global `Vocab`** | `FocusRender.lickday/review/sprint/cycle` (1739–1744) → `renderLickPanel(host,**{fresh local st}**,…)` — builds a **new `{lickId,keyPc,ear}` object each block** | `blockSnapshot` lick cases (2453+) |
| **Cycle** | `renderCyclePanel($('#vocab-cycle-host'), …)` (2517), callback writes `Vocab.keyPc=kw` (2517) | `FocusRender.cycle` (1742–1744) → local `st`, callback re-renders `lp` | — |
| **Gym** | `PAGES.gym` (2714) re-invokes `(FocusRender[b.preset])(stage,b,P)` per block (2764) + a free-standing **Toolkit** card (Tempo Ramp / Gap Trainer / Single-Tongue / Clarke Circuit, 2724–2757) | native `FocusRender.warmup/ladder/clarke/bootcamp/pyramid` (1664–1738) | `blockSnapshot` gym cases (2441–2452) |
| **Ears** | `PAGES.ears` (2781) re-invokes `FocusRender.intervals/transcribe` (2809) + `FocusRender.lore` (2811); order = ear-block-first (2807) | native `FocusRender.intervals/transcribe/lore` (1767–1806) | — |

### What "one instance, one state, tabs own it" means per case

- **Tunes — already correct in shape.** Both surfaces call the *same* `renderTune`. The only divergence is `mode` (tab `'full'` vs focus per-step `learn/guides/memorize/solo`) and `context`. Under tabs-canonical this stays — the Session sequencer just calls `renderTune` with the day's `mode` per block, and the tab is the full view. **No instance/state duplication to remove here; keep as the reference proof.** `tuneSt(t.id)` (2050) is already a shared per-tune state store keyed by id — both surfaces read it, which is exactly the "one state" target. ✅
- **Vocab — the real divergence.** The tab binds to the module-global `Vocab`; the focus blocks build a *fresh ephemeral `st`* (1739–1744). These are two states for one lick. Target: the Session sequencer must drive the **same state object the Vocab tab owns** (seed it from `todaysPicks()` for the day's block, but read/write the *tab's* state, not a throwaway). Then "open Vocab → run the lick block → return to Vocab" shows one consistent lick/key/ear. `[confirm: exact shape of the canonical Vocab state — today it's the bare module-global `Vocab` object; the build lane should decide whether to keep `Vocab` as the single store or move to a `tuneSt`-style per-lick map.]`
- **Cycle — same root cause.** Tab cycle writes the shared `Vocab.keyPc` (2517); focus cycle writes a local `st.keyPc` (1743). Collapse to one: the cycle callback writes the canonical (tab-owned) state, and the Session sequencer reads it.
- **Gym — split into shared panels.** `PAGES.gym` already calls the same `FocusRender` panel functions the Session uses (2764), so the *panels* are shared. The duplication is in *framing* (a "today's blocks + always-open Toolkit" tab vs the native session blocks) and in transient `Metro` state (Toolkit arms `Metro.ramp`/`gapOn`, 2773–2777; session blocks never clear them). Under tabs-canonical: the Gym **tab** is the canonical surface that owns today's gym panels + the Toolkit drawer; the Session sequencer walks the user through those same panel functions. (Whether the Toolkit drawer survives at all is a Chris call — see §5.)
- **Ears — same shape as Gym.** `PAGES.ears` already re-invokes the shared `FocusRender.intervals/transcribe/lore` (2809–2811). The hazards are the shared `EarGame.scoreEl` global pointer (set in `FocusRender.intervals`, 1774) and the `host.closest('#ears-today')` DOM-id branch in `transcribe` (1786). Under tabs-canonical the **Ears tab owns the live interval/transcribe instance**; the Session sequencer reuses it rather than re-pointing the global.

**Net:** under tabs-canonical, the WOODSHED-REBUILD-SPEC `renderSection(host, scope, context)` unification is *still exactly the right mechanism* — but the **tab call site becomes the canonical owner** and `FocusRender.*` becomes the thin `context:'focus'` wrapper that reads the tab-owned scope/state, rather than the reverse.

---

## 3 · Re-projected conflict resolution table (MODE-CONFLICTS §3's 15 rows, under TABS-CANONICAL)

"Old winner" = what MODE-CONFLICTS §4 line 94 resolved (Session-primary). **FLIP?** = does tabs-canonical change the winner? Verified line numbers are live-file; `[confirm]` where I could not pin exact lines.

| # | Conflict (from §3) | Old winner (§4, Session-primary) | **New winner (TABS-CANONICAL)** | FLIP? |
|---|---|---|---|---|
| 1 | Both surfaces open at once (`showPage` 1479 never closes `#focus`; `Runner.start` 1597 opens it) | Session owns the screen; `showPage` refuses while `#focus.open` | **Mutual exclusion still required, but tabs are home base.** When the Session sequencer is mid-block, returning to a tab should *land you on that tab's canonical state* (the session was driving it), not a competing copy. Simplest: `Runner.close()` syncs state back to the tab; `showPage` may close `#focus`. The anti-divergence requirement (state is shared) makes "both open" far less dangerous than before. | **Reframed** (mechanism flips: tab is the place you return to, not a thing to lock out) |
| 2 | `goPreset` orphaned router | delete | **✅ ALREADY DONE (wood-14).** Not in live `index.html` (grep: only in `.bak-*` files). | done |
| 3 | `band-chorus` / `highlightBar` dead ref | delete `highlightBar`+`#band-chorus` | **PARTIALLY done + the doc is now WRONG.** `#band-chorus` element and its `highlightBar`-writing path are **gone (wood-14)**. But `highlightBar` (def 2675) **still exists and is LIVE** — `FocusRender.jamset` calls `highlightBar('fj',bar,ch)` (1764) to highlight `#fj-bar-*` chart bars. **Do NOT delete `highlightBar`.** §3 row #3's "delete highlightBar" is stale. | **FLIP** (was "delete"; now "keep — it's live") |
| 4 | `Vocab` singleton shared across surfaces (tab binds global `Vocab` 2525; focus builds fresh `st` 1739–1742) | Session-derived picks win; tab reads per-block state | **TAB-owned state wins; Session reads from it.** The canonical Vocab state lives with the tab; the Session sequencer drives that same object. | **FLIP** (winner moves Session→Tab) |
| 5 | Cycle writes into `Vocab.keyPc` (tab 2517) vs local `st` (focus 1743) | Local per-context; Session semantics win | **TAB-owned `keyPc` wins; the cycle writes the canonical state both surfaces read.** | **FLIP** |
| 6 | `st.high` (8va) persistence differs tab vs focus `[inferred]` | reset per render | **Reset per render (unchanged), but the persisted-if-any value lives on the tab-owned state.** `[confirm: 8va/`high` toggle — re-grep; not located at old line in live file.]` | Reframed |
| 7 | `renderTune` mode differs tab (`full`+extras) vs focus (per-step) — maintenance seam (one renderer, `isTab`/`mode` branches, 2045–2052) | Keep unified, Session primary; collapse tab to thin reference | **Keep unified; TAB `full` view is the canonical/primary one.** The Session sequencer calls the same `renderTune` per-step. No collapse of the tab — the tab is canonical. | **FLIP** (tab is primary, not demoted) |
| 8 | `showGuides` only in focus 'guides' vs tab suppresses skeleton | cut guides (folds into wood-13) | **✅ RESOLVED via wood-13.** Live code: `guides` mode now routes to the single Outline trainer (`showOutline` includes `'guides'`, 2117; comment: "legacy skeleton/etude removed, wood-13"). No skeleton/etude branch remains. The `guides` *block/preset* still exists (curriculum 967, `FocusRender.guides` 1746) but renders Outline. | done (renderer); see §4 P-TUNE for optional block-label cleanup |
| 9 | Outline vs old Etude duplication (wood-13) | Outline wins; retire Etude + guides block | **✅ DONE (wood-13).** `makeGuideLine`/`guidesInner`/skeleton gone; `makeOutlineCells` (2389) is the sole chord-tone trainer. | done |
| 10 | `FocusRender.transcribe` host-detection guard (`host.closest('#ears-today')` 1786) | keep behavior, can go once Ears collapses | **Keep for now; under tabs-canonical the Ears tab is canonical so the guard's purpose (suppress the nested interval `<details>` when rendered *inside* the Ears tab) stays meaningful.** Revisit only when the single-instance Ears refactor (row 11) lands. | Reframed |
| 11 | `EarGame.scoreEl` shared global pointer (set 1774; `#ear-score` fallback) | single instance; drop global `scoreEl` + dead `#ear-score` | **`#ear-score` fallback ✅ removed (wood-14)** — live `renderEarGame` (2780) reads only `EarGame.scoreEl`, no fallback. **Still open:** `scoreEl` remains a single global pointer the last-rendered surface owns. Under tabs-canonical: **the Ears tab owns the live interval instance**; the Session reuses it rather than re-pointing the global to a focus-only `#fe-score`. | **FLIP** (winner = tab instance) + partial done |
| 12 | Triple-rendered block list — `#blockgrid` snapshot (`blockSnapshot` 2436, grid built 2407–2431), rail (`renderRail` 1637), focus stage (1610) | demote the grid to a launcher | **Demote the grid to a launcher (UNCHANGED direction) — but the grid lives on the canonical Today tab.** `blockSnapshot` (2436) is a *parallel preview renderer*; replace with a launcher that calls `Runner.start(P.plan.blocks,i)` (the grid already wires this at 2423/2429; the rail proves it at 1650). Keep rail + focus. | Same direction, tab-framed |
| 13 | "Free practice / mirror" framing copy (Gym 2721 "same detail, here for free practice"; Ears 2788 "both trainers stay available"; Today 2406 "exact mirrors of the session") | One primary door (Session); tabs stop claiming parity | **INVERTED: the TABS are the primary door; the Session is "a timed walk through your tabs."** Reword copy so tabs read as *the* surface and the Session as the guided sequencer — not "the session, mirrored." | **FLIP** (primary door = tabs, not Session) |
| 14 | `writtenView` global toggle, ≥2 buttons (`#vocab-written` 2495/2515, `#tunes-written` 2620/2641; both flip `S.writtenView` and full-re-render; focus inherits via `chordChartHTML` 1469 / `renderTune` 2078) | single toolbar-level toggle; remove per-tab duplicates | **Single global toggle (UNCHANGED).** One control (toolbar-level), both surfaces read `S.writtenView`. Direction-agnostic. | No flip |
| 15 | `Metro` ramp/gap leaks across surfaces (Gym Toolkit sets `Metro.ramp`/`gapOn` 2773–2777; `beginBlock` 1600 stops Band/Synth 1602 but never resets Metro ramp/gap) `[inferred]` | reset on `beginBlock` | **Reset transient `Metro` modifiers on `Runner.beginBlock` (UNCHANGED).** Direction-agnostic — the sequencer should start each block from a clean metronome state regardless of which surface is canonical. | No flip |

**FLIP tally:** of 15 rows, **6 flip winner** under tabs-canonical (#3, #4, #5, #7, #11, #13) and **2 are reframed** (#1, #10; #6 minor). The §4 one-liner "1 Session · 4 Session · 5 Session · 7 Session-primary · 11 single-instance · 13 Session" is the cluster that inverts toward **tab-owned**. **5 rows are already shipped/done** (#2, #3-element, #8, #9, #11-fallback via wood-13/wood-14). The remaining live work is the **state-unification cluster (#4, #5, #11-pointer)** plus the **framing/launcher/toggle/metro cleanup (#1, #12, #13, #14, #15)**.

---

## 4 · Phased merge plan for the BUILD lane (tabs-canonical)

Each phase: single-file, git-tracked, independently shippable + reversible, with a **Done when** acceptance check and the functions/ids it touches. The already-shipped dead-code (wood-14) and etude/outline (wood-13) phases from MODE-CONFLICTS §5 are **excluded** (Phase 0 and Phase 3 there are done). Sequence stages the riskiest state-unification so it's testable in isolation.

> **Phase 0 (MODE-CONFLICTS §5) — Dead-code sweep — ✅ SHIPPED (wood-14).** `goPreset`, `#band-chorus` element + its `highlightBar` path, `#ear-score` fallback all removed (verified absent in live file). **Caveat for the build lane: `highlightBar` itself is still live (jamset, 1764) — do not delete it.**
> **Phase 3 (MODE-CONFLICTS §5) — wood-13 etude/outline dedupe — ✅ SHIPPED.** Single Outline trainer; `guides` routes to it (2117).

**Phase A — Metronome reset on block entry (#15). [lowest risk, do first]**
`Runner.beginBlock` (1600) already stops `Band`/`Synth` (1602); add a reset of transient `Metro` modifiers (`Metro.ramp=null; Metro.gapOn=0; Metro.gapOff=0;`) at block entry.
- *Done when:* arming a Tempo Ramp / Gap on the Gym Toolkit, then starting a session block, shows a clean metronome (no surprise ramp). `[confirm: Metro reset field names — live values are `Metro.ramp` (2773), `Metro.gapOn`/`Metro.gapOff` (2776–2777); confirm there are no other transient fields.]`
- *Touches:* `Runner.beginBlock` 1600–1602; field names per 2773–2777.

**Phase B — Single `writtenView` control (#14). [low risk]**
Collapse `#vocab-written` (2515) + `#tunes-written` (2641) into one toolbar-level toggle; both surfaces already read `S.writtenView` (1469, 2078). Remove the per-tab buttons.
- *Done when:* exactly one written-B♭ control exists; toggling it updates Vocab, Tunes, and any session block consistently; grep finds no `#vocab-written`/`#tunes-written`.
- *Touches:* 2495, 2515 (vocab); 2620, 2641 (tunes); a new control in the toolbar (`wireToolbar` 1484); `[confirm: toolbar markup id for the new toggle.]`

**Phase C — Vocab/Ears state unification: tabs own the instance (#4, #5, #11-pointer). [the keystone — riskiest, stage + test in isolation]**
Make the Session sequencer drive the **tab-owned** Vocab/Ears state instead of fresh per-block objects.
- Vocab: `FocusRender.lickday/review/sprint/cycle` (1739–1744) currently build `{lickId,keyPc,ear,…}` fresh. Repoint them to read/write the canonical Vocab state the tab uses (`Vocab` object today, 2525) — seed it from `todaysPicks()` for the block, but do not throw it away. Cycle callback writes the canonical `keyPc` (unify 1743 with 2517).
- Ears: stop having `FocusRender.intervals` re-point the global `EarGame.scoreEl` (1774) to a focus-only `#fe-score` when the Ears tab already owns a live instance; bind the score element to the current canonical host.
- *Done when:* open Vocab tab → run the matching session lick block → return to the Vocab tab shows **no cross-contaminated lick/key/ear**; render Ears tab interval game, run a session interval block, return — the tab's score buttons write to the tab's score element, not a detached node.
- *Touches:* 1739–1744, 1774, 2517, 2525, 2574, 2780; `[confirm: final canonical Vocab-state shape — keep `Vocab` global vs adopt a `tuneSt`-style per-lick map; this is a build-lane design choice, flag if it grows beyond one file's worth of change.]`

**Phase D — Mutual-exclusion + return-to-tab sync (#1). [medium risk; after C so state is already shared]**
With state shared (Phase C), make surface switching coherent: when `#focus` is open and the user navigates a tab, either `Runner.close()` (syncing session position/state back) or land them on the tab reflecting the session's current item. Avoid two live surfaces driving the same state simultaneously.
- *Done when:* you cannot get a tab and a session block running divergent state at once; closing the session leaves the matching tab showing where you were.
- *Touches:* `showPage` 1479–1482, `Runner.close/closeUI` 1623–1626, `renderRail` 1637.

**Phase E — Demote Today grid to a launcher + invert framing copy (#12, #13). [low-medium risk]**
Replace the `blockSnapshot`-driven `#blockgrid` cards (2407–2431, `blockSnapshot` 2436+) with a simple launcher list (reuse rail semantics — `Runner.start(P.plan.blocks,i)` is already wired at 2423/2429). Reword Gym (2721), Ears (2788), Today (2406) copy: tabs are *the* surface; the Session is "a timed walk through your tabs," not "the session, mirrored." Keep rail + focus as the live block views.
- *Done when:* Today shows one "Start session" + a lightweight block launcher (no parallel preview renderer); `blockSnapshot` is gone or reduced to a label helper; no tab claims to "mirror the session."
- *Touches:* 2406–2434 (Today grid), 2436+ (`blockSnapshot`), 2721 (Gym copy), 2788 (Ears copy).

**Phase F — Verify + log. [always last]**
Full click-through: every session block in-sequence, every canonical tab, written-toggle, metronome cleanliness, no cross-contamination. Confirm the export bridge still serializes (`[confirm: export builder name — MODE-CONFLICTS §5 cites `buildMissionControl`; re-grep, may be `mountExportSync` 2404 / a different builder in the live file]`). `window.onerror` silent. Then the one-line handoff.
- *Done when:* no console errors; all blocks run from both the launcher and the rail; tab/session render the same section DOM for the same item (the WOODSHED-REBUILD-SPEC step-5 parity check); export valid.

**Sequencing rationale:** A and B are near-zero-risk warmups. **C is the keystone and the only genuinely risky change** (it touches shared state) — it's isolated so a parity test can prove tab and session render identically *before* D wires mutual exclusion on top. D depends on C (sync only makes sense once state is shared). E is cosmetic/launcher and can ship anytime after C. F gates the merge.

---

## 5 · Open questions — genuine Chris judgment calls (do NOT answer in the build lane)

Carried forward from MODE-CONFLICTS §6, **re-framed for tabs-canonical** (under tabs-primary these mostly become "how rich is each canonical tab," not "does the tab survive"):

1. **[decide] Free, non-timed practice.** Under tabs-canonical the tabs *are* the canonical surface, so "open one tune/lick and noodle without a timer" is naturally first-class (the opposite worry from the Session-primary doc, where it was at risk). Confirm: do you want the tabs to remain fully usable as standalone practice with **no requirement to ever enter the timed Session**, or should some blocks be session-gated?
2. **[decide] Gym Toolkit drawer fate (#15, §2 Gym).** The free-standing Toolkit (Tempo Ramp / Gap Trainer / Single-Tongue / Clarke Circuit, 2724–2757) is the main source of the `Metro` leak. Keep it as an always-open drawer on the canonical Gym tab, or fold those tools *into* the relevant blocks? (Phase A neutralizes the leak either way; this is about surface, not safety.)
3. **[decide] Tune Vault library scope.** The Tunes tab is canonical; how much library lives on it — the full 24-tune dropdown (`renderTuneGrid` 2665) + iReal/forScore exports as a browse-all, or trim toward the weekly-rotation primary tune? Determines how much of `PAGES.tunes` stays.
4. **[decide] Ears & Lore tab composition.** With the Ears tab canonical, confirm the canon table + lore deck + Day-Review closing block all stay on it (they have no Session-only equivalent), and whether the interval trainer stays a co-equal tool or a side `<details>` (the `transcribe` guard at 1786 currently hides it inside the Ears tab).
5. **[decide] STATUS Key Facts correction.** The STATUS Key Facts block (`status/woodshed.md` line 8) still says "Session = primary/canonical." It needs to flip to tabs-canonical. The parent owns the board/STATUS — flagging so it's corrected and no future agent re-reads the stale "Session-canonical" as governing.

---

## 6 · What's done vs what remains

- **DONE (this brief = the wood-8 research/audit slice):** corrected the direction to tabs-canonical, quoted the governing decision, re-projected all 15 conflict rows (6 flipped, 2 reframed, 5 already-shipped), verified every reused code citation against the *live* `index.html`, produced an ordered, reversible, single-file phased plan, and surfaced Chris's open calls. Added a SUPERSEDED banner to MODE-CONFLICTS.md (after backing it up to `.bak-20260615`).
- **REMAINS (BUILD lane, later run):** execute Phases A–F above against `index.html`. The keystone is **Phase C** (state unification). Nothing in this brief edits application code.
- **REMAINS (parent/board):** flip the STATUS Key Facts "Session = canonical" line to tabs-canonical (§5 item 5).

---

*No application code was modified by this audit. This brief governs the wood-8 merge direction and supersedes MODE-CONFLICTS.md §4/§5.*
