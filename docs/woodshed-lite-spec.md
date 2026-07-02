# Woodshed Lite — Build Spec

**Owner:** Chris
**Status:** Spec v1 (scaffold landed Jun 29, 2026)
**Purpose:** The public, hosted demo that runs the M0 → M3 validation funnel — *without* forking the Woodshed you keep building.
**Companion docs:** [`woodshed-validation-gameplan.md`](woodshed-validation-gameplan.md) (the 13-week funnel) · [`woodshed-M0-M2-execution-plan.md`](woodshed-M0-M2-execution-plan.md) (what's on the site, week-by-week).
**Lives at:** `woodshed-lite/` (project) · this spec in `docs/`.

---

## 1. What Lite is — in one breath

A single-scroll public page: a **hook** that names the pain (your practice is scattered across six tabs), then **two live stations** that prove the fix — a **Warmup** (real PD exercise + metronome + rep tracker) and a **Jam** (PD lead sheet + changes + a band that sounds great, with tempo/feel/style toggles) — then a **funnel** (waitlist, vote board, founder rail, socials).

It is **not** the full Woodshed. It's the 3 best wow-moments, one screen, no login. Everything that doesn't serve *show the consolidation / activate in 30s / capture the hand-raise* is cut.

The wedge, stated the same way everywhere: **playing trumpet is the hard part — the Woodshed makes everything around it effortless.** One tab, press start, warmup → jam → done. We concede ~80% of iReal's jam engine and win on *workflow and consistency*, not voicing count.

---

## 2. The real problem this spec solves: no fork, no drift

You want to keep building the full Woodshed *and* host a Lite version, **without maintaining two codebases or doing version control gymnastics.** A naive "copy index.html, strip it down" creates exactly the drift you're avoiding: every engine improvement (comping, drums, the reel studio) would have to be hand-ported, and the two would silently diverge.

**The decision (locked): Shared engine + thin Lite shell.**

```
                       ONE SOURCE OF TRUTH
   ┌─────────────────────────────────────────────────────────┐
   │  index.html        the full app (engine lives inside it)  │
   │  charts/           chart + drum data (shared)             │
   │  vendor/           abcjs, pdf.js, qrcode (shared)         │
   │  assets/           PD warmups, drum audio (shared subset) │
   └─────────────────────────────────────────────────────────┘
              │  build-lite.sh extracts + filters
              ▼
   ┌─────────────────────────────────────────────────────────┐
   │  woodshed-lite/                                           │
   │   index.html       landing chrome ONLY (hero/funnel)     │
   │   lite.config.js   which tunes/warmup + funnel IDs       │
   │   src/mount.js     mounts the shared engine in 2 slots   │
   │   build-lite.sh →  dist/  (the static deploy bundle)     │
   └─────────────────────────────────────────────────────────┘
```

**The contract that guarantees no drift:**

1. **Lite never re-implements the engine.** Band, comping, drums, metronome, and chart rendering have exactly one home (the canonical Woodshed). Lite *mounts* them; it doesn't copy them.
2. **The only Lite-specific code is marketing chrome** — hero, pitch, footer, funnel embeds — which genuinely *shouldn't* live in the practice app anyway (you already stripped origin-story / aspirational copy out of the app UI per V4.2). So this split is clean by design, not a compromise.
3. **The musical content Lite shows is a filter, not a copy.** `lite.config.js` is an allowlist of tune/warmup IDs that already exist in `charts/`. Add a tune to the Woodshed → it's available to Lite by ID. Lite shows a curated few; the data has one source.
4. **Lite is a build target, not a branch.** You never hand-edit the engine in two places. You change the Woodshed, re-run `build-lite.sh`, redeploy. The build re-extracts from canonical every time.

**What you maintain by hand, forever:** the landing copy and the ~6-line config (which 3–4 tunes, which warmup, funnel embed IDs). That's it. The 387KB of engine you keep improving flows to Lite automatically on rebuild.

---

## 3. The engine boundary (what `build-lite.sh` extracts)

The engine is currently inline in `index.html` (one ~4,100-line `<script>`). These are the self-contained, app-state-free blocks Lite needs. The build extracts these (plus the vendor libs and the filtered chart data) and nothing else:

| Block | Where (index.html, approx) | Role in Lite |
|---|---|---|
| `AC` | ~L1272 | AudioContext wrapper + shared reverb. Foundation for all audio. |
| `Metro` | ~L1432 | Metronome (tap tempo, start/stop, swing, subdiv). **Warmup station.** |
| `DrumLoop` | ~L1332 | Real-drum per-tune loop player (tempo-follow). **Jam station drums.** |
| `compBar` / `CompFeel` / `COMP_FEELS` / `compOptions` | ~L1721–1755 | Comping engine + Evans/Garland/Jamal feel presets. **Jam "feel" toggle.** |
| `Band` | ~L1755 | The rolling-scheduler backing band (bass + comp + drums). **Jam PLAY.** |
| `makeVamp` | ~L1930 | Loop generator. |
| `compileLick` | ~L722 | Lick/line compiler (needed by makeVamp). |
| chart render (`renderUserCharts` + the `.chordchart`/`.ccbar` host-scoped renderer) | ~L3858 | Renders ABC notation + the moving chord playhead. **Both stations' notation.** |

**Two extraction strategies — recommendation: start pragmatic, migrate clean.**

- **v1 (ship M0 fast) — marker-delimited extraction.** Wrap each block above in `/*<wsl:engine>*/ … /*</wsl:engine>*/` comment markers in `index.html` (a one-time, ~10-marker edit that doesn't change app behavior). `build-lite.sh` greps the marked spans and concatenates them into `dist/engine.js`. Single source of truth = the marked spans; Lite is regenerated, never hand-edited. **Lowest refactor risk; you can ship this week.**
- **v2 (debt paydown, do it gradually) — real modules.** Move the marked blocks into an `engine/` folder of plain `<script>` files (mirroring how `charts/` is already external) that *both* `index.html` and Lite load. The monolith shrinks over time; Lite and the app literally share files. Migrate one block per quiet week; the marker build keeps working until the last block moves.

Either way the no-fork contract holds. v1 gets you live; v2 is the clean end-state.

> **⚠️ The one real spike (do it Day 1, before anything else):** confirm the extracted engine **boots and plays without the full app's state** (`S`, `todaysPicks`, curriculum, localStorage schema). Band/Metro/DrumLoop/comp are Web-Audio-pure and should lift cleanly; the **chart renderer is the risk** — verify it renders an ABC chart + moving playhead when handed a bare `{abc, bars, bpm, style}` with no app globals. If it has hidden deps on `S`, that's the only refactor the v1 build needs. This mirrors the M0 plan's "does the band play in a purely static deploy" spike — **same risk, resolve both in one Day-1 session.**

---

## 4. Page spec

Single scroll = the shape of a practice session, top to bottom. The structure itself sells the consolidation.

```
┌──────────────────────────────────────────────────────────┐
│ 1. HERO — "Your whole practice session. One tab."          │
│    • 8–12s muted autoplay loop (you + overlay, from Reels)  │
│    • Headline + subhead + ONE CTA: ▶ Start the session      │
│    • CTA jumps to the JAM station (the wow first, A.5)      │
├──────────────────────────────────────────────────────────┤
│ 2. STATION 1 — WARMUP                                       │
│    • One re-engraved PD exercise (Clarke Technical Study II)│
│    • Inline metronome (tap tempo, start/stop)              │
│    • Simple rep check-off (the "tracker")                  │
│    • Microcopy: "This is where every session starts."      │
├──────────────────────────────────────────────────────────┤
│ 3. STATION 2 — JAM (the wow)                               │
│    • Tune picker: 1 PD lead sheet + 2 changes-only         │
│    • Big PLAY → band runs it, chord playhead moves         │
│    • Tempo slider + count-in                               │
│    • Feel toggle (Evans / Garland / Jamal) + style + drums │
├──────────────────────────────────────────────────────────┤
│ 4. THE PITCH — one line                                   │
│    • "Six tabs, three devices → one surface."             │
├──────────────────────────────────────────────────────────┤
│ 5. THE ASK — funnel                                       │
│    • Waitlist (one email field) + value microcopy          │
│    • Vote board (Canny/Featurebase, 6–8 seeded)           │
│    • Founder rail (stub now; charge in Phase 2/M3)        │
├──────────────────────────────────────────────────────────┤
│ 6. FOOTER — who's building this + ALL socials             │
└──────────────────────────────────────────────────────────┘
```

**The 30-second activation path (design the default state for this):**

1. Land → hero loop autoplays muted, captioned.
2. Hero CTA **jumps straight to the Jam station**, pre-cued to **Blue Monk, medium tempo**, one obvious PLAY.
3. One PLAY → band comes in, playhead moves. *That's the wow.* (Feel + tempo right there for discovery.)
4. *Then* they scroll up and find the Warmup already sitting there → the "wait, it's all in one place" realization. **The wow earns the consolidation insight.**

Every decision before the band plays costs M2 activation. Default station, default tune, default tempo, one button.

**Aesthetic:** inherit the Woodshed's Blue Note record-sleeve look (warm paper `#f2ecdf`, ink `#1a150f`, one hot orange `#e84e10`, Archivo Black display, hard offset shadows). The landing chrome should feel like the same world as the app — premium, intentional, a little swagger, not overdesigned.

---

## 5. The Lite content set (PD-safe — the hard guardrail)

The one rule that governs everything (verified Jun 2026; your `verify_public_safe.py` gate already enforces the core of it):

- **Chord changes only (no melody) → safe for ANY tune,** including copyrighted standards. (iReal's legal basis.)
- **Full lead sheet (melody + chords) → ONLY public-domain tunes** (published ≤1930) that you engrave yourself.
- **Audio → always your own band / your own playing.** Never a famous recording.

**Ship-minimum set (a complete session):**

| Slot | Tune | Legal basis | Why |
|---|---|---|---|
| Warmup | **Clarke Technical Study II** | PD (1912), re-engraved by you | Most-recognized trumpet warmup — instant r/trumpet credibility. |
| PD lead sheet | **On the Sunny Side of the Street** (1930) | Full melody + chords, you engrave | Recognizable, singable; proves you can ship a *real* chart legally. |
| Changes-only | **Blue Monk** | Chords only | Universal blues; band grooves obviously. **Default cued tune.** |
| Changes-only | **So What** | Chords only | Sparse modal changes = cleanest playhead demo. |

**Stretch:** add **I Got Rhythm** (1930, PD) as a 2nd lead sheet — rhythm changes = max utility signal.

**The one genuine content build task:** engrave the 1–2 PD lead sheets via the `score-to-woodshed` skill → verified ABC → `charts/`. Budget into Week 1. Everything else already exists in your data.

---

## 6. The funnel (hosted embeds, no backend)

| Piece | Tool | Notes |
|---|---|---|
| Email capture | Tally / ConvertKit / Beehiiv embed | One field: email. ConvertKit/Beehiiv if you'll email the list (you will — M2 depends on it). |
| Vote board | Canny (free) / Featurebase | Public upvotes; seed 6–8 features; doubles as roadmap + content. |
| Founder rail | Stripe Payment Link / Lemon Squeezy / Gumroad | **Stub now, charge at M3.** "First 30 founding members: $3/mo locked for life + name on the wall." Test a one-time $20–30 founder pass against the sub. |

All three are `<script>`/iframe embeds → work on a static host, no server. IDs live in `lite.config.js` so swapping providers is a one-line change.

**Seed the vote board (don't ship it blank):** more tunes · **build-your-own session** *(the consolidation probe — watch if this rises)* · transpose toggle (Bb/Eb/C) · loop-a-section · more warmups · slow-down trainer · save streak/log · mobile app.

**Analytics — instrument these exact events** (Plausible or GA4; you can't run the ladder blind): `page_view` (+UTM) · `demo_play` *(M2 numerator)* · `metronome_start` · `feel_toggle`/`tempo_change` · `waitlist_submit` *(M1)* · `vote_cast` *(M2)* · outbound TikTok click. UTM-tag every shared link so you know *which channel converts*.

---

## 7. Ready-to-use copy

**Hero**
> **Headline:** *Your whole practice session. One tab.*
> **Subhead:** Warmup, lead sheets, and a real backing band — in one free, no-login surface. Stop juggling a PDF, a metronome app, and a YouTube tab. Press play and practice. Built by a trumpet player, for the woodshed.
> **CTA:** ▶ Start the session

*Alt (band-forward):* "Practice jazz with a band that actually shows up."
*Alt (POV/edge):* "Six tabs, three devices, one messy practice session. I built the fix."

**Waitlist microcopy**
> **Get early access — and a vote on what I build next.**
> I'm building this in the open. Drop your email for the next release, and tell me what to build on the board below.
> *No spam. Just the occasional "here's what's new."*

**Footer POV**
> Built by Chris — SVP by day, learning to actually play jazz by night. Woodshedding in public, one tune at a time.
> → [TikTok] · [Instagram] · [YouTube] · [the rest of your socials]

---

## 8. Build & deploy

**`build-lite.sh` pipeline (one command, repeatable):**

1. **Extract** the marked engine spans from `index.html` → `dist/engine.js`.
2. **Filter** `charts/` to the `lite.config.js` allowlist → `dist/charts.lite.js` (only the PD-safe tunes Lite shows).
3. **Copy** the shared vendor libs + the PD warmup/lead-sheet assets + drum audio for the chosen tunes → `dist/`.
4. **Assemble** `dist/index.html` = the landing shell + `<script>` tags for engine + filtered charts + `mount.js`.
5. **Gate:** run `./publish.sh` (→ `public-assets/ci_check.py` → `verify_public_safe.py`). **Gate failure = hard stop, no deploy.** Extend the gate's allowlist to cover the `dist/` bundle (flag any melody-bearing notation whose tune isn't on the PD allowlist).
6. Output a clean static `dist/` ready to drag-and-drop.

**Hosting:** Cloudflare Pages or Netlify (free, static, custom domain + HTTPS in minutes). Deploy stays your manual step — the gate certifies, it never publishes.
**Domain:** grab something clean (`thewoodshed.app` / `woodshed.fm` / `playthewoodshed.com`).

> **De-risk Day 1 (the M0 spike, same as the engine spike above):** confirm the band plays in a *purely static* deploy with **no `woodshed_server.py` running** — open `dist/` from a dumb static server with Python off. The audio is client-side, so it *should*. If anything only works through the local server, that's the one real build task. This is the single biggest technical risk in the whole plan.

---

## 9. Risks & honest tradeoffs

- **Chart renderer hidden state-deps** *(highest technical risk).* If notation rendering secretly needs app `S`, the v1 build needs a small refactor to pass chart data explicitly. Resolve in the Day-1 spike before building anything else.
- **Static-audio assumption.** The whole Lite premise is "no server." Confirmed only by the Day-1 static-deploy test, not assumed.
- **Marker maintenance.** The `/*<wsl:engine>*/` markers add a tiny tax to engine edits (keep them around the right spans). Cheap, and the v2 module migration removes them entirely.
- **Scope creep.** Resist porting more of the Woodshed into Lite. Lite is 3 wow-moments + a funnel. The reach ceiling — not the product — is the real bottleneck (per the gameplan). Most effort goes to top-of-funnel, not polishing Lite.
- **Copyright.** Never ship Real Book / source PDFs or post-1930 melody. The gate is the backstop; the `lite.config.js` allowlist is the front-stop.

---

## 10. Folder & retention

```
Trumpet/
├── docs/
│   └── woodshed-lite-spec.md        ← this file (all specs live in docs/)
└── woodshed-lite/                    ← the Lite project (one new root folder)
    ├── README.md                     # the no-fork contract + build/deploy steps
    ├── index.html                    # landing shell (hero/funnel chrome) — stub
    ├── lite.config.js                # tune/warmup allowlist + funnel IDs + copy knobs
    ├── build-lite.sh                 # extract + filter + assemble + gate — stub
    ├── src/
    │   ├── landing.css               # marketing chrome styles — stub
    │   └── mount.js                  # mounts shared engine into the 2 station slots — stub
    └── dist/                         # build output — regenerated, not hand-edited
```

**Retention rules:** spec doc in `docs/` (consistent with every other brief). One new root folder, `woodshed-lite/`, sibling to `pipelines/` and `charts/` — it must sit at root to reference `../index.html`, `../charts/`, `../vendor/` by relative path at build time. `dist/` is a build artifact (treat as disposable; never hand-edit). No engine code is copied into `woodshed-lite/` — only chrome, config, and the build script.

---

## 11. Milestone tie-in

This spec delivers **M0** from the validation gameplan: *demo live + instrumented.* The exit check, unchanged:

> Open the URL on your phone → CTA → hear the band; scroll up → metronome ticks on the warmup. An email lands in your list. A vote registers. Analytics fire. **All five green = M0, advance to the M1 content push (50 emails).**

The only thing that matters in July is **50 emails**. Lite exists to earn them.
