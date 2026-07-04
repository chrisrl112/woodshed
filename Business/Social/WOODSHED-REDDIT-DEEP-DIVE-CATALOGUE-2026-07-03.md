# Woodshed — Reddit Deep-Dive Catalogue (2026-07-03, round 2)

*Supporting detail behind the memo. 19 threads read in full (post + all visible comments), not just search snippets. Method: old.reddit.com via connected Chrome, two parallel research passes. Read-only, no posting.*

---

## Cluster A — App-juggling & practice-workflow threads

**1. r/musicians — "tired of jiggling around different practice apps"** (1 mo, 40 comments) — *the single richest thread in the batch.*
Dev pitching an all-in-one hobbyist app (metronome, notes, calendar, sheet music, recordings, timers, gig scheduling, AI practice-plan assistant).
- Wants: custom metronome tones/uploadable .wav, a metronome that simulates an actual drum pattern (not just a click), weekly lesson-driven practice checklists, per-feature toggles ("hide the calendar if I don't need it"), setlist intelligence (auto-flag songs needing more practice), shared setlists for bandmates, lyric tracking.
- One detailed strategic comment (u/Scott_J_Doyle): not the target user himself, but predicted a real niche among **hobbyists wanting a single "master app," explicitly not professionals**. Recommended messaging around reducing overwhelm, adding streaks/leaderboards, and **explicitly advised against subscription pricing** — "the angle is less hassle."
- Pushback: one commenter asked if it was "vibe coded" (AI-generated); OP said AI-assisted builds were "catastrophic," now hand-built with AI only for code review. AI-shell apps read as low-trust here.
- Practice-journaling is contested even within this thread — some want it, most engaged critic elsewhere (Cluster below) calls tracking itself "more work that takes me away from the actual process."

**2. r/trumpet — "how do you keep your musical life organized" (OpusMode)** (2 mo, 2 comments)
A DCI/big-band lead (power user, ~1000 charts already organized on a tablet) pushed back hard: "notes organization is a well trodden path... I would not be re-inventing the wheel here. Spend that time practicing," and "it's going to be hard to make a product flexible enough to meet the needs of a large cross section of musicians." Direct pro-segment skepticism of consolidation pitches.

**3. r/trumpet — "Fake Book Index App"** (2 mo, 5 comments) — narrow utility (search 90+ fake books for a tune/page), one-time purchase, no ads/account. Entirely positive, zero pushback. "I already appreciate the 'one time purchase' model." Android launched first, iOS request followed, then delivered — a completed request→build→ship→download loop.

**4. r/trumpet — "Woodshed Drills" TestFlight ask** (2 mo, 3 comments) — **naming collision.** A different developer's music-theory drill app, live domain woodsheddrills.com, active TestFlight, promoted in r/trumpet — the same word "Woodshed," same subreddit Chris would use. No product feedback in the thread (purely technical tangent), but the collision itself is real and current.

**5. r/trumpet — "TonArt Coach" ("built an app instead of practicing")** (7 mo, 3 comments) — shallow, uniformly positive ("there aren't many good trumpet apps"), no critical feedback.

**6. r/trumpet — "Improv Backing Tracks?"** (11 mo, 9 comments) — a genuine user ask, resolved entirely with free YouTube channel/video recommendations. No app was mentioned by any commenter. Signal: for "give me something to blow over," YouTube is perceived as fully adequate — the bar for a paid/dedicated backing-band feature is "why switch from free," not just "better than iReal."

**7. r/Jazz — "Jazz Piano App" (dev asked "what annoys you")** (6 mo, 10 comments) — more skeptical, purist tone than thread #1.
- Top comment: exhausted by "obviously LLM-written" pitch posts; jazz culture prizes "truth and individuality" over polish.
- A working musician: no substitute for "listening, transcribing, playing along with transcriptions"; explicitly warned against gamification, citing deleting Duolingo for the same reason; called practice tracking "more work that takes me away from the actual process."
- Joke replies about simulating gig-room noise/pressure — underneath the joke, real skepticism that software can replace performance pressure.

**8. r/Jazz — "Quartet vs. FeelBook apps"** (5 mo, 13 comments) — richest direct competitor-intel thread.
- "IReal is still king" — larger catalog, tempo/key flexibility, user-importable charts (competitors' real-recorded audio can't support custom charts).
- FeelBook: subscription pricing rejected ("NO to any subscription, and NO to any US-based company"), small catalog (~50-70 tunes) but growing, audio quality praised.
- Quartet: ~$50 one-time, 500+ tunes, no subscription, UI criticized (wonky search, unreliable save, forced landscape, per-song ensemble settings don't persist, un-skippable intros).
- Band-in-a-Box raised as pricier/uglier but deeply customizable; lacks "cohesive ensemble feeling."
- Storage-footprint concern raised for pre-recorded-audio apps — relevant since Woodshed's engine is algorithmic/generated, not sample-heavy.

**9. r/trumpet — "Reharmonize" (chord-similarity tune finder)** (2 mo, 5 comments) — best-quality single feedback exchange in the whole batch, from a trumpet teacher:
- "Fills a hole that I think is needed"; would use weekly, not daily — a useful reminder that not every feature needs daily-habit framing to be valuable.
- Unprompted, concrete willingness to pay: **"I would pay $20 flat to use Reharmonize if I had to."**
- Audience-targeting language: good fit for "conservatory students and serious adult learners," not beginners.
- OP shipped a real bug fix directly from this conversation — fast iteration loop.

**10. r/Jazz — "Jazz Library"/"CleverJazz"** (1 yr, 4 comments) and **"Jazz Pad"** (9 mo, 6 comments)
- Jazz Library's launch post was caught by Reddit's spam filter (likely the hashtag-heavy "#buildinpublic #indiedev" copy) — a real distribution-risk lesson. One user found it by googling "jazz licks app," confirming organic search intent exists. Renamed to CleverJazz roughly 8 months after the pitch — normal indie timelines.
- Jazz Pad's top comment (9 points, most-upvoted in the sub-thread): **"Further proof that musicians will do literally anything other than actually practice."** OP laughed it off. This joke recurs almost verbatim in thread #5's own post title — a mild, recurring meme risk for any new "I built a practice app" post.
- Android-support requests appear again here (a third+ independent instance across the batch) — iOS-only launches reliably draw this friction.

---

## Cluster B — iReal Pro & WeAreTheMusicMakers megathreads

**11. r/Jazz — "iReal Pro alternative"** (2 mo, 19 comments) — dev seeking Android beta testers.
- "What does it do that iReal doesn't?" — the reflexive first question any Woodshed post should expect.
- Named competitor: **The Feel Book** ("the best one out there," real recordings, no chart editing).
- Bb-instrument display requested directly (commenter's trumpet-playing wife) — validates transposition as a real ask.
- Pricing: "most important to have a one-time payment instead of a subscription... can be like 20€... I skipped alternatives that only offer subscriptions."
- iReal's playback criticized outside jazz genres (funk/soul "not so much... a bit frustrating").

**12. r/Jazz — "Building a better alternative to iReal Pro"** (2 mo, 14 comments, poll) — same dev.
- Launch-sequencing advice from a commenter: "Work incrementally. Make it possible to import your irealpro library... Real book sources can come later, even as freemium."
- Concrete gaps named: modern tunes with nonstandard head/solo forms poorly supported, clunky time-signature changes, no mid-tune style switching (can't go swing→latin within one chart), messy forum-based chart discovery, chart-accuracy complaints vs. the Real Book.
- Competitors named again: The Feel Book, Quartet.

**13. r/Jazz — "iRealPro finessing me"** (4 yr, 1 comment) — pricing/repurchase frustration after an iOS update; thin, likely a purchase-restoration confusion rather than an actual double-charge.

**14. r/musicians — "Is ForScore worth it?"** (2 yr, 3 comments) — iReal and ForScore seen as complementary, not competing ("I also love iRealPro, especially for quickly making charts"). One commenter had never heard of iReal at all — sheet-music users and chord-chart users are meaningfully different audiences.

**15. r/musicians — "Piano Bar - Getting Started"** (2 yr, 12 comments) — "I have iRealPro but it doesn't have lyrics" — gap never resolved in-thread; **Ultimate Guitar** named as an alternative for lyrics+chords together.

**16. r/musictheory — "Best app for writing charts?"** (5 yr, 6 comments) — richest chart-authoring complaint thread: "how clunky writing charts is," missing chord types entirely forcing plain-text workarounds, bar-length/overlap issues. Alternatives suggested (Finale, Sibelius, MuseScore, NoteFlight) are full notation editors, not true substitutes for lead-sheet authoring.

**17. r/musictheory — "All-in-one Songbook / Chord Map / Lyric" ask** (5 yr, 10 comments) — reads like an unsolicited spec: lyrics + chord shapes + sync across devices. iReal named but flagged incomplete ("doesn't support lyrics or chord shapes"). Competitor named: **SongBook** (linkesoft.com).

**18. r/musicians — "Cover Band Charts"** (1 yr, 11 comments) — iReal mentioned once, then dismissed — pop/rock cover culture defaults to "send the recording, learn by ear," not charts. Confirms iReal/Woodshed-style tools are a jazz/standards-niche solution, not a general-band-charts solution.

**19. r/trumpet — "Realbooks"** (2 yr, 11 comments) — **the clearest unprompted articulation of Woodshed's exact value proposition found anywhere in this research:**
> "What I really want is something like iReal Pro but with leadsheets instead of just chords."
From a trumpet player, in r/trumpet, frustrated after juggling physical books, PDFs, Kindle, iReal Pro, and a paid Hal Leonard play-along subscription. Workarounds described (CSV-bookmarked ForScore PDFs, hand-scanning Kindle pages) show real pain and no real solution today.

**WATMM Weekly Feedback Thread** (98 comments, fully loaded/skimmed) — one tool-share (Trackprint, a visual arrangement planner) got zero replies in a thread otherwise 100% song-critique. Explicit rule: one song per top-level comment, 3 constructive comments required, no promo-only replies (reported as spam). Tone: warm, hedged, zero hostility across all 98 comments.

**WATMM Weekly Promotion Thread** (68 comments, fully loaded/skimmed) — one tool-share (a free lyric-writing site) got zero replies, 1 point. "Contest mode" (randomized order) enabled to prevent vote-gaming. More one-directional/broadcast than the Feedback thread; some commercial asks tolerated without visible mod pushback.

---

## Named competitor set surfaced across all 19 threads
iReal Pro (the constant reference point) · The Feel Book · Quartet · Band-in-a-Box · SongBook (linkesoft) · Ultimate Guitar · ForScore · MuseScore/Finale/Sibelius/NoteFlight (notation, not chart tools) · therealbook.info · Fake Book Index · Reharmonize · CleverJazz/Jazz Library · Jazz Pad · TonArt Coach · OpusMode · Woodshed Drills (name collision) · useclicktrack.com
