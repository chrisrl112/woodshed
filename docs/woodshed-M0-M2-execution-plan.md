# Woodshed — M0 → M2 Execution Plan (Weeks 1–6)

**Window:** Jun 29 – Aug 9, 2026 · **Budget:** 5–8 hrs/wk · **Owner:** Chris

**The two milestones in scope** (plus M0, the prerequisite ship):

- **M0 — Demo live + instrumented.** Hosted URL, email capture, vote board, analytics firing. *(Weeks 1–2)*
- **M1 — Message resonates: 50 waitlist emails.** Proves the *promise* lands. *(Weeks 3–5)*
- **M2 — Interest has depth: 25%+ of list opens the demo, 15+ feature votes.** Proves the demo *activates*. *(Weeks 5–6)*

This phase stays **free-tool framed**. No payment, no pricing. You're buying signal and a list, not revenue yet. Money is M3 (next phase). Polluting M1/M2 with a paywall kills the community-share passport your own map is built around.

---

## PART A — What's on the demo site

### A.0 The wedge: one practice surface, not six

The demo isn't selling a backing-band toy — iReal already owns that fight. It's selling **consolidation**: the trumpeter's practice session today is a mess of a Real Book PDF on an iPad, a metronome app on a phone, a YouTube play-along on a laptop, a notes app for the routine, a separate tracker for streaks. **The Woodshed is mission control — open one tab, press play, and your whole session is there in order.** Warmup → jam → done, no tab-switching, no device-juggling.

So the demo must *show the session*, not just a feature. A visitor should see two stations stacked the way a real practice session flows:

- **Warmup** — a real exercise page with an inline metronome + rep tracker.
- **Jam Session** — lead sheet(s) + Real Book changes + a customizable band.

That's the "oh — it's all *here*" moment. The honest pitch vs. iReal: *80% of the jam capability, but it's one thoughtful surface that keeps you consistent and organized, with the warmup and the practice discipline built in.* You win on **workflow and consistency**, not on having more chord voicings than iReal.

### A.1 The site's three jobs

1. **Show the consolidation** — a visitor sees a *whole session* (warmup + jam) on one surface and gets the "all in one place" wedge in a glance. (The differentiator.)
2. **Activate in 30 seconds** — they press one play button and hear a real band / hear the metronome, without reading or signing up. (Drives M2.)
3. **Capture the raised hand** — one frictionless email field + a vote board. (Drives M1 + M2.)

It is **not** the full Woodshed. Everything that doesn't serve those three jobs gets cut from the lite build — deep logging, range work, the feedback agent, the full 26-tune library — all M3+ territory. The lite demo shows *one clean session*, not the whole gym.

### A.2 The hard guardrail: copyright (your own gate already enforces this)

Your `public-assets/verify_public_safe.py` gate already enforces the core rule: never ship Real Book scans or source PDFs. Here's the precise legal line for the two new sections, verified June 2026.

**The one rule that governs everything:**

- **Chord changes only (no melody) → safe for ANY tune,** including still-copyrighted standards. Chord progressions are functional data, not copyrightable — this is the exact legal basis iReal Pro operates on. Use this for the "jam over changes" tunes from your 26 (Blue Monk, So What, etc.).
- **Full lead sheet (melody + chords) → ONLY for public-domain compositions** that you engrave yourself. Re-engraving a *copyrighted* tune does **not** make it yours — the composition copyright survives regardless of who typesets it. So the lead sheet you display must be a PD tune.
- **Audio → always your own band / your own playing.** Sound recordings are a separate copyright; never use a famous recording. Your synthesized band + your trumpet are 100% safe.

**What's public domain as of 2026 (verified):** everything published **1930 or earlier** is now PD in the US.

- **Warmup methods:** **Arban (1864)** and **Clarke Technical Studies (1912)** are public domain. ⚠️ *But modern Carl Fischer editions have their own copyrighted engraving* — don't scan a current edition. Use the IMSLP / Mutopia Project PD typesets, or re-engrave the exercise yourself (you have the OMR + score tooling to do this cleanly). **Cichowicz is modern and still copyrighted — keep it out of the public demo** (fine for your private practice).
- **Jam standards (now PD, melody + chords both publishable):** "I Got Rhythm," "Body and Soul," "On the Sunny Side of the Street," "Embraceable You," "Georgia on My Mind" (all 1930) · "Star Dust," "Ain't Misbehavin'," "Honeysuckle Rose" (1929). Plus blues/trad forms ("St. Louis Blues," "When the Saints").

✅ **Ships:** PD exercise pages (re-engraved or IMSLP), your own engraved lead sheet of a PD standard, chord-changes-only for any tune, your band audio, your trumpet/overlays.
❌ **Never ships:** Real Book / Real Christmas PDF pages, scanned modern editions, full melody notation of any post-1930 tune.

**Run `./publish.sh` before every deploy** — treat a gate failure as a hard stop. (Consider extending the gate to also flag any melody-bearing notation whose tune isn't on a PD allowlist.)

### A.3 Page structure (single scroll, no login)

The single scroll *is* a practice session, top to bottom: hero → warmup → jam → ask. The structure itself sells the consolidation.

```
┌──────────────────────────────────────────────┐
│ 1. HERO — "your whole session, one tab"        │
│    - 8–12s autoplay loop: you playing w/ overlay │
│    - Headline + subhead + one CTA button        │
│    - CTA scrolls to the session (not a signup)  │
├──────────────────────────────────────────────┤
│ 2. STATION 1 — WARMUP                          │
│    - A real PD exercise page (Clarke/Arban)     │
│    - Inline metronome (tap tempo, start/stop)   │
│    - Rep tracker / check-off (the "tracker")    │
│    - Frames the wedge: "this is where you start"│
├──────────────────────────────────────────────┤
│ 3. STATION 2 — JAM SESSION (the wow)           │
│    - Tune picker: 1–2 PD lead sheets + 2 changes│
│    - Big PLAY → band (bass+comp+drums) runs it, │
│      chord playhead moves                        │
│    - Tempo slider + count-in                     │
│    - Customizable: "feel" (Evans/Garland/Jamal) │
│      + drums on/off — the iReal-parity moment   │
├──────────────────────────────────────────────┤
│ 4. THE PITCH — one line                         │
│    - "Six tabs → one surface." consolidation say-it│
├──────────────────────────────────────────────┤
│ 5. THE ASK — WAITLIST + VOTE BOARD              │
│    - One email field + value-prop microcopy     │
│    - Embedded Canny/Featurebase, 6–8 seeded     │
├──────────────────────────────────────────────┤
│ 6. FOOTER — who's building this + TikTok        │
└──────────────────────────────────────────────┘
```

*(Workshop candidate, per your note: whether Warmup sits above Jam, or Jam leads and Warmup proves depth on scroll. Default above = "mirror a real session." If analytics show people bounce before reaching Jam, flip them so the wow comes first.)*

### A.4 The lite content set

**Warmup station — pick ONE PD exercise to start:**

| Option | Why | Source |
|---|---|---|
| **Clarke Technical Studies, Study II** *(recommended)* | The single most-recognized trumpet warmup — instant credibility with the r/trumpet crowd. A clean page + ticking metronome + rep check-off *is* the consolidation pitch in one screen. | IMSLP PD typeset, or re-engrave |
| Arban — slurs / first studies | Equally PD, broader (cornet+trumpet); good alt if you'd rather not lead with finger-busters. | Mutopia Project PD typeset |

Re-engrave it in your own notation rather than embedding the IMSLP PDF — cleaner, on-brand, and zero edition-copyright risk.

**Jam station — 1 PD lead sheet (melody shown) + 2 changes-only tunes:**

| Slot | Tune | Legal basis | Why |
|---|---|---|---|
| **PD lead sheet** *(the "real chart, all here" showcase)* | **"On the Sunny Side of the Street"** (1930, now PD) | Full melody + chords — you engrave it | Instantly recognizable, singable, friendly. Proves you can ship a *real lead sheet* legally. |
| Alt PD lead sheet | **"I Got Rhythm"** (1930, now PD) | Full melody + chords | Rhythm changes = the most-used form in jazz; max utility signal. Great as the 2nd PD chart. |
| Changes-only | **Blue Monk** | Chord changes only (no melody) | Universally known blues; band grooves obviously. |
| Changes-only | **So What** | Chord changes only | Sparse modal changes = cleanest playhead demo; the "oh, a real band" moment. |

**Ship minimum:** 1 warmup (Clarke II) + 1 PD lead sheet (Sunny Side) + 2 changes-only (Blue Monk, So What). That's a complete session and proves the consolidation wedge. Adding "I Got Rhythm" as a 2nd PD chart is the high-value stretch.

**The one new build task:** engrave 1–2 PD lead sheets. Your `score-to-woodshed` skill is purpose-built for exactly this — it produces verified ABC notation you can drop into the app. Budget this into Week 1.

### A.5 The 30-second activation path (design the default state for this)

Two stations create a risk: the warmup sitting above the jam could bury the wow. Solve it with the CTA, not by reordering everything:

1. Land → see you playing (hero loop auto-plays muted, captioned).
2. **Hero CTA jumps straight to the Jam station**, already cued to **Blue Monk at a medium tempo** — one obvious PLAY button.
3. Hit **one PLAY** → band comes in, playhead moves. *That's the wow.* (Feel toggle + tempo slider right there for discovery.)
4. *Then* they scroll up and discover the Warmup station already sitting there — which is the "wait, it's all in one place" realization. The wow earns the consolidation insight.

Default station loaded, default tune, default tempo, one button to the wow. The warmup reinforces the wedge *after* you've hooked them — it doesn't gate the hook. Every extra decision before the band plays costs you M2 activation.

### A.6 Capture + vote: use hosted embeds (no backend)

- **Email:** [Tally](https://tally.so) or **ConvertKit/Beehiiv** form embed. Beehiiv/ConvertKit is better if you'll email the list later (you will — M2 activation depends on it). One field: email. No name, no friction.
- **Votes:** [Canny](https://canny.io) (free tier) or **Featurebase**. Public board, upvotes, lets people add their own. Doubles as your roadmap and a content source ("you voted, I shipped").
- Both are `<script>`/iframe embeds → work on a static host, no server needed.

### A.7 Hosting (you're closer than you think)

You already have a **public-bundle / publish-gate pipeline** (`publish.sh` → `public-assets/ci_check.py` → snapshot). The deploy is the one manual step left.

- **Build:** produce the static public bundle via your existing snapshot path, trimmed to the lite tune set.
- **Deploy:** **Cloudflare Pages** or **Netlify** — free, static, drag-and-drop or git-connected, custom domain + HTTPS in minutes.
- **Domain:** grab something clean (e.g. `thewoodshed.app` / `woodshed.fm` / `playthewoodshed.com`).
- ⚠️ **Verify first (Week 1, before anything else):** does the backing band play in a *purely static* deploy with **no `woodshed_server.py` running**? The comping/drums are client-side audio, so it *should* — but confirm by opening the built bundle from `file://` or a dumb static server with the Python server OFF. If something only works through the local server, that's your one real build task this week. **This is the single biggest technical risk in the whole plan — de-risk it Day 1.**

### A.8 Analytics — instrument these exact events (you can't run the ladder blind)

Use **Plausible** (clean, privacy-friendly, one script) or GA4. Track:

| Event | Feeds which rate |
|---|---|
| `page_view` (+ source/UTM) | Reach → site |
| `demo_play` (hit play on any tune) | **Activation (M2 numerator)** |
| `metronome_start` (warmup station) | Did the consolidation wedge land? |
| `feel_toggle` / `tempo_change` | Depth of engagement |
| `waitlist_submit` | **Capture (M1)** |
| `vote_cast` | **Depth (M2)** |
| outbound click to TikTok | Cross-pollination |

Tag every shared link with UTMs (`?utm_source=reddit_trumpet`, `?utm_source=tiktok`, etc.) so you know **which channel converts**, not just that something did.

---

## PART B — Week-by-week (Weeks 1–6)

> **Operating rhythm each week** (fits 5–8 hrs): one ~2.5h build/batch block (Sun), one ~1h community/engagement block (midweek), one ~0.5h dashboard read (Fri). Weeks 1–2 borrow extra from the "flex/product" hours to ship.

### WEEK 1 — Jun 29 to Jul 5 · *De-risk + ship the skeleton* → toward M0

**Objective:** the lite demo is live at a real URL, even if rough. Done > polished.

- [ ] **Day 1 — kill the technical risk (A.7):** confirm the backing band plays in a static deploy with the Python server OFF. If yes, you're clear. If no, fix that before touching anything else.
- [ ] **Engrave 1 PD lead sheet** ("On the Sunny Side of the Street") via `score-to-woodshed` → ABC into the app. (Stretch: also "I Got Rhythm.")
- [ ] **Stand up the Warmup station:** one re-engraved PD exercise (Clarke II) + inline metronome + a simple rep check-off.
- [ ] Set the Jam station's changes-only tunes (Blue Monk, So What) + default state: Blue Monk cued, medium tempo, one PLAY (A.5).
- [ ] Wire the **hero CTA → Jam station** (the wow comes first, A.5).
- [ ] Run `./publish.sh` → build the static bundle (must pass the copyright gate; confirm no melody-bearing notation except the PD lead sheet).
- [ ] Deploy to Cloudflare Pages/Netlify. Buy + connect the domain.
- [ ] **Exit check:** open the URL on your phone → CTA → hear the band; scroll up → metronome ticks on the warmup.

**Time:** 5–6h (heaviest week — front-loaded on purpose; the engraving + warmup station are the new build cost). **Watch:** nothing yet; just ship. *If time is tight, cut the warmup station to a static exercise image + metronome (no tracker) and add the tracker in Week 2 — but keep both stations visible so the consolidation wedge reads.*

### WEEK 2 — Jul 6 to Jul 12 · *Instrument + wire the asks* → **hits M0**

**Objective:** the funnel can be measured and can capture a hand-raise.

- [ ] Add Plausible; confirm `page_view`, `demo_play`, `waitlist_submit`, `vote_cast` fire (A.8).
- [ ] Embed the waitlist form (A.6) with the value-prop microcopy (Part C).
- [ ] Stand up the Canny/Featurebase board; seed 6–8 features (Part C).
- [ ] Write the hero headline/subhead + footer POV (Part C).
- [ ] Record/cut the 8–12s hero loop from existing footage (you have reels already).
- [ ] **Soft test:** send the link to 5–10 trusted friends/fellow players. Watch analytics: does `demo_play` fire? Do they find the email field? Fix the obvious drop-offs.
- [ ] **🚩 M0 GATE:** URL live · play works · an email lands in your list · a vote registers · analytics fire. **All five green = advance to M1 push.**

**Time:** 5–6h. **Watch:** does the soft-test group actually hit play? If <50% do, your activation path (A.5) needs work *before* you drive traffic to it.

### WEEK 3 — Jul 13 to Jul 19 · *Content engine on + first warm shares* → M1 begins

**Objective:** start filling the top of funnel. Begin with your **warmest** rooms.

- [ ] **Batch 5 posts** for the week (use the pillar formula from the master gameplan: Take / Play / Build / Play / Ask). Every caption ends with a soft CTA to the demo.
- [ ] Post to TikTok daily; cross-post each cut to Reels + Shorts.
- [ ] **First community share — start where you're welcome (per your map):**
  - **Jazzcord (Discord)** — verified welcoming; hang out, then share in the projects/share channel as a free tool + feedback ask.
  - **r/trumpet** — your bullseye. Post the "I built this for my own practice" share (Part C). Read the live sidebar rule first.
- [ ] Reply to every comment/DM. Engagement is the algorithm's oxygen and your highest-trust conversion.
- [ ] **Fri dashboard:** waitlist count, demo_play count, top traffic source.

**Time:** 6h. **Watch:** **waitlist adds per post** and **per channel.** This is the M1 signal. Which room sends the best traffic?

### WEEK 4 — Jul 20 to Jul 26 · *Sustain + widen* → drive toward M1

**Objective:** keep posting; add the next tier of rooms; double down on what's working.

- [ ] Batch + post 5 again. **Make more of whatever pillar drove the most waitlist adds** in Week 3 (likely The Take or The Build — not the straight performances).
- [ ] **Next community rooms (space them out — don't carpet-bomb, it's the #1 spam flag):**
  - **r/WeAreTheMusicMakers** weekly promo/feedback thread — give 2–3 others real feedback first.
  - **Trumpet Herald** Jazz/Commercial subforum — post a few genuine replies, then your thread.
- [ ] DM your 5–10 most engaged TikTok followers personally: "building this, would love your take" → demo link.
- [ ] **Fri dashboard.** Are you on pace for 50 emails by end of Week 5? If adds/week < 15, the bottleneck is **reach or message** — see the diagnostic below.

**Time:** 6h. **Watch:** cumulative waitlist vs. the 50 line. Channel mix.

### WEEK 5 — Jul 27 to Aug 2 · ***Hit M1*** → pivot to activation (M2)

**Objective:** cross 50 emails; turn the list from passive to active.

- [ ] Keep the posting cadence (don't drop content the moment you pivot).
- [ ] **🚩 M1 GATE: 50 waitlist emails.** Hit it → start the M2 activation push. Missed it after a fair test → run the M1 diagnostic (below) *before* adding more volume.
- [ ] **Send your first list email** (you finally have a reason to): "Thanks for joining — here's the live demo, go play a tune, and tell me the ONE thing I should build next → [vote board]." This single email is your primary M2 lever: it drives both `demo_play` and `vote_cast` from people who already raised a hand.
- [ ] Post the **first "you voted" content** if votes are coming in — closing the loop publicly is your highest-trust post.

**Time:** 5–6h. **Watch:** **demo-open rate of the list** (target 25%+) and **vote count** (target 15+). These are M2.

### WEEK 6 — Aug 3 to Aug 9 · ***Drive M2*** → read the funnel, set up M3

**Objective:** confirm the list actually engages, not just signs up.

- [ ] Second list email if needed: a specific, fun prompt — "Which feel do you practice to — Evans, Garland, or Jamal? Reply and tell me." (Replies train deliverability + give you content + qualify interest.)
- [ ] Keep posting; lean into Build/Take.
- [ ] **🚩 M2 GATE:** ≥25% of the list has opened the demo (`demo_play` from list traffic) **and** ≥15 feature votes. Hit both → the funnel activates; you've earned the right to test willingness-to-pay (M3).
- [ ] **Compute the real funnel** end-to-end: Reach → site → demo_play → waitlist → vote. Write down the actual rates. These numbers *are* the deliverable of this phase — they tell you exactly where M3's money test will leak.
- [ ] **Decide M3 setup:** which feature won the vote (that's your founder offer's headline), and which channel converts best (that's where you'll launch the founder tier).

**Time:** 5–6h. **Watch:** the full rate table. Retention hint: did anyone come back and play twice?

---

## PART C — Ready-to-use copy

### Hero (site top)

> **Headline:** *Your whole practice session. One tab.*
> **Subhead:** Warmup, lead sheets, and a real backing band — in one free, no-login surface. Stop juggling a PDF, a metronome app, and a YouTube tab. Press play and practice. Built by a trumpet player for the woodshed.
> **CTA button:** ▶ Start the session

*(Alt headline, band-forward: "Practice jazz with a band that actually shows up." · Alt, POV/edge: "Six tabs, three devices, one messy practice session. I built the fix.")*

### Waitlist microcopy (above the email field)

> **Get early access — and a vote on what I build next.**
> I'm building this in the open. Drop your email for the next release, and tell me what to build on the board below.
> `[ your email ]  [ Get access ]`
> *No spam. Just the occasional "here's what's new."*

### Footer POV (who's building this)

> Built by Chris — SVP by day, learning to actually play jazz by night. Woodshedding in public, one tune at a time. → [TikTok @yourhandle]

### r/trumpet intro post (read the live sidebar rule first)

> **Title:** Built a free, no-login practice room for my own jazz woodshedding — would love feedback
>
> I'm a comeback-ish player working on jazz, and I was tired of practicing across six tabs — a Real Book PDF, a metronome app, a YouTube play-along, a notes app for my routine. So I built one surface that holds the whole session: a warmup page with a built-in metronome, then a jam section where a backing band runs the changes with you (adjustable tempo, a few comping feels). No login, no paywall, nothing to install.
>
> It's rough and early, but it's already changed how consistent my practice is. Sharing in case other players find it useful — and I'd genuinely love feedback on what would make it better. [link]
>
> *(What I'm most curious about: does the band feel good to play over, and what tune/feature would you want next?)*

### Jazzcord (Discord) share — projects/share channel, after hanging out

> Hey all — been lurking and enjoying the server. I built a free practice tool for my own jazz woodshedding: pick a tune, a backing band plays the changes, adjustable tempo + a couple comping feels. No login. Would love feedback from people who actually play over changes — especially whether the comping feels musical. [link]

### Seed the vote board with 6–8 features

Pick from these so first-time visitors have something to react to immediately (don't ship a blank board):

1. More tunes (which ones? — let them name them)
2. Build-your-own session (warmup → tunes → cooldown, saved as a routine) — *the consolidation feature; watch if this rises*
3. Transpose / concert-pitch toggle (Bb, Eb, C)
4. Loop a section (woodshed a hard 4 bars)
5. More warmup exercises (Clarke/Arban library)
6. Slow-down trainer (gradual tempo bump)
7. Save your practice streak / log
8. Mobile app version

*(Seed #2 is a probe: if "build-your-own session" climbs the board, the market is confirming consolidation — not feature parity — is the wedge. That's a real strategic signal, not just a feature request.)*

---

## PART D — Diagnostics (when a gate stalls, fix the named thing — never just "post more")

| Stalled at | The bottleneck is | Do this — NOT "more volume" |
|---|---|---|
| **M0** (can't ship) | Static deploy / backing band needs the server | Fix the build so audio works statically (Week 1, A.7). |
| **M1** < 50, but demo-open rate is *high* among visitors | **Reach** — not enough people see it | Add channels, post more cross-platform, go IRL (Green Mill jam). The funnel works; it's just small. |
| **M1** < 50, and demo-open rate is *low* | **Message** — the promise/hook isn't landing | Rewrite the hero + the post hooks. Test a sharper POV angle. The product isn't the problem yet. |
| **M2** — people sign up but don't open the demo | **Activation** — the first 30 seconds | Simplify the default state (A.5). One tune, one button, instant band. Cut every step before the wow. |
| **M2** — they play but don't vote | **Investment ask** | Make voting one tap; seed the board; literally ask in the post-signup email. |

**The rule:** volume never fixes a broken rate. Diagnose *which* number is low, fix that, then pour traffic into a funnel you've proven converts.

---

## The 6-week scoreboard (one glance)

| Week | Milestone | The one number that matters |
|---|---|---|
| 1 | Skeleton live | URL works + band plays |
| 2 | **M0** | All 5 instrumentation checks green |
| 3 | M1 begins | Waitlist adds per channel |
| 4 | M1 push | Cumulative waitlist vs. 50 |
| 5 | **M1** (50 emails) | 50 ✅ → demo-open rate |
| 6 | **M2** | 25% list activation + 15 votes |

Ship rough in Weeks 1–2. The only thing that matters in July is **50 emails**. Everything else is in service of that.
