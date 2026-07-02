# Woodshed — Validation & Content Gameplan

**Owner:** Chris
**Window:** Jun 28 – Sep 27, 2026 (13 weeks / ~90 days)
**Budget:** 5–8 hrs/week
**Objective:** Sequenced — (1) ship the lite demo, (2) build a content engine + list, (3) validate willingness to pay. Decide go/no-go on a bigger build by end of Q3.

---

## 0. What the product actually is (the wedge)

The Woodshed isn't "a backing-band app" — that fight belongs to iReal Pro. It's **one practice surface that holds your whole session.** Today a trumpeter practices across six tabs: a Real Book PDF on the iPad, a metronome app on the phone, a YouTube play-along on the laptop, a notes app for the routine, a tracker for streaks. The Woodshed is **mission control: open one tab, press play, and warmup → jam → done is all there, in order.**

**Positioning vs. iReal (your biggest competitor):** don't out-feature them. Concede it openly — *"~80% of the jam capability, but it's one thoughtful surface that keeps you consistent and organized, with the warmup and practice discipline built in."* You win on **workflow and consistency**, not voicing count. The wedge is the *session*, not the sound engine.

**The legal foundation (verified Jun 2026) — this is an enabler, not just a constraint:**

- **Chord changes are functional data, not copyrightable** (the iReal legal model). You can ship changes for *any* tune, including copyrighted standards.
- **Full lead sheets only for public-domain tunes** you engrave yourself. As of 2026, everything published **1930 or earlier** is PD — which now includes genuinely recognizable charts: "I Got Rhythm," "Body and Soul," "On the Sunny Side of the Street," "Star Dust," "Ain't Misbehavin'." Re-engraving a *copyrighted* tune does NOT make it yours; pick PD tunes.
- **Warmups:** Arban (1864) and Clarke Technical Studies (1912) are PD — re-engrave them (modern editions have their own copyright). Cichowicz is modern; keep it private.
- **Audio is always your own band/playing.** Never a famous recording.

This means you can legally publish a *real* practice surface — warmup pages + lead sheets + changes + band — to the open internet. That's the moat the scattered-tabs status quo can't match. (Full detail in the M0–M2 execution plan.)

---

## 1. The core idea: separate the *rate* problem from the *volume* problem

Your two targets are different animals:

- **5,000 @ $10/mo ($50K MRR)** — a *volume* outcome. Requires reach you don't have yet.
- **300 @ $3/mo ($900 MRR)** — your "feel great" floor. Still mostly a *volume* problem.

But you can't buy volume intelligently until you know the **funnel converts**. So the formula is: **prove the rates cheaply with a small N, then pour volume into a funnel you already know works.** Don't scale a leaky bucket.

### The validation equation

```
Paying members = Reach × Engaged% × Captured% × Activated% × Paid%
```

| Stage | What it measures | Honest benchmark (warm niche, founder-led) |
|---|---|---|
| Reach → Engaged | Does the content land? | 5–15% of reach engages |
| Engaged → Captured (email/waitlist) | Is the offer interesting? | 2–5% of engaged followers |
| Captured → Activated (opens demo) | Does the promise pull them in? | 25–40% of list |
| Activated → Paid | Will they actually pay? | 5–15% of activated (warm), 1–4% (cold) |

**The reveal:** at 10% list→paid, your 300-floor needs ~3,000 engaged emails. 1,300 TikTok followers won't get you there alone. **Reach is your real constraint — and TikTok is one channel, not the channel.** The volume unlock is cross-posting into where jazz learners already cluster: r/trumpet, r/Jazz, trumpet/jazz Discords, adult-learner Facebook groups, YouTube Shorts, Instagram Reels. Same content, 5 surfaces.

---

## 2. The formulaic milestone ladder

You asked for milestones set formulaically, not by vibe. Here's the ladder. Each gate is a **diagnostic** — if you stall at a rung, it tells you *exactly* which rate is broken, so you fix that instead of guessing.

| # | Milestone | Threshold | What it proves | If you stall here, the problem is… |
|---|---|---|---|---|
| **M0** | Demo live + instrumented | Hosted URL + email capture + analytics working | You can measure | (just ship it) |
| **M1** | **Message resonates** | 50 waitlist emails | People want the *promise* | Your POV / hook / offer — not the product |
| **M2** | **Interest has depth** | 25%+ of list opens demo; 15+ feature votes | The promise → real curiosity | Activation: the demo's first 30 seconds |
| **M3** | **Willingness to pay** ⭐ | **30 founding members paying** | The economic thesis is real | The offer / price / value gap |
| **M4** | **Floor** | 300 paying @ $3/mo | Repeatable + worth your time | Volume — pour reach into proven funnel |
| **M5** | **Target** | 5,000 @ $10/mo | Business | Scale + retention + pricing power |

**M3 (30 paying founding members) is your real 90-day win.** It's small enough to hit fast, big enough to compute a true conversion rate and read week-1 retention. Everything above M3 is a *volume* problem you only earn the right to solve after M3 proves the rates. M4/M5 are the runway, not the 90-day bar.

**Decision rule at each gate:** hit it → advance. Miss it after a fair test (≥ 8 posts, ≥ 2 weeks) → don't push more volume; fix the named upstream rate first. This is the whole point of formulaic: *volume never fixes a broken rate.*

---

## 3. The sequenced 13-week plan

### Phase 0 — Ship & instrument (Jun 29 – Jul 12, wks 1–2) → gate: M0

Get something clickable and measurable live. Resist polishing.

- **Host the lite Woodshed.** Cloudflare Pages or Vercel free tier — static HTML deploys in minutes, free, fast, custom domain. Strip the lite version to your 3 best "wow" tunes + the backing band + a couple overlays. One screen, no login.
- **Add email capture.** Tally or Formspree embedded form — no backend. "Get early access / vote on what I build next."
- **Add a feature-vote board.** Canny (free) or Featurebase — lets people vote and creates investment + a public roadmap you can post about.
- **Instrument it.** Plausible or simple analytics: track visits, demo plays, email submits, votes. You can't run the ladder if you can't see the rates.
- **Founder-membership rail (stub now, charge in Phase 2).** Stripe Payment Link or Lemon Squeezy/Gumroad (handles tax). Don't build billing — use a hosted link.

**Exit:** URL is live, an email lands in a list, a vote registers, analytics fire.

### Phase 1 — Content engine + list (Jul 13 – Aug 9, wks 3–6) → gate: M1, then M2

Turn the trumpet feed into a funnel. The play stays; you add a **POV** and a **CTA**.

- Lock the POV + pillars (Section 4).
- Post on the weekly formula (Section 5). Every post ends with a soft CTA to the demo/waitlist.
- Cross-post the same cuts to Reddit / Shorts / Reels / Discords to break the 1,300-follower ceiling.
- **Watch leading indicators, not followers:** save rate, share rate, watch-through, and *waitlist adds per post*. Saves/shares > likes — they signal "this is useful," which is what converts.

**Exit:** M1 (50 emails). Then push activation to M2 (25% open demo, 15 votes).

### Phase 2 — Activate & pre-sell (Aug 10 – Sep 6, wks 7–10) → gate: M3

Now ask for money — framed as founding membership, not a subscription.

- **Founders offer:** "First 30 founding members lock in $3/mo for life + name on the wall + direct line on the roadmap." Scarcity + status + co-creation. (Price-test: a one-time $20–30 "founder pass" often converts higher than $3/mo for a pre-revenue niche tool — run both as A/B if you have the volume.)
- Drive the warm list → demo → founders link. Email the waitlist directly; DM your most engaged followers.
- Use the vote board as content: "You voted, here's what's shipping." Closing the loop is the highest-trust content you have.

**Exit:** M3 — 30 founding members paying.

### Phase 3 — Read & decide (Sep 7 – Sep 27, wks 11–13)

- Compute the real funnel: actual Reach → Engaged → Captured → Activated → Paid.
- Read retention: are founders still using it in week 3?
- **Decision:** Scale (rates work, go raise reach toward M4) / Iterate (one rate is the bottleneck, fix it) / Park (no willingness to pay — you learned it for ~$0 and 90 days, which is a win).

---

## 4. Content POV & pillars

Right now you post *performances*. Performances earn reach but not identity or conversion. Add a **point of view** so people follow a person building something, not just a guy playing.

**The POV (pick the lane that's true to you):**
> *"Adult, mid-career, rebuilding — learning to actually play jazz, and building the practice tool I wish existed. Woodshedding in public."*

That frame does triple duty: it's relatable (adult learner), it's differentiated (you're *building*), and it earns the CTA naturally (the tool is part of the story).

**The recurring hook that ties POV to product: consolidation.** "My practice used to live in six tabs across three devices" is a problem every player feels. It's the most shareable version of the build story and it sells the wedge without sounding like an ad. Lead with the mess, show the one surface.

**Four pillars (rotate them):**

1. **The Play** — what you already do: performance + Woodshed overlay. *Job: reach.*
2. **The Build** — building Woodshed in public; comping engine, real drums, the reel studio. *Job: differentiation + maker audience.*
3. **The Take** — sharp, specific POV on practice, jazz, learning as an adult ("stop practicing scales like this," "the Real Book lies to you about…"). *Job: saves, shares, authority.*
4. **The Ask** — feature votes, "what should I build," demo CTAs, founder calls. *Job: capture + conversion.*

The Take pillar is your unlock. Performances are a commodity on music TikTok; a strategist's *point of view* on learning jazz is not.

---

## 5. The posting formula (built for 5–8 hrs/wk)

**Batch once, drip all week.** One 2–3 hr weekend block to film/cut; schedule the rest.

**Weekly cadence: 5 posts.**

| Day | Pillar |
|---|---|
| Mon | The Take (hook-y, saveable) |
| Tue | The Play |
| Wed | The Build |
| Thu | The Play |
| Fri | The Ask (vote / demo CTA) |

Cross-post each to ≥ 2 other surfaces (Reels, Shorts, a relevant subreddit/Discord). That's ~15 touches/week from 5 source pieces. **Followers are the vanity metric; waitlist-adds-per-post is the one that matters.**

### 10 starter post concepts

1. *(Take)* "I'm an SVP by day. Here's how I practice trumpet in 20 minutes before work." — relatable, system-y, saveable.
2. *(Build)* "My practice used to live in 6 tabs across 3 devices." Screen-record the messy before → the one Woodshed surface. The consolidation hook, visualized.
3. *(Take)* "The Real Book won't teach you to swing. Here's what actually did." — spicy, specific, sharable.
4. *(Play)* A clean performance with the overlay — but caption it with the *struggle* ("took me 40 takes").
5. *(Ask)* "Building a jazz practice tool. What's the one thing that'd make you actually practice? Vote 👇" → vote board.
6. *(Build)* Comping engine demo: same tune, Evans vs. Garland vs. Jamal feel. "Pick your pianist."
7. *(Take)* "Woodshedding as an adult hits different. Nobody's grading you. That's the problem and the gift."
8. *(Play)* Duet-with-yourself / overlay storytelling — lean into the "creative canvas" you mentioned.
9. *(Ask)* "First 30 people get founding access for $3/mo, locked forever. Link in bio." (Phase 2)
10. *(Build)* "You voted. Here's the feature shipping this week." — close the loop publicly.

---

## 6. Weekly operating cadence (your 5–8 hrs)

| Block | Time | What |
|---|---|---|
| **Sun — Batch** | 2.5 hr | Film/cut the week's 5 posts; write hooks + CTAs; schedule. |
| **Mid-week — Engage** | 1 hr | Reply to comments/DMs; drop cross-posts in Reddit/Discord; talk to people. |
| **Fri — Read the dashboard** | 0.5 hr | Log the week's numbers vs. the ladder. Which rate moved? |
| **Flex — Product** | 1–3 hr | One small Woodshed improvement, driven by the top vote. |

Once a month, spend the Friday block computing the full funnel and checking it against the milestone ladder.

---

## 7. The one-number dashboard (track weekly)

Reach · Engaged% · **Waitlist adds** · Demo opens · **Activated%** · Votes · **Paying members** · Week-3 retention.

Bold = the ones that actually predict the business. Everything else is texture.

---

## 8. Risks & honest tradeoffs

- **Reach ceiling is the real bottleneck, not the product.** Most of your effort should go to top-of-funnel + the Take pillar, not polishing Woodshed. Resist the engineer's urge to keep building.
- **iReal is the obvious "why not just use X."** Have the one-line answer ready everywhere: you're not replacing iReal's jam engine, you're consolidating the *whole session* into one consistent surface. If a community pushes back with "iReal already does this," that's a positioning test, not a threat — lean into workflow/consistency, not feature parity.
- **$3/mo may underprice and undersignal.** Cheap can read as low-value to a hobbyist who'll happily pay $15 for a tool they love. Test a one-time founder pass against the $3 sub.
- **Subscription churn in hobby tools is brutal.** M3 isn't done at "30 paid" — it's confirmed at "30 paid *and still using it in week 3*." Retention is the real validation.
- **Cross-posting can read as spam.** In Reddit/Discord, give value first (insights, free charts), pitch second. Be a member, not a marketer.
- **Time risk.** 5–8 hrs/wk only works if you batch. Ad-hoc posting will quietly eat your evenings and still underperform.

---

## 9. This week (Jun 29 – Jul 5)

1. Deploy the lite Woodshed to Cloudflare Pages/Vercel — 3 best tunes, one screen.
2. Embed a Tally waitlist form + stand up a Canny vote board.
3. Add Plausible; confirm visit/play/submit events fire.
4. Write the POV one-liner and your 4 pillars in a note.
5. Batch + schedule your first 5 posts. Post #5 (the Ask) drives to the vote board.

Hit M0 this week. M1 (50 emails) is the only thing that matters in July.
