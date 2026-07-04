# Feature Brief — Scan & Practice Tab (v2, corrected)

New tab in the main Woodshed app (`index.html`, not woodshed-lite). Parent item: #1 in `WOODSHED-BACKLOG-2026-07-02.md`.

**v1 of this brief wrongly reached for OMR/homr (auto note-reading). Scrapped per Chris — not production-viable, not the actual need. Real trigger: he got 4 printouts from his band director last night and wants them living in one practice surface, not scattered paper.** Everything below is manual-entry-first, no ML/OMR anywhere.

## Goal

One home for physical sheet music (director handouts, etc.): clean it up like a scanner app, keep it with everything else you practice, play it with a metronome, and — since typing in chord changes for a handful of charts is genuinely fast — get the backing band and reference recordings too.

## Core flow

1. **Upload** — photo(s) or PDF. Support multiple pages per piece (a handout is often 2+ pages).
2. **Scan-itize** — the CamScanner move: detect the page edges in the photo, perspective-correct it flat (un-skew the angle you shot it at), then apply a contrast/threshold pass so it reads as clean black-text-on-white rather than a photo of paper (CamScanner calls its presets "Magic Color" / B&W / Grayscale / Original — worth picking one default rather than exposing all of them day one). Multi-page uploads stitch into one entry. This is standard document-processing (edge detection + perspective transform + adaptive threshold), not music-specific — no OMR, no ML model.
3. **Save to a personal library** — a "My Charts" style shelf alongside the Real Book/Arban content, browsable like everything else in the app.
4. **Metronome inline** — already built (Web Audio metronome, used elsewhere in the app) — just needs to render next to this new viewer. No new audio work.
5. **Chords (manual)** — a simple type-in UI for the changes, one time per chart. This plugs straight into chord-symbol parsing and the backing-band generator that already exist (walking bass/ride/piano) — the band engine doesn't care whether the chords came from iReal import, a curated tune, or you typing them in. This is the cheapest bonus on the list: no new synthesis, no new reading capability, just a form.
6. **Video links (manual)** — paste a YouTube URL for the original recording and/or a backing-track loop, same mechanism the app already uses for the 13 curated `CANON` tunes, just exposed as a per-chart field instead of hardcoded in code. No API key needed (see below).

## One shortcut worth checking before building from scratch

There's an existing but **dormant** "My Charts" browser in the codebase (`renderUserCharts` / `#mycharts-host`) that was built during the transcription work but never wired up (nothing was populating it). Haven't re-verified this is still true, but if it's close to functional, it could shortcut step 3 significantly — worth a quick look at current code state before scoping this as new-from-zero.

## Why manual, not auto, everywhere

You said it yourself — manual chord entry "feels really possible," and that's the right read: typing changes for 4 charts is minutes, not hours, and it's 100% reliable, versus auto chord-symbol OCR which doesn't exist anywhere in the stack and would need real R&D to even attempt. Same logic on video: pasting a link is trivial; a live YouTube search embed hasn't worked since Nov 2020 (Google killed `listType=search`), and the "correct" replacement is a Data API integration you don't need if you're picking the video yourself anyway.

## Monetization (decided 7/3)

Considered: gate the tab at 3 free uploaded songs, charge to upload more.

**Verdict: keep the gate concept, don't build it as a standalone paywall.** A metered "3 free, pay for more" mechanism needs two things that are explicitly deferred in `STACK-AND-SEQUENCING.md` — per-user accounts (to know who uploaded what) and metered billing (not a flat price). That ADR names building auth/billing ahead of M3 as *the* leaky-bucket-scaling mistake to avoid, and we're still pre-M0/M1.

**What to do instead:**
- Ship the tab free and uncapped now. It's good Build/Ask-pillar content on its own ("upload your director handouts, one practice surface").
- Fold "unlimited charts" into the **existing** founding-membership offer (hosted Stripe link, $3/mo or the founder-pass) at M3 — one price, one CTA, no new billing mechanism.
- Pre-M3, a soft client-side count (localStorage, no login) is enough to signal the ceiling exists — nobody's motivated to game a 3-song cap at this scale, and real server-side enforcement arrives for free once Supabase Auth lands post-M3 anyway.
- Don't turn on the "upgrade to keep uploading" prompt until Phase 2 (Aug–Sep, when founding membership is actually being pre-sold). Before then it just stays free.

**Why gating on song count specifically is a good hook:** it's tied to accumulation (the pain compounds with use), not an abstract feature restriction — and Chris's own trigger event (4 director printouts in one night) blows past a 3-song ceiling immediately, which is a live signal the number is roughly right, though still worth treating as a testable hypothesis, not a locked decision.

## Open questions

1. **Scan quality bar** — is a phone-photo-through-perspective-correction good enough, or do you want to push people toward "lay it flat, shoot from directly above" for best results? Affects how much correction work the edge-detection step needs to do.
2. **Library structure** — one entry per piece, or per upload session (your 4 printouts — 4 separate entries, or one batch)?
3. **Chord entry format** — reuse the existing bar-by-bar format from iReal import (`bars={bar:chord}`), or do you want something faster to type for one-off manual entry (e.g. a text shorthand you paste in)?
4. **Worth checking the dormant My Charts UI first** — want me to look at current code state before scoping the library piece as new work?
