# The Woodshed — Reel Overlay: Design Brief / Prompt

*Paste everything below into Claude (or any design tool). It's written as a self-contained prompt.*

---

Design a beautiful, eye-catching **lower-third overlay graphic** for vertical short-form video (TikTok / Reels / Shorts). It sits at the **bottom of the frame** over a video of me playing jazz trumpet. It's a "now-playing" card that shows a tune's chord changes moving in time, and it markets my practice app, **The Woodshed**. The current version works but doesn't *pop* — I want it to look like it was art-directed.

Deliver a **single self-contained HTML file** (HTML5 Canvas or inline SVG + CSS, no external libraries except optional Google Fonts) that renders the full 9:16 frame with placeholder content, flat and chroma-key-ready, with the current-measure highlight animating. Make it genuinely gorgeous and on-brand.

## Format & hard constraints
- Vertical **9:16, 1080×1920**.
- The overlay occupies **only the bottom ~30%** of the frame (max). The top ~70% is empty for my video.
- **Chroma-key ready:** everything outside the card is pure green **#00B140**, with a **clean, crisp horizontal break** between the green and the card (no elements straddling the edge — keying fringes them).
- Flat vector style — no gradients, photos, drop-shadow mush, or noise. Bold shapes and type.
- Must stay **legible at phone size over busy footage**.
- Implementable/animatable on Canvas or SVG (a highlight moves across the chords; a badge pulses).

## Brand — mid-century Blue Note jazz
- **Colors:** ink/near-black `#1A150F`, warm paper/tan `#F2ECDF`, hot orange `#E84E10` (the single accent — use it boldly), white `#FFFFFF`, chroma green `#00B140` (key background only).
- **Type:** Archivo Black (heavy display / wordmark), Oswald (condensed — chord labels), Inter (small UI). You may propose a better retro-jazz pairing if it's stronger.
- **Vibe:** premium, retro Blue Note record-sleeve, confident, high-signal, a little swagger — "cool, not cringe." Strong color-blocking, intentional negative space, hard edges. It should POP.

## Elements the card must contain
1. **Wordmark "THE WOODSHED"** sitting fully on the tan card. An **orange bar/rule extends from the end of the word to the right edge** (editorial masthead device).
2. **Tune title on its own line**, plus the song's key. (Example: title "All The Things You Are", key "A♭".)
3. A **notation strip** — one line of a lead sheet (placeholder five-line staff with a few generic notes; do NOT use any real copyrighted sheet music) shown full-width. In the real app this rolls one line at a time.
4. A row of **four chord "measures"** (one line of the chart). The **current measure is highlighted in orange**; it advances measure-to-measure. Example chords: `Cm7  F7  B♭maj7  E♭7`, current = `F7`. Use rounded chips or a divided bar — your call, make it stylish.
5. A small **"LIVE" / REC badge top-right** (red dot) that pulses on the downbeat.

## Behavior (context, for the animation)
- **Head (first chorus):** show the notation strip + the four chord measures.
- **Improv (later choruses):** hide the notation, show just the four chord measures (larger).

## What "pop" means to me
Bold, intentional, premium, retro-jazz energy — like a Blue Note cover crossed with a sharp broadcast lower-third. **Avoid:** generic SaaS templates, fake luxury, corny "music app" clichés, thin/timid type.

Return the HTML file plus a one-paragraph note on the type/layout choices you made and why.
