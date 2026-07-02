# MODE-CONFLICTS — Dashboard vs. Session, and the path to one surface

> 🛑 **SUPERSEDED (2026-06-21) — renderer target is TABS-CANONICAL (Chris, 6/13, LOCKED).**
> The canonical renderer/surface is the **tabbed Dashboard** (Chris's locked decision, 2026-06-13). The
> tabbed Dashboard owns the real component instances + state; the full-screen timed Session (`#focus`,
> `Runner` + `FocusRender`) sequences **through those same tab components** — no divergent state.
> The **session-canonical** guidance in this document — specifically **§4 ("Recommendation — collapse to
> ONE primary surface")** and **§5 ("Phased merge plan")** — is **SUPERSEDED** by
> [`WOOD8-MERGE-EXECUTION-BRIEF.md`](./WOOD8-MERGE-EXECUTION-BRIEF.md) (the tabs-canonical merge brief).
> Section numbering confirmed: §4/§5 are exactly the sections that recommend Session-canonical, so the
> §4/§5 references are accurate (no discrepancy). §3's 15-row conflict inventory is **direction-agnostic
> and still valid** (the brief re-projects it onto tabs-canonical). **This doc is retained for
> historical/diagnostic context only — do not execute §4/§5 as written.**
> (Backup before this edit: `MODE-CONFLICTS.md.bak-20260621`.)

> ⚠️ **SUPERSEDED DIRECTION (2026-06-15):** §4/§5 recommend **Session-canonical**, which Chris **OVERRODE**. The governing direction is **TABS-CANONICAL** — see [`WOOD8-MERGE-EXECUTION-BRIEF.md`](./WOOD8-MERGE-EXECUTION-BRIEF.md). §3's conflict inventory remains valid; §4/§5's recommendation does **not**. (Backup of pre-banner file: `MODE-CONFLICTS.md.bak-20260615`.)

**Board task:** wood-8 · **Type:** research/analysis only (no app code changed) · **Date:** 2026-06-13
**Source of truth:** `Projects/Trumpet/index.html` (single file, ~2860 lines). Every claim below cites a line/function.

---

## 1 · TL;DR

The app ships two surfaces over the *same* trainers: a **tabbed Dashboard** (free navigation, 7 pages) and a **full-screen Session** (`#focus`, timed blocks). The trainers are genuinely shared (one `renderTune`, one `renderLickPanel`, one `FocusRender` table reused by Gym/Ears tabs), so this is mostly *duplicate framing*, not duplicate logic — but the two surfaces can be open at once, hold divergent state, and there's real dead/orphaned routing left over from an earlier architecture.
**Recommendation: keep the Session as the spine; demote the Dashboard tabs to a thin "library/reference" shell, and delete the orphaned `goPreset` router and `band-chorus` dead refs.** Fewer surfaces, less state — exactly Chris's bias.
> **[SUPERSEDED — see WOOD8-MERGE-EXECUTION-BRIEF.md; tabs-canonical locked 6/13]** The "Session as the spine / demote the tabs" recommendation in this TL;DR is the session-canonical direction Chris **overrode** on 6/13. Governing direction is **tabs-canonical** (full detail in §4/§5 markers and the merge brief). The dead-code cleanup (`goPreset`/`band-chorus`) remains valid.

---

## 2 · The two surfaces, precisely defined

### A) Dashboard Mode (tabbed, free-nav)
- **Entry/exit:** nav buttons `.navbtn[data-page=…]` (HTML lines 299–305) → `showPage(p)` (line 1542). Wired at 1569. Initial load lands on `today` (line 2854). No exit — it's the base layer.
- **Pages:** `#page-today … #page-manifesto` (HTML 309–315). Rendered lazily via `PAGES[p]()` with a `rendered{}` cache; `today` always re-renders (line 1544).
- **Owns:** the persistent **toolbar** (metronome/tuner/drone, lines 1547–1568, always live), the **session rail** `#session-rail` (HTML 294; `renderRail()` 1700), the **Today block grid** (`#blockgrid`, built 2289–2313), and the reference pages (Tune Vault, Vocab Lab, Gym toolkit, Ears canon/lore deck, Progress, Manifesto).
- **Confirms your sketch:** ✅ `showPage` at 1542, pages at 309, rail at 294/1700, start button `#start-session` at 2247. One correction: `renderRail` lives at **1700**, not 1889/2854 (2854 is the init call).

### B) Session / Focus Mode (full-screen guided)
- **Entry:** `#start-session` (HTML 2247, wired 2314) → `Runner.start(blocks,0)`; also each Today block card (`.bc-run` 2305, card body 2311) and each rail segment (`seg.onclick` 1713) call `Runner.start(blocks,i)` to resume mid-session.
- **Engine:** `Runner` (1658–1690). `start()` adds `.open` to `#focus` and sets `body.overflow:hidden` (1661). `beginBlock()` (1663) renders the block via `FocusRender[preset]` (1673) into `#focus-stage`, runs a 1-sec timer (1677), rings a bell + auto-advances at zero (1679).
- **Exit:** `#focus-close` → `Runner.close()` (1722/1686) removes `.open`, restores scroll, logs minutes if ≥5; `finish()` (1684) on the last block logs + returns to Today.
- **Owns:** the block sequence, the timer, block completion (`S.blocksDone`, `markBlockDone` 1691), per-block logging (`renderBlockLog` 1874), and the `FocusRender` per-block renderers (1725–1870).
- **Confirms your sketch:** ✅ `#focus` HTML 320–337, engine from 1657, dispatch via `context:'focus'`.

### The overlap that creates the conflicts
The **same trainers render in both surfaces**:
| Trainer | Single definition | Used by Dashboard | Used by Session |
|---|---|---|---|
| Tune trainer | `renderTune` (2002) | Tune Vault tab → `renderTuneDetail` `{mode:'full',context:'tab'}` (2591) | `FocusRender.tuneweek/guides/memorize/solo` (1808–1811) `{context:'focus'}` |
| Lick panel | `renderLickPanel` (2407) | Vocab Lab → `renderLickDetail` (2456) | `FocusRender.lickday/review/sprint/cycle` (1802–1806) |
| Cycle machine | `renderCyclePanel` (2458) | Vocab Lab (2399) | `FocusRender.cycle` (1806) |
| Gym blocks | `FocusRender.warmup/ladder/clarke/…` | Gym tab re-invokes `FocusRender[preset]` directly (2642–2647) | native (1727–1801) |
| Ears tools | `FocusRender.intervals/transcribe` | Ears tab re-invokes them (2690–2692) | native (1830–1852) |
| Lore + Day Review | `FocusRender.lore` (1853) | Ears tab closing card (2694) | last block |

This is a **good** pattern (one source, both surfaces) — the conflicts are at the *seams*: shared mutable singletons, host-scoping edge cases, duplicate copy, and leftover routing.

---

## 3 · Conflict inventory

| # | Area/Feature | Dashboard behavior (cite) | Session behavior (cite) | The conflict / risk | Recommended winner |
|---|---|---|---|---|---|
| 1 | **Both surfaces open at once** | `showPage(p)` (1542) only toggles `.page`/`.navbtn` classes — it **never checks or closes `#focus`** | `Runner.start` sets `#focus.open` + `body.overflow:hidden` (1661); nav is still in the DOM behind it | You can `showPage('vocab')` while a session is mid-block. Focus overlays at `z-index:340` (CSS 164) so it's visually hidden, but the tab page **re-renders and its timers/band can run underneath**. No mutual exclusion. | **Session** owns the screen. `showPage` should refuse (or `Runner.close()`) while `#focus.open`. |
| 2 | **`goPreset` orphaned router** | `goPreset(p)` (2826) routes presets to **tab anchors** `#gym-warmup`, `#gym-ladder`, `#td-guides`, `#td-memo`, `#band-chorus`, `#ears-game`, `#ears-transcribe` | n/a | **Dead code.** `goPreset` is never called (grep: only its own definition). Every anchor it targets **no longer exists** in the DOM (Gym now renders via `FocusRender` 2642; tunes via `.tn-` classes; no `#td-*`/`#ears-game`). A stale "jump to tab" architecture that predates the shared-renderer model. | **Delete** `goPreset` entirely. |
| 3 | **`band-chorus` dead reference** | `highlightBar()` (2557) writes to `#band-chorus` (2559) | Tune highlight in focus uses local `.tn-pos` (2134–2136) | `#band-chorus` is **never created** anywhere in the DOM (no element has that id; `goPreset` case 'solo' 2842 also targets it). `highlightBar` is the old global highlighter; the live path is the host-scoped `hl` closure inside `renderTune` (2135). Dead/duplicate highlighter. | **Delete** `highlightBar` + `#band-chorus` refs; keep host-scoped `hl`. |
| 4 | **`Vocab` singleton shared across surfaces** | Vocab tab binds the panel to the **module-global** `Vocab` object (`renderLickDetail`→`renderLickPanel(host,Vocab)` 2456; state at 2367) | Focus lick blocks build a **fresh local `st`** each block (e.g. `{lickId,keyPc,ear}` 1802–1806) | Asymmetric state: tab edits (`Vocab.lickId`, `.ear`, `.keyPc`) persist globally; focus blocks are ephemeral. Switching tab→session→tab the Vocab tab may show a lick the user changed inside focus — or not — depending on which path wrote last. `[inferred]` low user-visible impact today but a latent surprise. | **Session-derived** picks win; tab should read the same per-block state, not a separate global. |
| 5 | **Cycle-machine writes into `Vocab.keyPc`** | Vocab cycle callback sets `Vocab.keyPc=kw` then `renderLickDetail(true)` (2399) | Focus cycle uses local `st`, callback re-renders `lp` (1806) | The dashboard cycle **mutates the shared `Vocab` singleton mid-run** (key follows the band). If a session later reuses `Vocab`, the key is whatever the cycle last left. Same root cause as #4. | Local per-context state; **Session** semantics win. |
| 6 | **`st.high` (8va) lives only in the lick panel's local `st`** | Vocab uses `Vocab` (no `.high` field unless toggled) | Focus blocks pass `{…}` without `high` | Toggling 8va (2427/2448) sets `st.high` on whichever object is bound. In tab that's the persistent `Vocab` (sticks across visits); in focus it resets each block. Divergent persistence of the **same** control. `[inferred]` | Don't persist 8va globally; reset per render. Minor. |
| 7 | **`renderTune` mode differs tab vs focus** | Tab calls `{mode:'full'}` → shows book + chart + memo + outline, **plus tab-only `extras`** (About/Videos/Listening/Fix-page, 2068–2080) and the side-by-side book layout (2097–2108) | Focus calls per-step `{mode:'learn|guides|memorize|solo'}` → one slice each, stacked layout (2109–2118), `ch` defaults to 6 vs tab's 3 (2045) | Intentional and well-built (one renderer, `isTab`/`mode` branches). The *risk* is drift: two layout branches + `extras` only in tab means a fix to the tune UI must be checked in both. Not a bug — a **maintenance seam**. | Keep unified `renderTune`; collapse Tune Vault tab to thin reference (see §4) so only the focus path is "primary." |
| 8 | **`showGuides` only in focus 'guides'** | Tab `'full'` **suppresses** skeleton/etude (comment 2011: "superseded by the Outline trainer") | Focus `'guides'` block still renders skeleton+etude (2113, `guidesInner` 2054) | The **same renderer shows guide-tone lines in the session but hides them on the tab** — a deliberate-but-inconsistent feature gate. A user comparing surfaces sees different content for "the same tune." | Pick one: if Outline supersedes guides, **cut the focus `guides` block too** (folds into wood-13). |
| 9 | **Outline vs. old Etude duplication (wood-13)** | Tab `'full'` shows **Outline trainer** (3·5·7·9·1, 2082–2094) and hides etude | Focus `'guides'` still exposes the **Etude line** (`makeGuideLine(t,true)`, 2144–2147) | Two overlapping chord-tone trainers (Outline cell vs. Etude line) coexist; the etude survives only in the focus `guides` path. This is the known **wood-13** dedupe. | **Outline wins**; retire the Etude line + the `guides` block. |
| 10 | **`FocusRender.transcribe` host-detection guard** | Ears tab renders it inside `#ears-today` (2691); the code checks `host.closest('#ears-today')` (1849) to **hide** the nested interval `<details>` | Focus renders it standalone → shows the nested interval trainer | The renderer **branches on its host's DOM id** to avoid an id/feature collision (the `#ftr-iv` interval sub-panel would double-up the Ears tab's own interval tool). Evidence of prior collision-patching; brittle (depends on a literal id string). | Keep behavior, but once Ears collapses into the session this special-case can go. |
| 11 | **`EarGame.scoreEl` is a shared global pointer** | Ears tab's interval render sets `EarGame.scoreEl=#fe-score` (1837); `renderEarGame` falls back to `$('#ear-score')` (2663) — **an id that no longer exists** in the Ears markup | Focus interval block sets the same `EarGame.scoreEl=#fe-score` (1837) | Whichever surface rendered last **owns the global score element**. Render Ears tab, then a focus interval block, then click the tab's buttons → score may write to the focus element (or a detached node). Plus `#ear-score` fallback is dead (no such id; grep). Classic shared-singleton-DOM-pointer hazard across surfaces. | **One** interval trainer instance bound to its current host; drop the global `scoreEl` pointer + dead `#ear-score`. |
| 12 | **Duplicated "today's blocks" rendering** | Today tab builds `#blockgrid` cards via `blockSnapshot` (2289–2313) — a **second renderer** that re-derives each block's preview | Session renders the real block via `FocusRender` (1673); rail (1700) is a **third** view of the same block list | The same `P.plan.blocks` is rendered **three ways** (grid snapshot, rail, focus stage), each with its own copy logic (`blockSnapshot` 2318 duplicates labels/keys the focus renderers also compute). Drift risk: a block's preview can disagree with what the session actually runs. | Keep rail + focus; **demote the grid** to a launcher list, not a parallel renderer. |
| 13 | **Conflicting "free practice" framing/copy** | Gym tab: "same gym blocks the session walks you through — same detail, here for free practice" (2604); Ears: "both trainers stay available" (2671) | Session presents the block as *the* prescription | Copy on multiple tabs asserts they mirror the session ("exact mirrors of the session" 2288, "same component the session ends on" 2693). True today, but it **markets two doors to one room** — the core UX confusion this brief exists to resolve. | One primary door (Session); reference tabs stop claiming parity. |
| 14 | **`writtenView` global toggle, three buttons** | `#vocab-written` (2377/2397), `#tunes-written` (2502/2523) each flip `S.writtenView` and full-re-render their page | Focus inherits `S.writtenView` (read in `chordChartHTML` 1518, `renderTune` 2036) | One piece of state, **two+ separate toggle buttons** on different tabs, no toggle inside the session. Toggling in a tab silently changes what the next session block shows. Consistent state, **scattered controls**. | Single global toggle (toolbar-level); remove per-tab duplicates. |
| 15 | **`Metro` ramp/gap state leaks across surfaces** | Gym tab sets `Metro.ramp` / `Metro.gapOn` (2656–2660) | Focus blocks (e.g. pyramid 2801, ladder) drive `Metro.subdiv`/start; never clear ramp/gap | `Metro` is a global; a ramp armed on the Gym tab **stays armed into a session** (no reset on `Runner.start`/`beginBlock`). `[inferred]` — `beginBlock` stops Band/Synth (1665) but not Metro ramp/gap. Possible surprise tempo ramp inside a focus block. | `Runner.beginBlock` should reset transient Metro modifiers. |

**Conflict count: 15 rows.** Of these, **#2 and #3 are pure dead code**, **#9 is wood-13**, and **#4/#5/#6/#11/#15 are shared-singleton hazards** with the same fix shape.

---

## 4 · Recommendation — collapse to ONE primary surface

> **[SUPERSEDED — see WOOD8-MERGE-EXECUTION-BRIEF.md; tabs-canonical locked 6/13]** The recommendation below makes the **Session** canonical; Chris **overrode** this on 6/13 in favor of **tabs-canonical**. Retained for historical context — do not execute.

**Winner: the Session (`Runner` + `FocusRender`) is the primary, canonical surface. The Dashboard tabs survive only as a thin reference/library layer, not as a parallel practice surface.**

### Why
- The Session already **owns the real practice flow** (timed blocks, logging, completion, rail). The tabs mostly **re-render the same `FocusRender`/`renderTune`/`renderLickPanel` components** with extra chrome (Gym 2642, Ears 2690, Vocab 2399, Tunes 2591). Cutting the parallel framing removes surfaces and state without losing any trainer.
- It matches Chris's stated bias: **fewer surfaces, less state.** The shared-singleton hazards (#4/#5/#6/#11/#15) mostly **evaporate** once each trainer has exactly one live host instead of two competing ones.
- The dead routing (#2 `goPreset`, #3 `band-chorus`, #11 `#ear-score`) is pure debt from the pre-shared-renderer era — deleting it is risk-free.

### What gets KEPT vs CUT
**KEEP**
- The whole **Session engine** (`Runner`, `FocusRender`, rail, block logging).
- The **unified component renderers** (`renderTune`, `renderLickPanel`, `renderCyclePanel`) — already the right design.
- **Reference-only** tab content that has no session equivalent: Listening Canon + Lore Deck (Ears 2675–2700), Progress page, Manifesto, the iReal/forScore exports (Tunes 2507–2519), and the **Gym toolkit** (Tempo Ramp / Gap Trainer / Clarke links, 2607–2641) as an "always-open tools" drawer.
- The **toolbar** (metronome/tuner/drone) — genuinely cross-cutting.
- **Tune Vault as a browse/library** (the 24-tune dropdown 2500 + book/iReal) so Chris can open any tune outside a session.

**CUT / DEMOTE**
- `goPreset` (#2) — delete. `highlightBar`+`#band-chorus` (#3) — delete. `#ear-score` fallback (#11) — delete.
- The **Etude line + focus `guides` block** (#8/#9, wood-13) — Outline wins.
- The **`#blockgrid` snapshot renderer** (#12) — replace with a simple launcher list that calls `Runner.start(blocks,i)` (the rail already proves this works).
- **Duplicate `written B♭` toggles** (#14) — one control.
- The **"mirror" framing copy** on Gym/Ears/Today (#13) — reword tabs as "tools," not "the session, again."

### Each conflict-row's winner (consistent resolution)
1 Session · 2 delete · 3 delete · 4 Session · 5 Session · 6 reset-per-render · 7 unified (Session primary) · 8 cut guides · 9 Outline · 10 keep then retire · 11 single-instance · 12 demote grid · 13 Session · 14 single toggle · 15 reset on beginBlock.

### Main tradeoff / risk
**Risk:** some users like free, non-timed practice (open Vocab, noodle one lick). Demoting tabs to "reference" must **not** strip the ability to *run a trainer outside the clock*. Mitigation: keep `renderTune`/`renderLickPanel` reachable from the library tabs in a no-timer mode (they already accept `context:'tab'`), so "browse + practice one thing" still works — we're removing the *parallel session framing*, not the trainers.

### Alternatives rejected
- **(a) Dashboard wins, delete Session.** Rejected: the Session is where logging, timing, streaks, and the daily plan live (`Runner.finish` 1684, `markBlockDone` 1691). Killing it guts the product's spine and the Mission-Control export bridge depends on session state.
- **(b) Keep both fully, just fix the seams.** Rejected: it leaves two marketed doors to one room (#13) and preserves every shared-singleton hazard. Lower one-time effort, permanently higher carrying cost — the opposite of Chris's "less state" bias.

---

## 5 · Phased merge plan (proposal — executes only after Chris approves §4)

> **[SUPERSEDED — see WOOD8-MERGE-EXECUTION-BRIEF.md; tabs-canonical locked 6/13]** This phased plan executes the Session-canonical direction in §4, which Chris **overrode**. The governing phased plan is in `WOOD8-MERGE-EXECUTION-BRIEF.md §4` (tabs-canonical). Retained for historical context — do not execute the plan below.

Each step is independently shippable and reversible (single-file, git-tracked). "Done when" is the acceptance check.

**Phase 0 — Dead-code sweep (zero behavior change).**
Delete `goPreset` (2826–2847), `highlightBar` + `#band-chorus` (2557–2559), and the `#ear-score` fallback (2663).
*Done when:* grep finds no `goPreset`/`band-chorus`/`ear-score`; app loads and every block still runs.
*Touches:* 2557–2559, 2663, 2826–2847.

**Phase 1 — Mutual exclusion (#1, #15).**
`showPage` early-returns (or calls `Runner.close()`) when `#focus.open`; `Runner.beginBlock` resets `Metro.ramp/gapOn/gapOff`.
*Done when:* nav clicks are inert during a session; no stray tempo ramp inside a block.
*Touches:* 1542, 1663–1665.

**Phase 2 — One state per trainer (#4, #5, #6, #11).**
Stop binding the Vocab/Ears tabs to module-global singletons (`Vocab`, `EarGame.scoreEl`); give each render its own host-scoped state, seeded from `todaysPicks()`.
*Done when:* opening a tab, running the matching focus block, returning to the tab shows no cross-contaminated key/lick/score.
*Touches:* 2367, 2399, 2456, 1837, 2663.

**Phase 3 — wood-13 dedupe (#8, #9).**
Remove the Etude line + the focus `guides` block; Outline trainer is the sole chord-tone tool. Drop `showGuides`/`guidesInner`.
*Done when:* no skeleton/etude UI anywhere; Outline renders in both tab and any remaining tune context; tune-block count in the plan updated.
*Touches:* 2011, 2054–2061, 2113, 2144–2151, 1809.

**Phase 4 — Demote the Dashboard to a library (#7, #12, #13, #14).**
Replace `#blockgrid` snapshot cards with a launcher list (reuse rail semantics); reword Gym/Ears/Today copy from "mirror of the session" to "tools/reference"; collapse the two `written B♭` toggles into one toolbar control.
*Done when:* Today shows one "Start session" + a simple block launcher; only one written-view control exists; tabs no longer claim session parity.
*Touches:* 2256–2316, 2288, 2377/2397, 2502/2523, 2604, 2671.

**Phase 5 — Verify + log.**
Full click-through of every block in-session and every reference tab; confirm export bridge (`buildMissionControl`) still serializes; handoff line.
*Done when:* no console errors (`window.onerror` 2857 silent), all blocks run, export valid.

---

## 6 · Open questions for Chris (judgment calls)

1. **[decide] Does the Session fully replace free practice, or must "open one tune/lick and noodle without a timer" survive?** My plan preserves it via library tabs; confirm that's wanted vs. a cleaner "session-only" app.
2. **[decide] Etude line — gone for good?** wood-13 assumes Outline supersedes it. Confirm you don't still want the running-8th-note etude as a separate drill (#8/#9).
3. **[decide] Should Gym's Tempo Ramp / Gap Trainer remain a free-standing toolkit drawer, or move *inside* the relevant focus blocks?** Affects whether the Gym tab survives at all (#15, §4 KEEP list).
4. **[decide] Tune Vault dropdown (browse all 24) — keep as a library, or is the weekly-rotation primary tune enough?** Determines how much of the Tunes tab remains after Phase 4.

---

*No app code was modified by this audit. This is a recommendation; the merge runs only after Chris approves the direction in §4.*
