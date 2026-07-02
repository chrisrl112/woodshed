# Woodshed Lite — Design Brief for Claude Design

**What you're designing:** A single-scroll public landing page for The Woodshed — a jazz trumpet practice app. This is the marketing/demo page, not the app itself. Goal: most beautiful possible distillation of the concept. Someone lands, feels the aesthetic, gets the value prop in 3 seconds, hits play, and is converted.

---

## The vibe

**Blue Note record sleeve.** Reid Miles energy. Warm paper, ink black, ONE hot orange. Not a tech startup landing page. Not a music-school brochure. Something that looks like it belongs on a shelf next to a Miles Davis record — but it's a web page that plays jazz.

Polished, intentional, a little swagger. Premium without being flashy.

---

## Design system (locked — use exactly these tokens)

```css
/* FONTS — load from Google Fonts */
/* Archivo Black — display/headlines */
/* Oswald 500/600/700 — labels, kickers, nav */
/* Inter 400/500/600/700 — body, UI */
/* JetBrains Mono — data, BPM, code-like text */
@import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=Archivo:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600;700&family=Oswald:wght@500;600;700&display=swap');

:root {
  /* Palette */
  --bg:      #f2ecdf;   /* warm paper — page background */
  --surface: #faf6ec;   /* slightly lighter paper — cards */
  --ink:     #1a150f;   /* near-black — borders, text, shadows */
  --brass:   #e84e10;   /* THE hot orange — used sparingly, maximum impact */
  --brass-hi:#c23c07;   /* darker on hover */
  --muted:   #5d5343;   /* secondary text */
  --faint:   #968a72;   /* tertiary text, placeholders */
  --paper:   #fffdf4;   /* near-white — card backgrounds */
  --line:    #d6c9af;   /* dividers */

  /* Shadows — hard offset, no blur. This IS the aesthetic. */
  --shadow-sm: 3px 3px 0 var(--ink);
  --shadow:    5px 5px 0 var(--ink);
  --shadow-lg: 9px 9px 0 var(--ink);

  /* Type scale */
  --disp: 'Archivo Black', sans-serif;
  --osw:  'Oswald', sans-serif;
  --ui:   'Inter', sans-serif;
  --mono: 'JetBrains Mono', monospace;
}

/* Key component patterns */

/* CTA button — the main action */
.cta {
  font-family: var(--osw);
  font-weight: 700;
  font-size: clamp(17px, 1.4vw, 22px);
  letter-spacing: .5px;
  text-transform: uppercase;
  padding: 14px 32px;
  background: var(--brass);
  color: #fffdf4;
  border: 2px solid var(--ink);
  border-radius: 4px;
  box-shadow: 5px 5px 0 var(--ink);
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  transition: transform .08s, box-shadow .08s;
}
.cta:hover  { transform: translate(-1px,-1px); box-shadow: 6px 6px 0 var(--ink); }
.cta:active { transform: translate(5px,5px);   box-shadow: 0 0 0 var(--ink); }

/* Cards — hard offset shadow, ink border, no border-radius or very small */
.card {
  background: var(--paper);
  border: 2px solid var(--ink);
  border-radius: 4px;
  box-shadow: var(--shadow-lg);
  padding: clamp(18px, 1.6vw, 28px);
}

/* Chart card — the musical notation display */
.chartcard {
  background: var(--paper);
  border: 3px solid var(--ink);
  border-radius: 8px;
  box-shadow: 9px 9px 0 var(--ink);
  padding: 18px 22px 14px;
}
/* Orange rule above the staff — the signature chart card detail */
.cc-rule { height: 5px; background: var(--brass); border-radius: 2px; margin: 11px 0 4px; }

/* Kickers / eyebrows */
.kicker {
  font-family: var(--ui);
  font-weight: 800;
  font-size: 13px;
  letter-spacing: .18em;
  text-transform: uppercase;
  color: var(--brass);
}

/* Pitch/invert section */
.pitch-section {
  background: var(--ink);
  color: var(--paper);
  /* any brass accent words → color: var(--brass) */
}
```

---

## Page structure & copy (exact)

### 1 — HERO (full viewport height)
- Optional: muted video loop in background (dim it, paper shows through)
- **Headline:** `Your whole practice session. One tab.`
- **Subhead:** `Warmup, lead sheets, and a real backing band — in one free, no-login surface. Stop juggling a PDF, a metronome app, and a YouTube tab. Press play and practice. Built by a trumpet player, for the woodshed.`
- **CTA:** `▶ Start the session` → jumps to Jam station
- Alt headlines to consider: `"Practice jazz with a band that actually shows up."` / `"Six tabs, three devices, one messy practice session. I built the fix."`

### 2 — WARMUP STATION
- **Kicker:** `Station 1 · Warmup`
- **Station line:** `This is where every session starts.`
- Content: mockup of the Clarke Technical Study II exercise — show an ABC notation staff (you can draw stylized lines suggesting notation), metronome display showing BPM (in JetBrains Mono, orange), and a rep tracker (e.g. ○ ○ ○ ○ ○ → five circles, first one filled brass)
- Make this look like a real UI slice, not a placeholder box

### 3 — JAM STATION (the wow — most important section)
- **Kicker:** `Station 2 · Jam`
- **Station line:** `A band that actually shows up. Pick a tune, press play.`
- Content: mockup of the chord chart player — show:
  - Tune picker: `Blue Monk · So What · Sunny Side of the Street` (Blue Monk highlighted/active)
  - A chord chart card (`.chartcard` style) with fake chord changes: bars showing `F7 | Bb7 | F7 | F7 | Bb7 | Bb7 | F7 | F7 | C7 | Bb7 | F7 | C7` (Blue Monk blues changes, roughly) — one bar highlighted orange (the playhead)
  - A big brass PLAY button
  - Tempo slider (showing ~120 BPM in monospace), Feel toggle buttons (`Evans · Garland · Jamal`)
- This should feel like you can almost hear it

### 4 — PITCH (full-bleed dark section)
- `Six tabs, three devices →` **`one surface.`**
- Short. Punchy. Ink background, paper text, brass on the key words.

### 5 — THE ASK (funnel)
- **Headline:** `Get early access — and a vote on what I build next.`
- **Subhead:** `I'm building this in the open. Drop your email for the next release, and tell me what to build on the board below. No spam. Just the occasional "here's what's new."`
- Email input + submit button (MailerLite embed slot — style the placeholder to match)
- Below: vote board placeholder (`What should I build next?` — show a few seeded items as cards: `More tunes` · `Build-your-own session` · `Loop a section` · `Mobile app`)

### 6 — FOOTER
- `Built by Chris — SVP by day, learning to actually play jazz by night. Woodshedding in public, one tune at a time.`
- Social links: TikTok · Instagram · YouTube

---

## Design intent: what "most beautiful distillation" means

This page has to do something the app doesn't: **arrest someone in 3 seconds.** The app can afford to be functional. This page has to make someone feel something — that this exists, that someone built this with care, that it would actually make their practice better.

Design goals:
- **The hero should be cinematic.** Big headline, lots of space, the CTA feels like the only possible action.
- **The station sections should feel like zoomed-in windows into a real product** — not mockup boxes, actual UI slices with real text, real controls, real chart data. Someone should be able to look at the Jam station and understand exactly what the product does.
- **The pitch section should punch.** Ink background, maybe huge type, the contrast is jarring in a good way.
- **The ask should feel human, not corporate.** It's one person building something. The copy is personal. The form should match.
- **Vertical rhythm and whitespace matter a lot.** Blue Note records have incredible use of negative space — don't fill every inch.
- **The hard offset shadow is non-negotiable.** It's the visual signature of this design system. Every card, every button, every chart panel should have it.

---

## Files included
- `woodshed-lite/index.html` — current landing shell (HTML structure + copy, stations are empty slots)
- `woodshed-lite/src/landing.css` — current stub CSS (has the tokens and skeleton, needs a full design pass)

## Output requested
A fully redesigned `index.html` + `landing.css` (or a single combined HTML file) that is **production-quality static HTML/CSS** — no JS required to render the design, just the visual layer. The station slots can be richly mocked up. The design should be so good that Claude Code just needs to wire in the engine, not redesign anything.
