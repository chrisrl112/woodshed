# Woodshed Backlog — July 2 Brainstorm

Source: whiteboard dump, Thu 7/2 9:59pm. Six buckets, eight items circled/numbered as priority order. Briefs below are a first pass — flag anything I've misread or mis-scoped.

---

## Priority order (as numbered)

### 1. PDF viewer + metronome — *Features* → **now scoped, see [WOODSHED-BACKLOG-UPLOAD-TAB-BRIEF.md](WOODSHED-BACKLOG-UPLOAD-TAB-BRIEF.md)**
**What:** New main-app "Scan & Practice" tab — upload photo/PDF printouts (e.g. band-director handouts), clean them up scanner-app style, keep them in one practice surface with a metronome, and add chords (typed in manually) + reference YouTube links (pasted in manually) so the existing backing-band engine can play along.
**Status:** Scoped 7/2, corrected same day — first pass wrongly reached for OMR/auto note-reading (not viable); real spec is manual-entry-first, no ML anywhere. Full flow + open questions in the linked doc.

### 2. Arban chop up — *Features*
**What:** Slice the Arban Method PD scan into usable sections.
**Context:** This is **already done** — `pipelines/arban-source/` indexed and chopped all 355 pages into 51 named sections, same day (7/2), verified page-count-complete. So either you wrote this before finishing it that night, or "chop up" actually means the next step: running sections through the transcription pipeline (homr → ABC) so they show up as real exercises in the app.
**Open question:** Is this item now "done, cross it off" or does it roll into #5 (more exercises)?

### 3. Reddit research — *Social*
**What:** Scope which subreddits are worth engaging (r/trumpet, r/Jazz, r/WeAreTheMusicMakers, etc.) for early-adopter discovery and feedback.
**Context:** Feeds directly into the validation gameplan's M1 target (50 waitlist emails) and M2 (15 votes) — Reddit is a plausible top-of-funnel for people who'd actually want a jazz practice tool.
**Open question:** Research-only (find the right communities + norms) or research + first posts?

### 4. TikTok — message — *Social*
**What:** The core content pillar / point of view for TikTok — what the account is actually saying, distinct from a specific video's opening line.
**Context:** You separated this from "hook" below, which is the right instinct — message = positioning, hook = per-video execution.
**Open question:** Is the audience "jazz/trumpet players" (product-market fit for Woodshed) or "career/AI-builder" (personal brand, adjacent to your Circana/strategy identity)? Changes the message entirely.

### 5. More exercises on mainpage — *Features*
**What:** Expand the exercise content surfaced on the front page.
**Context:** Downstream of #2 — Arban sections are chopped but not yet transcribed into the app's format. This is the "make the backlog of content actually visible to a user" step.
**Open question:** Same surface question as #1 — main app front page, or woodshed-lite demo page (which needs content to justify the "PDF viewer + metronome" tool)?

### 6. Landing page tweaks — *Design*
**What:** Adjustments to the public landing/voting page.
**Context:** This is woodshed-lite, currently in the M0→M1 validation stage (get to a live demo, then 50 waitlist emails).
**Open question:** What's not working — conversion, copy, mobile layout, something else? A "tweaks" list needs a specific complaint to be actionable.

### 7. Logo — *Branding*
**What:** A proper mark for the Woodshed.
**Context:** You already have a locked visual language (Blue Note sleeve aesthetic — warm paper #f2ecdf, ink, one hot orange #e84e10, Archivo Black) and a favicon/apple-touch-icon in place. This reads as "give that identity an actual logotype/mark," not starting from zero.
**Open question:** Wordmark only, or wordmark + icon (for social avatars, favicon replacement)? Any reference marks you like?

### 8. Revisit targets/KPIs — *Strategy*
**What:** Re-check the validation ladder.
**Context:** `docs/woodshed-validation-gameplan.md` already has a concrete 90-day M0→M5 ladder (M1: 50 waitlist → M2: 25% open + 15 votes → M3: 30 paying founding members — the real 90-day win → M4: 300@$3 → M5: 5000@$10), set Jun 28.
**Open question:** Is this a progress check-in against those existing numbers, or do the numbers themselves need to change based on what you've learned since Jun 28?

---

## Unranked backlog (no circle, still on the board)

- **TikTok — hook**: per-video opening lines/patterns. Downstream of #4 (message) — do this after, not before.
- **TikTok — experiments**: a format-testing plan (what to vary, how you'll know something worked).
- **TikTok — analytics**: tracking setup — views/follows/waitlist-conversion attribution from TikTok specifically.
- **LinkedIn**: separate channel, separate audience question — same as #4, is this Woodshed-audience or personal-brand?
- **Survey**: an audience/customer survey — likely feeds M2/M3 (pricing sensitivity, feature priority for founding members). Could be the single highest-leverage item here if M3 (30 paying) is the real goal.
- **Agentic — model routing**: least clear item on the board. Could mean routing logic inside a Woodshed feature (e.g. the feedback agent, or a future practice-coach agent picking cheap vs. capable models per task), or could be a personal AI-workflow-library item unrelated to Woodshed specifically.

---

## What I'd want to nail down before assigning real effort

1. **#1 and #5 (and the demo/main-app split)** — same underlying question, worth answering once: is the current push about the *private practice app* or the *public woodshed-lite demo*? The validation-ladder context (targets/KPIs, landing page, Reddit, TikTok) suggests the demo is the actual priority right now, and Features items 1/2/5 should serve that, not the private app.
2. **#4 + LinkedIn** — one audience decision (trumpet/jazz players vs. your own professional brand) that determines message, hook, and content plan for both channels at once.
3. **Agentic/model routing** — needs one sentence of intent before I can scope it at all.
4. **#2 Arban** — confirm whether to just check this off or fold it into #5.
