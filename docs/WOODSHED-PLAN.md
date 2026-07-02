# WOODSHED V4 — Execution Plan
*Drafted from Chris's first full session feedback · June 10, 2026*
*STATUS: BUILT & SHIPPED as Release Candidate — same day. Decisions: Blue Note aesthetic · 2-tune mastery week · 6 blocks, harder + loop-driven. All phases A–D executed; Phase E checklist lives in the in-app changelog card. Awaiting Chris's RC pass.*

The headline: the session was fun and the skeleton works, but v3 fails on three fronts — **musical truth** (made-up exercises where your real books should be), **play density** (too much clicking, not enough blowing), and **system cohesion** (features that don't feed each other). Plus bugs. This plan fixes root causes, not symptoms.

---

## Part 1 · Root-cause diagnosis (every item you raised)

| # | What you saw | Actual root cause |
|---|---|---|
| 1 | Cichowicz on page ≠ Group A in the book | I generated a fake "flow study" instead of using your actual book. Wrong philosophy — anything that exists in your three PDFs should be **embedded page images of the real thing**, not my approximation. |
| 2 | Clarke "scale" had a wrong note + weird jump | My v3 "extended" Clarke cell introduced a melodic error ([14,16,14,12] then a dead jump to the tonic). Same philosophy failure as #1. |
| 3 | Vocab block: unclear what to do | No protocol text. The block assumed you knew the ear-first method and which keys were assigned. |
| 4 | "Hear it" plays concert pitch vs your written screen | Real transposition bug: the synth plays written-pitch MIDI at concert pitch — sounds a whole step above your horn. Fix: sound everything down 2 semitones so audio matches what your trumpet produces reading the same notation. |
| 4b | Want looping ii-V-I backing per key | Legit missing feature — the single highest-value vocab addition. |
| 5 | Ghost echo after Stop | Found it: drum/piano **reverb sends bypass the band's kill-switch bus** — scheduled hits keep feeding the reverb after stop. Symptom matches exactly (fades out "eventually"). |
| 6 | "Piano toggle deleted" | Not deleted — the mixer only exists on the Tune Vault page. Focus Mode's compact band panel never got it. You practiced in Focus Mode. |
| 7 | Recorda Me chords ≠ book | That tune was flagged "from memory, page approx" and never verified against your book (unlike the 12 core tunes). The fix is an **audit: every chart read against the actual book page render** before it ships. |
| 8 | Want guide-tone play-along notation | New feature: two generated lines per tune — Skeleton (guide tones in rhythm) and **Etude** (a composed 8th-note line that lands each guide tone on the downbeat through a full chorus), playable in sync with the band. |
| 9 | "Memorized" too easy | Checkbox theater. Rungs need dates, daily limits, and a re-verification gate before the badge. |
| 10 | Play button died | Likely downstream of #5 (audio graph left in a bad state) — plus no defensive guards. Fix the graph lifecycle + add try/catch + an audio panic-reset. |
| 11 | Ears video embed broken | YouTube has effectively killed `listType=search` embeds. Replace with **verified video IDs** (I'll resolve the canon + the 12 core tune solos via real searches) and graceful link-out fallbacks everywhere else. |
| 12 | Stay on Recorda Me? Weekly structure? | See Part 3 — proposing a 2-tune week with mastery gates. Your call on the model. |
| 13 | Only ~1/3 your usual playing volume | The deepest issue. The hour is fragmented into reading/clicking. Fix: every block becomes **loop-driven** — band/backing runs continuously, instructions collapse, and the week gets explicit "open horn" blow time. Target: ≥70% of the hour with the horn on your face. |
| 14 | Want weekly goals | New "This Week" system: auto-generated Monday targets (tune rungs, lick keys, one tempo PR, transcription bars), tracked all week, **assessed in the Saturday jam-sim**. |
| 15 | Hate the blue palette | Re-skin entirely. Direction decision is yours — three options below. |
| 16 | PRs/receipts don't connect to what you did | True. The audit (Part 4) wires every loop: drills prompt logging at the right moment → receipts only show what curriculum actually trains → weekly goals consume the same numbers. |

---

## Part 2 · Build phases

### Phase A — Correctness & audio (the trust layer)
1. **Sound-matches-horn transposition**: all lick/etude playback sounds at concert (written − 2). Pads too.
2. **Stop-ghost fix**: per-play reverb send routed through the kill bus; full audio-graph teardown on stop; try/catch guards; "reset audio" escape hatch.
3. **Focus Mode mixer**: bass/drums/piano/click controls in every band panel, settings persist.
4. **Real Cichowicz + real Clarke**: warmup and Clarke blocks embed the actual book pages inline (Group rotates daily; Clarke study pages per day). My generated notation remains only for things not in your books (pyramid, double-tongue cell) — and the Clarke cell reverts to the true No. 26 pattern as a quick-reference above the embedded page.
5. **Chord audit vs the book**: render the page for all flagged/from-memory tunes (Recorda Me, Half Nelson, Misty bridge, Ornithology, Out of Nowhere, MFV, Cherokee bridge, Stella B, TINGL A) at readable resolution, correct my data to match your edition exactly. Recorda Me ending fixed first.

### Phase B — Play density (the workload layer)
6. **Looping backing tracks in the Vocab Lab**: one button — the band vamps the lick's progression (ii-V-I, minor ii-V, blues, turnaround) in the current key, forever, at your tempo. Key advances only when you say so (or auto every N choruses — toggle).
7. **Vocab protocols**: each mode (ear-first / review / sprint) shows a tight numbered protocol + today's assigned keys highlighted on the ring.
8. **Blow-first defaults**: band choruses default high (6–8), every tune panel gets "loop until stopped," instructions collapse behind a toggle.
9. **Open Horn block**: scheduled free-improv time over the week's tune vamp — the band runs, the UI shuts up.

### Phase C — Structure & cohesion (the system layer)
10. **The 2-tune week** (pending your call): PRIMARY tune (deep work, most blocks) + SECONDARY (last week's, consolidation + Saturday set). Mastery gate: a tune doesn't rotate out of PRIMARY until rung 3+, you can pin it to stay regardless.
11. **Memorization integrity**: rungs store dates, max 2 rungs/day/tune, the badge requires rung 5 passed on two days ≥3 days apart, one-click rollback. (Your Recorda Me state: roll-back button included.)
12. **This Week card**: Monday auto-generates goals (tune rung target, lick × keys, one tempo PR + amount, transcription bars); progress bars all week; Saturday jam-sim doubles as the weekly assessment; Sunday plans the next.
13. **Guide-tone Skeleton + Etude**: generated per tune, notated, playable in sync with the band, sounding at horn pitch.
14. **PR loop closure**: ladder/Clarke/tongue/bootcamp blocks end with an inline "log it" gate; receipts page shows only curriculum drills, with staleness nudges; jam-readiness pulls from the same store.
15. **Verified listening**: real video IDs for the 14-track canon + the 12 core tune solos (resolved by actual search, tested), embedded directly; rapid-transcription block keeps the 5-minute format you liked, now with a working player; everything else links out cleanly.

### Phase D — The re-skin (after you pick a direction in the questions)
One full visual rebuild, no half-measures: type, color, texture, components. The three candidate directions are in the question I'm asking alongside this plan.

### Phase E — Verification protocol (the process fix you asked for)
- **Musical truth gate**: any notation/chart change ships only after a side-by-side render against the source (book page or engine output read back).
- **Audio QA script**: a written checklist I execute every release — play/stop/loop every engine, rapid double-clicks, mode switches mid-play, focus-mode walk of all 7 days.
- **Automated suite**: existing logic + DOM tests, extended with audio-graph lifecycle assertions.
- **RC handoff**: I ship as "release candidate" with a visible changelog card in the portal listing exactly what changed and what to test — you confirm before I call anything done.

---

## Part 3 · Recommendations on your open questions

**Recorda Me / cycling**: stay on it. Repertoire that rotates before it's owned is the old mistake this system exists to kill. Recommended model: PRIMARY + SECONDARY with mastery gates (Phase C-10) — calendar suggests, mastery decides, you can always pin.

**Workload**: your instinct is right and the diagnosis is structural — v3 optimized for *guidance* at the cost of *reps*. The fix isn't abandoning structure; it's making the structure loop so the horn never leaves your face: backing vamps, long band runs, open-horn time, collapsed instructions. If after a week it still feels light, we drop from 6 blocks to 4 longer ones.

**Scheduled task**: still unnecessary — the portal self-refreshes by date. The feedback loop stays: journal in-app → bring it here → I implement against this plan.
