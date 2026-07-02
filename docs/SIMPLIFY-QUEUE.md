# SIMPLIFY-QUEUE — Woodshed reduction proposals (one-in, one-out)

**Owner of the cut:** Chris approves; a separate human-approved build task makes the change.
**Owner of proposals:** the **woodshed-janitor** scheduled agent (see `WOODSHED-JANITOR-SPEC.md`).

## The contract
This file is a review queue of **simplifications only** — each entry removes code, copy, state, or a surface; nothing
here ever adds a feature. The janitor appends **exactly ONE** new proposal per nightly run (or stands down if nothing
clears the bar), so the queue stays short and reviewable. Chris acts on each entry in place via the `Chris:` line
(approve / defer-with-note / skip — the D3 standard). Resolved items stay in the file (status updated) so the janitor
never re-proposes them.

**Status values:** `queued` (awaiting Chris) · `approved` (cut authorized, not yet built) · `done` (cut shipped) ·
`skipped` (Chris declined) · `deferred` (Chris wants more context first).

## Proposal template (the janitor copies this block, increments the id)
```
### SQ-<n> · <short title>
- **Status:** queued
- **What / where:** <plain description> — grepped evidence: `<symbol/id>` at <function/id name> (~line N, verify by grep, not number).
- **Why it's safe:** <why removing it changes no live behavior / loses no feature>.
- **The single reduction:** <one concrete cut — the smallest coherent change>.
- **Risk:** <low/med> — <what to watch>.
- **Done when:** <grep-checkable acceptance test>.
- **Chris:** [ ] approve  ·  [ ] defer (note: ____)  ·  [ ] skip
```

---

## Queue

### SQ-1 · Collapse the two "written B♭" toggles into one toolbar control
- **Status:** queued
- **What / where:** One global flag, `S.writtenView`, is flipped by **two separate buttons on two different tabs** —
  `#vocab-written` (Vocab Lab) and `#tunes-written` (Tune Vault). Grepped evidence (verify by grep, not number — these
  drifted from MODE-CONFLICTS' cited 2377/2502 to their current spots):
  - Default flag: `writtenView:true` in `DEFAULT_S` (~line 1484).
  - Button 1: `id="vocab-written"` rendered ~line 2485; handler `$('#vocab-written').onclick=…{S.writtenView=!S.writtenView; saveState(); PAGES.vocab();}` ~line 2505.
  - Button 2: `id="tunes-written"` rendered ~line 2610; handler `$('#tunes-written').onclick=…{S.writtenView=!S.writtenView; saveState(); PAGES.tunes();}` ~line 2631.
  - Consumers (unchanged): `chordChartHTML` (~1518), `guideToneABC` (~1527), `renderTune` (~1386/1440/2142). The session
    inherits `S.writtenView` with **no toggle of its own**.
  - A persistent home already exists: the always-live `#toolbar` (HTML ~line 249), which already hosts the cross-cutting
    metronome/tuner/drone controls. (This is MODE-CONFLICTS conflict #14.)
- **Why it's safe:** There is exactly **one** piece of state (`S.writtenView`); the two buttons are pure duplicate
  controls for it. Both consumers already read the single flag, so moving the control to the toolbar changes *where you
  click*, not *what happens*. No feature is lost — written-B♭ vs concert toggling still works everywhere, and the
  session (which has no toggle today) gains consistent access rather than silently inheriting whatever a tab last set.
- **The single reduction:** Remove the two per-tab `written B♭` buttons (`#vocab-written`, `#tunes-written`) and their
  two onclick handlers; add **one** toggle in `#toolbar` that flips `S.writtenView`, calls `saveState()`, and
  re-renders the current page (e.g. `showPage(currentPage)` / re-invoke the active `PAGES[...]`). Net: two controls and
  two handlers become one.
- **Risk:** low — the only watch-item is that the toolbar toggle must trigger a re-render of whichever surface is
  visible (Vocab, Tunes, or a focus block) so the change is reflected immediately, the same way each old per-tab handler
  re-ran its own `PAGES.*()`.
- **Done when:** grep finds **no** `vocab-written` and **no** `tunes-written`; exactly one control writes `S.writtenView`;
  toggling it from the toolbar flips chart spelling on the Vocab tab, the Tune Vault, and inside a session block; app
  loads with no console error.
- **Chris:** [ ] approve  ·  [ ] defer (note: ____)  ·  [ ] skip

---

*Seeded from MODE-CONFLICTS #14. Confirmed NOT covered by any open board task (wood-13 = Etude dedupe; wood-14 =
dead-code sweep goPreset/#band-chorus/#ear-score — both distinct from this).*
