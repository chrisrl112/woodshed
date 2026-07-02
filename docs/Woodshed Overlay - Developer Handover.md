# THE WOODSHED — Reel Overlay
### Developer Handover & Manifesto

A vertical (9:16) "now-playing" lower-third graphic for short-form video (TikTok / Reels / Shorts). It sits over footage of a musician playing, shows the tune's chord changes moving in time, and markets the practice app **The Woodshed**. Visually it's a mid-century **Blue Note record-sleeve** crossed with a **broadcast lower-third**, rendered as a flat, hard-edged, chroma-key-ready vector scene.

The prototype is a single self-contained HTML file (`Woodshed Overlay v2.dc.html`). This document specifies what every element is, and — most importantly — **how each animation is meant to lock to the music** so a developer can wire it to a real beat clock.

---

## 1. The one idea that matters: everything is on the clock

Every motion in this graphic is derived from **one master tempo clock**. Nothing is on an arbitrary timer. In the prototype the clock is faked from a single `BPM` value; **in production it must be driven by the actual song's beat** (see §7).

```
beat   = 60000 / BPM      // milliseconds per quarter note
bar    = beat * 4         // 4/4 assumed
phrase = bar  * 4         // one 4-bar chord cycle
```

**Phase 0 = the downbeat (beat 1).** Every loop below is phase-aligned so that, at the downbeat, the graphic is in its "1" state (current chord lit, metronome at the left, tree at rest, etc.). If the clock is correct, the chop lands on the backbeat, the metronome ticks on the beat, the tree shakes on every quarter note, and the chords advance on the bar — all automatically, at any tempo.

---

## 2. THE LINKAGES (read this table first)

Example timings shown at **120 BPM** (beat = 500 ms, bar = 2 s, phrase = 8 s).

| Element | Musical trigger | When | Motion |
|---|---|---|---|
| **Master clock** | — | `beat=60000/BPM`, `bar=4·beat`, `phrase=4·bar` | reference; phase 0 = downbeat |
| **Chord billboards** | new chord | advances **1 cell per bar**, 4-cell / 4-bar loop | current cell snaps to orange + spring "pop"; text flips white |
| **Chord impact ring** | chord change | on the bar, per cell | hard square ring expands + fades |
| **Turnaround wipe** | top of phrase | every **phrase** (4 bars) | white slash wipes across the billboards = the "1" of a new chorus |
| **Woodcutter — axe contact** | **backbeat (2 & 4)** | every 2 beats, contact *on* the beat | held high through 1 & 3 → fast snap down → contact on 2 & 4, with a body dip |
| **Wood chips burst** | each axe contact | beats 2 & 4 | orange/ink chips fly from the wedge |
| **Pine tree vibration** | **every quarter note** | each beat | whole tree shudders and settles (he's chopping away) |
| **Metronome light** | **every beat** | one sweep per beat, ping-pong | orange pill glides across the 8 segments and back, easing (slowing) at each end = the tick |
| **REC dot** | downbeat | every bar | scale pulse |
| **"NOW PLAYING" EQ bars** | pulse | ~per beat | 3 bars bounce (loose, organic) |
| **Key chip (e.g. A♭)** | downbeat | every bar | scale pop |
| **Birds** | *ambient — NOT beat-locked* | free loops | 2-frame wing flap + slow drift |
| **Blowing sand / scrub grass** | *ambient wind* | free loops | drift left / sway |
| **Mountains, woodpile, sun-free sky** | static | — | backdrop |

> Rule of thumb: **harmonic motion is on the bar, the backbeat lives in the axe, the pulse lives in the metronome and the tree, and the scenery (birds, wind) is deliberately *off* the grid so the piece breathes.**

---

## 3. Format & hard constraints

- **9:16, 1080 × 1920.**
- The graphic is a compact lower-third (~26% of frame height) anchored to a fixed top edge, with deliberate **green headroom below it** (~20% of frame height) so the platform's own caption/username/UI chrome has room and the card never collides with it. The top ~54% is empty for the performer's video.
- **Chroma-key ready:** everything outside the card is pure green `#00B140`. Keep a clean horizontal break between green and card. Any element that floats over the green (e.g. a free REC badge) must be **fully opaque** so it keys without a fringe — no translucency or soft shadows over the green.
- **Flat vector only:** no gradients, photos, drop-shadow mush, or noise. The "pop" comes from hard color blocks, snap, and spring easing — not glows.
- Must stay legible at phone size over busy footage (solid card behind all text).

---

## 4. Brand

**Color**
| Token | Hex | Use |
|---|---|---|
| Ink | `#1A150F` | text, rules, silhouettes, road |
| Paper / canvas | `#F2ECDF` | card background (one continuous tone top-to-bottom) |
| Orange (accent) | `#E84E10` | wordmark accent, current chord, metronome, chips, key chip |
| White | `#FFFFFF` | reversed text on orange |
| Chroma green | `#00B140` | key background ONLY |

**Scene-only earth tones** (silhouette/desert, all warm — never the chroma green):
mountains `#DBCFB6` (far) / `#AE9468` (near); dune `#E4D8C0` / `#CBB994`; pine foliage `#34402E`; trunk `#4A3826`.

**Type**
- **Archivo Black** — the "THE WOODSHED" wordmark.
- **Oswald** (600) — song title, chord names, key.
- **Inter** (700) — small UI labels (LIVE, NOW PLAYING, KEY).

---

## 5. Layout (top → bottom inside the card)

The card is one continuous `#F2ECDF` panel framed top and bottom by a 7px ink rule. Two **background scenery layers** (mountains on the left, the giant pine on the right) are drawn *behind* all UI and are rooted on the desert floor, so they read as one tall world that the UI floats in front of.

1. **Masthead** — `THE` (ink) + `WOODSHED` (orange), with an orange rule running off the right edge (editorial masthead device).
2. **Title row** — kicker `● NOW PLAYING · HEAD` (with animated EQ), the song title (uppercase Oswald), and an orange **key chip**.
3. **Sky band** — open canvas where **birds** fly and the **mountain peaks** and **pine top** show through.
4. **Chord billboards** — 4 equal cells (the "music strip"); opaque, so the mountains and pine pass *behind* it.
5. **Desert band** — the **woodcutter** chopping the **pine trunk** (wedge notch + chips), the **woodpile** he's stacking, scrub grass, blowing sand; mountain foothills on the left meet the dunes here.
6. **Street** — the **metronome**: a dark "road" holding 8 fat rounded segments.

**Continuity cues (intentional):** the mountains form a natural diagonal (tall left → touching the ground on the right, no vertical cutoff); the pine is rooted on the desert floor and rises *behind the music strip* up to the masthead, and the **very bottom of its foliage pokes out just below the chord strip** to sell the "one tall tree behind everything" read.

---

## 6. Element specs & their beat hooks

**Chord billboards** — 4 cells = one line of the chart (prototype: `Cm7 · F7 · B♭maj7 · E♭7`). Exactly one cell is "lit" (orange fill, white text, slight scale overshoot) at a time; it advances one cell per **bar** and loops every **4 bars (phrase)**. A white **turnaround wipe** crosses the row once per phrase (on the "1"). *In production, drive the lit index from the live chord/bar position, not a fixed timer.*

**Woodcutter** — a pixel-man silhouette with a rotating axe. The axe is **held high during beats 1 & 3** (wind-up) and **snaps down to contact on beats 2 & 4** (backbeat), with a small body dip on contact. Chips burst from the wedge on each contact. Period = **2 beats**, contact at the mid-point. He chops a **wedge notch** cut into the base of the pine trunk (chips lodged in the cut + fresh ones flying).

**Pine tree** — a wide conifer silhouette rooted on the floor on the right, rising behind the chord strip to the masthead. The **entire tree vibrates on every quarter note** (a quick shudder that settles within the beat) — independent of the chop's 2-&-4 contact, because "he's chopping away" continuously.

**Metronome (street)** — 8 fat rounded segments on a dark road. A single **orange light** sweeps across them and back like a metronome pendulum, **one sweep per beat**, easing (slowing) at each end so the turn reads as the "tick." Road height is fixed; only the pills are large.

**REC dot / EQ / Key chip** — small pulse accents on the **downbeat** (dot, key chip) and a loose per-beat **EQ** bounce in the kicker.

**Ambient (off-grid on purpose)** — birds flap + drift on free loops; sand blows and scrub sways on slow free loops. These are *not* beat-locked; they keep the scene alive without fighting the rhythm.

---

## 7. What production must supply (the real linkages)

The prototype fakes the clock from a fixed `BPM` and assumes 4/4 and a 4-bar chord loop. A real implementation should feed it:

1. **A live beat clock** — ideally from the audio/transport engine: current `bpm`, current `beat` and `bar` index, and the **downbeat phase** (so phase 0 lines up with the real "1"). A tap-tempo or click-track source is acceptable; the key requirement is that **the graphic's phase 0 == the song's downbeat**, continuously re-synced (audio drifts).
2. **The tune** — `title`, `key`, and the **chord chart** as an ordered array of measures (e.g. `["Cm7","F7","B♭maj7","E♭7", …]`). The lit billboard = the current measure; advance it from the live bar position. The chart can be longer than 4 — page it 4 measures at a time.
3. **Mode** — `Head` (show the full scene) vs `Improv` (hide the sky/birds band, enlarge the chord cells). 
4. **Tempo** — if no live clock is available, a manual BPM so all loops still lock to each other.

Everything else (which beat the axe hits, when the metronome ticks, when the tree shakes, when the chord flips) is **derived** from items 1–3. Do not hand-author per-event timers; bind to the clock.

---

## 8. Tweakable parameters (already exposed in the prototype)

- **mode**: `Head` | `Improv`
- **tempo**: BPM (drives every loop)

Recommended additions for production: `title`, `key`, `chords[]`, and a `beatClock` source object.

---

## 9. Implementation notes (how the prototype builds it)

- **Pixel sprites** (birds, woodcutter, woodpile log-ends) are drawn with CSS `box-shadow` "pixel grids" or stacked divs — crisp at any scale, no image assets.
- **Silhouettes** (mountains, pine, dunes, axe head, trunk wedge) are `clip-path: polygon(...)` shapes — vector, hard-edged, recolorable.
- **Motion** is CSS `@keyframes` whose **durations are bound to the clock** (`beat`, `bar`, `phrase`). The chord ignite uses **negative `animation-delay`** per cell so exactly one is lit from frame 1. The metronome uses a single element with `animation-direction: alternate` over a CSS-variable sweep distance.
- **Layering**: background scenery is painted first (behind), the opaque chord strip masks the middle of the tall elements, and the desert actors are painted last (in front of the trunk).
- No external libraries; Google Fonts only (Archivo Black, Oswald, Inter).

---

## 10. Chroma-key & export

- Card edges meet the green on crisp horizontal ink rules — clean key boundaries.
- All scene tones are warm earth colors held well away from `#00B140`; keep key tolerance moderate and they survive.
- Any element floating over the green (optional free REC badge) must be fully opaque.
- Browser tabs pause CSS animation when hidden — the overlay only animates while its view is visible (irrelevant once composited to video, but note it for QA).

---

*Prototype file: `Woodshed Overlay v2.dc.html`. This document is the source of truth for intent and timing; the file is the visual reference.*
