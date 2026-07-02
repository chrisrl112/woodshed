# THE WOODSHED — Visual & Layout Redesign Brief

**For:** Claude Code
**File in scope:** `index.html` (single self-contained file — all CSS/JS inline)
**Type of work:** Re-skin + responsive/layout overhaul. **Not** a rebuild.
**Reference docs:** `Design/Woodshed Overlay - Developer Handover.md` and `Design/Woodshed Overlay v2 (standalone).html` (the desert/mountains/pine "one tall world" scene + Blue Note language).

---

## 0. The one-line mandate

The app already has every puzzle piece and a *hint* of the right aesthetic. Your job is to **take the concept all the way there** — turn the "hint of a vintage record-label / old-newspaper vibe" into a fully realized, cohesive, modern-feeling app that makes someone go *"oh, shit."* It should feel like it has **been here forever** — an artifact, not a template — while behaving like a 2026 web app.

Two non-negotiables before anything else:

1. **Do not break the app.** The tuner, metronome, drone, BPM clock, session rail, Vocab Lab, Tune Vault, Gym blocks, transcription, Reel Studio, Config, and all keyboard/audio wiring must keep working exactly as they do now. This is a styling and layout pass over working machinery — preserve all IDs, classes the JS depends on, and behavior. When in doubt, wrap/restyle rather than rip out.
2. **Do not touch the color story.** The palette stays *exactly* as-is (see §3). The orange, the ink black, the paper/canvas beige are sacred. You are changing **style, layout, type, density, and motion** — not hue.

---

## 1. Three influences, fused

The design language is the intersection of three things. Hold all three at once:

| Influence | What it contributes |
|---|---|
| **1960s Blue Note record sleeve** (Reid Miles) | The hot-orange / ink / paper color blocking, hard edges, confident type, the "designed object" feel. Already partly present — push it. |
| **Old newspaper / broadsheet** *(the #1 inspiration)* | The **layout grammar**: multi-column composition, rules and hairlines between sections, condensed display type for headers, dense-but-elegant information packing, "above the fold" thinking. Content should read like a beautifully set vintage broadsheet — *the Woodshed Daily*. |
| **The Reel Overlay scene** (`Design/` handover) | A living **desert world** — mountains, a giant pine, a woodcutter, metronome road — used as ambient, low-key background atmosphere behind the app. Engaging, alive, but **never distracting** from the content. |

The synthesis: **an old newspaper, printed on warm paper, in Blue Note ink and orange, sitting in a quiet desert world that subtly breathes to the tempo.**

---

## 2. What's wrong today (the problems to solve)

1. **It's not viewport-aware.** Everything is locked to `max-width:1240px; margin:0 auto`. On a large monitor that leaves big dead margins; on a laptop it feels cramped and forces scrolling just to navigate the main page. The layout must **respond to the actual browser** — fill big screens intelligently, stay comfortable and fit-to-screen on laptops.
2. **The aesthetic is only hinted at.** The Blue Note bones are there but timid. It needs to commit — full newspaper composition, real type hierarchy, real texture and confidence.
3. **Pages scroll too much; width is wasted.** A tab like The Gym stacks everything in one narrow column — "Today's prescription," then the full toolkit, then the music, then notes — so you scroll, scroll, scroll. It should **use horizontal width** and group related things side-by-side so far more fits above the fold.
4. **Controls feel like generic web widgets** in places. The elegant pattern (bold + underlined text → click → inline disclosure) should be the standard everywhere; clunky `<select>` boxes and default form chrome should be styled out.

---

## 3. Color — LOCKED. Do not change these.

Use the existing tokens verbatim (from `:root` in `index.html`):

```
--bg:    #f2ecdf   (paper / canvas — page background)
--surface:#faf6ec  --surface2:#efe7d6  --surface3:#e5dac3
--paper: #fffdf4   (brightest card paper)
--ink / --cream: #1a150f  (ink black — text, rules, silhouettes)
--brass: #e84e10   (the hot orange — THE accent, use it boldly)
--brass-hi:#c23c07  --brass-dim:#f0824f
--line:  #d6c9af   --line2:#b3a486  (hairlines / rules)
--muted: #5d5343   --faint:#968a72
```

Scene earth tones (for the background world only — already defined in the handover):
mountains `#DBCFB6` far / `#AE9468` near; dune `#E4D8C0` / `#CBB994`; pine foliage `#34402E`; trunk `#4A3826`. All warm — never introduce new cool colors into the scene.

You may add **tints/opacities of these existing colors** and a subtle paper grain/texture, but introduce **no new hues**.

---

## 4. Typography — commit to the newspaper

Fonts are already loaded: **Archivo Black** (`--disp`), **Oswald**, **Inter** (`--ui`), **JetBrains Mono** (`--mono`).

Make type do real work:
- **Mastheads / section headers:** Archivo Black or Oswald, uppercase, tight tracking, large — like a broadsheet nameplate and section heads ("THE GYM," "VOCAB LAB"). Consider a hairline rule + small-caps kicker above each, newspaper-style ("● TODAY'S EDITION · TUESDAY").
- **Body / labels:** Inter for UI, but lean into newspaper conventions — thin ink **rules between sections**, hairline column dividers, small-caps labels, drop-cap or oversized lead where it earns it.
- **Data (BPM, tuner, timers, chord cells):** JetBrains Mono — keep the "instrument readout" feel.
- It's fine to evaluate one tasteful **condensed serif or slab** *for editorial flourishes only* (datelines, pull-quotes, the "newspaper" texture) **if** it can be added via the existing Google Fonts link and doesn't fight the Blue Note feel. Optional — only if it elevates. Sans + mono alone can carry it.

The "old newspaper font feel" the user wants = condensed, confident, ink-on-paper, slightly editorial. Not literally Old English blackletter — that's too costume. Think mid-century broadsheet, not 1800s.

---

## 5. The frozen header (title row + activities row)

The header is a fixed, frozen masthead that does **not** scroll; only page content scrolls beneath it. Two stacked rows:

**Row 1 — The Masthead / instrument bar** (`#tb-row`, `#tb-panels`):
- `THE WOODSHED` wordmark as a real masthead (ink "THE" + orange "WOODSHED"), with the editorial orange rule running off the right edge.
- The tools — tuner, tempo/BPM, metronome, drone, written-B♭ toggle — styled as **brass instrument-panel readouts** set into the masthead, not loose buttons. Think the control strip of a vintage mixing console rendered in Blue Note ink/orange.

**Row 2 — The Day's Activities** (the nav `#nav` + `#session-rail`):
- The page tabs (Today / The Gym / Vocab Lab / Tune Vault / Ears & Lore / Progress / Manifesto / Config) as a **newspaper section index** — like the section navigation across the top of a broadsheet. Active tab clearly "inked."
- The session rail reads like the day's running order.

This whole header block is `position: sticky/fixed`, framed below by a heavy ink rule (the masthead/body break), and the content region scrolls under it. Make the frozen header **compact** so it doesn't eat the laptop viewport — vertical economy here is critical to fixing the "everything scrolls" problem.

---

## 6. Viewport-awareness (fix the responsiveness)

This is a top priority, not a polish item.

- **Kill the rigid `max-width:1240px` centered column** as the universal container. Replace with a **fluid layout** that responds to the real viewport: comfortable reading measures on content, but use the available width on large screens instead of dumping it into dead margins.
- Use a responsive system: CSS Grid for page composition, `clamp()` for fluid type and spacing, container queries / sensible breakpoints so the **same page reflows** from large desktop → laptop → tablet gracefully.
- **Laptop target:** the primary view of each page should *fit the screen* with minimal scrolling — the header is compact, and content is arranged in columns so the important stuff is above the fold.
- **Large-monitor target:** fill the space with a multi-column broadsheet composition rather than a skinny centered strip surrounded by margin. Margins should feel like intentional newspaper gutters, not emptiness.
- Respect `dvh`/`svh` for the frozen-header + scroll-area math so mobile browser chrome doesn't break it.

---

## 7. Page composition — think in newspaper columns

Apply to every page; **The Gym is the worked example** because it's the worst offender today.

Current Gym (bad): one narrow column — "Today's prescription" → "the full toolkit" → music → notes, all stacked, endless scroll.

Target Gym (good), on desktop:
- A **multi-column broadsheet grid**. The **sheet music / notation lives in a primary column on the left** (the lead story), sized to fit fully on screen.
- The **"pills" — scale/exercise chips (going up the scales, etc.) — flow into a column on the right** (the sidebar), grouped and scannable, instead of pushing the music down the page.
- "Today's Prescription" reads as the **lead headline + standfirst**; the "Full Toolkit" is the rest of the front page, not a separate scroll region.
- Notes / secondary material become a lower band or a narrower column — present, but not forcing three screens of scroll.
- The grid **collapses to a single readable column on narrow viewports** automatically.

Generalize this: every page is a **front page** — a clear lead, supporting columns, rules between sections, dense but elegant. Group related controls and content spatially so the user's eye (and the scroll) does less work.

---

## 8. The interaction pattern — bold-underline disclosures everywhere

The user specifically loves the existing pattern on the main page: a control that is just **bold + underlined text**, and clicking it reveals an **inline disclosure/dropdown** — elegant, typographic, no clunky boxed `<select>`.

- Make this the **house style** for options, pickers, and toggles across all pages.
- Replace default-chrome `<select>` / boxy dropdowns with this inline, typographic disclosure pattern wherever feasible (it reads like clickable newspaper text that expands).
- Buttons that remain should look like **letterpress / stamped** elements consistent with the Blue Note bones already in CSS (the hard `box-shadow:Npx Npx 0 var(--ink)` offset blocks are good — keep and systematize that vocabulary).
- Keep it all keyboard-accessible and preserve existing handlers.

---

## 9. The background world (incorporate the desert scene)

Bring the **`Design/` reel-overlay scene into the app itself** as ambient atmosphere — this is what makes it feel alive and "been here forever."

- A subtle, **low-contrast desert world lives behind the content**: the mountain range, the giant pine, dunes, maybe the woodcutter and the metronome "road," drawn in the warm scene earth-tones (§3) at low prominence so the newspaper content always sits clearly on top.
- **Interactive & engaging, but NOT distracting** — this is the explicit constraint. Default to quiet. Options to honor that intent:
  - Tie gentle motion to the **existing tempo/metronome clock** that's already in the app (the handover doc, §1–2, explains the beat→bar→phrase clock and which elements move on the beat). When the metronome runs, the pine can give the faintest shudder, the metronome road can pulse — *barely perceptible*, never animating under text the user is reading.
  - Parallax/ambient drift (birds, blowing sand) on slow free loops, off in the periphery / margins only.
  - When the metronome is **off**, the scene is essentially still — a printed illustration on the page.
- Implementation should match the handover's approach: **flat vector** (`clip-path` silhouettes, CSS, no photos/gradients/glows), recolorable, no external libraries. Reuse what's already proven in `Design/Woodshed Overlay v2 (standalone).html`.
- Respect `prefers-reduced-motion` — freeze the scene to a static illustration for those users.
- The scene should live **in the gutters / margins and behind low-density bands**, not under dense reading columns. On big monitors, the previously-dead margin space is the perfect home for the mountains and pine — that's how filling the viewport and adding the world solve each other.

---

## 10. Motion & feel

- Snappy, **spring/letterpress** micro-interactions (the existing `translate` + hard-shadow button press is the right instinct — systematize it).
- Transitions between tabs should feel like **turning a page**, not a generic fade — subtle, fast, tasteful.
- Everything tempo-reactive must read as *intentional and locked to the clock*, never random twitching.
- Restraint is the whole game: **pop where it counts** (the orange, a chord lighting up, a header), quiet everywhere else.

---

## 11. Hard constraints / guardrails

- Single self-contained `index.html`; all CSS/JS inline; **Google Fonts only**, no other external libs/CDNs for the redesign.
- **Preserve every element ID, data-attribute, and JS-referenced class** the app logic uses (`#tb-row`, `#nav`, `#page-*`, `#session-rail`, `.navbtn`, `.ccbar`, tuner/metro/drone IDs, etc.). Restyle; don't rename out from under the JS.
- Keep the existing color tokens; add only tints/opacities of them.
- Don't regress accessibility: keyboard nav, focus states, contrast, `prefers-reduced-motion`.
- Performance: the background scene must not cost meaningful CPU when idle; pause scene animation when the tab/metronome is inactive (the handover already notes browsers pause hidden-tab CSS — lean on that).
- **Back up before editing** (the repo convention is timestamped `index.html.bak-*`); work in passes, keep the app runnable after each pass.

---

## 12. Suggested order of work (passes)

1. **Foundation:** new responsive layout shell — fluid container, grid system, `clamp()` type scale, kill the rigid 1240px column. Get viewport-awareness right first; it unblocks everything.
2. **Frozen header:** compact masthead (instrument bar) + activities/section-index row, sticky, with the heavy ink masthead rule.
3. **Newspaper composition per page:** start with **The Gym** (music-left / pills-right multi-column), prove the grammar, then roll it to Today, Vocab Lab, Tune Vault, etc.
4. **Disclosure pattern:** convert pickers/toggles to the bold-underline inline-disclosure house style; kill boxed selects.
5. **Type & texture:** commit the Blue Note + broadsheet typography, rules, kickers, paper grain.
6. **The background world:** port the desert scene behind the content, tie subtle motion to the existing tempo clock, tune it down until it's atmosphere, not distraction.
7. **Polish:** page-turn transitions, letterpress micro-interactions, reduced-motion + responsive QA across large-desktop / laptop / tablet / phone.

---

## 13. Done = this is true

- On a large monitor the app **fills the screen** as a confident broadsheet; on a laptop each page **fits with minimal scrolling**; both reflow gracefully — no rigid centered strip, no dead margins, no horizontal scroll.
- The Gym (and every page) reads as a **newspaper front page**: clear lead, columns, rules, music and exercises grouped side-by-side, far more above the fold.
- The header is a **frozen masthead** with instrument-panel tools and a section-index nav; content scrolls cleanly beneath it.
- Pickers/toggles use the **elegant bold-underline disclosure**, not boxed widgets.
- A **subtle desert world** lives behind everything — alive and tempo-aware when the metronome runs, still and quiet otherwise, never competing with the content.
- The color story is **untouched**; nothing is broken; it makes you go *"oh, shit — this feels like it's been here forever."*
