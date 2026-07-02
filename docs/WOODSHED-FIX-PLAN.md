# Woodshed Fix Plan — Post-Session Debrief

**Date:** June 11, 2026
**Status:** for review. We align here, then execute step by step.

Two tracks. **Track A** = the six things you hit during the session. **Track B** = the "mission control" loop that turns the portal into a steerable system you drive each morning.

---

## Track A — Session fixes

### A1. Per-block logging (and kill the standalone Journal)

**Problem:** No way to log per block; the Journal is a separate afterthought.
**Fix:** Every block — in Focus Mode *and* on its tab section — gets an inline **Log** field: one freeform note plus a couple of quick structured signals where they matter (e.g. a "ready to advance" toggle, a "tempo reached" number on the speed blocks). Stored per day, per block (`S.blockLogs[date][blockIdx]`).
**Journal:** Removed as a standalone block. Journaling is now distributed across blocks. The closing block becomes **"Lore + Day Review"** — it shows the day's lore/commute listening *and* auto-compiles everything you logged into one summary (that summary is exactly what Track B exports).
**Why it matters:** these logs are the fuel for the whole morning-rebuild loop.

*Your examples this would capture: "ready to go to group E for Cichowicz, keep lip slurs and range as is, a little shaky" · "decent at 100 bpm, trouble at 110" · "tune almost memorized... keep in rotation this week."*

### A2. Group + name the Gym on "Today's 6"

**Problem:** The two gym blocks (Flows + Slurs, Clarke) read as unrelated cards.
**Fix:** Add module-group headers to the Today grid — a **GYM** label spanning both gym cards, then VOCAB, TUNES, EARS over their blocks. Same grouping logic everywhere.

### A3. Warmup / Clarke — real pages, not fabricated notation

**Problems:** The "Quick-reference cell in F (No. 26 shape)" is **wrong**. The Clarke Second Study is **2 pages** but only one is shown.
**Fix:**
- Delete the generated quick-ref ABC cell entirely. Show the **actual book-page screenshot** (we already render the real PDF page) — no synthetic notation where a real page exists.
- Generalize book sections to support **multiple pages**: render both pages of the Second Study side by side, and any other multi-page study.
- Keep the lip-slur and range notation as-is (you said those are good).

### A4. Vocab / Riffs — real licks, real ii-V-I

**Problems:** The licks are theoretically correct but don't *sound* good. "Hear it" plays over one chord; the backing loop is just a blues in the key. Ear-First isn't the default, so you see the lick immediately.
**Fix:**
- **Research and transcribe real, vetted vocabulary** — canonical blues licks and ii-V-I lines that actually sound like the language. Store them as explicit transcribed lines (so they sound right and transpose cleanly), weighted toward **ii-V-I**.
- **Backing loop becomes a 4-bar ii-V-I:** 1 bar ii · 1 bar V · 2 bars I, looping. "Hear it" plays the lick *over that progression*, not a single chord.
- **Ear-First is the default** — lick hidden/blurred until you reveal it.

### A5. Tunes "Solo with the band" — rebuild what we agreed

**Problem:** The layout we agreed on didn't survive the merge.
**Fix (rebuild):**
- **Left:** the 1-page music sheet. **Right:** chords + play button + band controls.
- **Below:** a looping **chord-tone outline** — for each chord in the tune, a short cell that lands the **3-5-7-9-1** (chord tones, any sensible order) and chains across the changes, playable with the band. This is the "outline the changes" trainer you wanted.
- **Backing track realism:** it feels robotic. Options below — you pick the mix.

*Your log this would capture: "chords I can play over from memory but not perfect at outlining them — keep in rotation this week."*

### A6. Daily Ears → real transcription

**Problem:** It's an interval quiz that doesn't match its own instructions.
**Fix:** Make Daily Ears an actual **transcription exercise** — load a solo (the week's tune's recommended recording), 0.5× playback, transcribe a measure or two, log what you got. Instructions and tool finally match. Interval trainer stays available as a side tool, not the main event.

---

## Track B — Mission Control (the daily steer-and-rebuild loop)

Your vision, made concrete:

```
   [1] Practice + log per block   (in the app)
            │
            ▼
   [2] App writes the day → logs/2026-06-11.md
            │
            ▼
   [3] Morning scheduled task reads the log + mission-control.json
       + any feedback you gave that morning
            │
            ▼
   [4] Updates mission-control.json  (rotation, rungs, objectives,
       what's being reviewed) AND rewrites index.html for the day
            │
            ▼
   [5] You open a freshly-tuned Woodshed + a short morning brief
```

**The running state lives in `mission-control.json`** — the backend brain: tunes being served, weekly objectives, monthly objectives, review schedule, rung status, PR targets. Today this is buried in browser localStorage; we promote it to a file the morning agent can read and steer.

**One real constraint:** a browser can't silently write files to disk. Three ways to bridge app → folder (pick one in the decisions):

| Bridge | How | Friction |
|---|---|---|
| **Local endpoint** *(rec)* | Extend your `Start Woodshed.command` server to accept the day-log and write it to `logs/` when you click "Save day" | None — one click |
| Manual export | "Download today's log" → you drop it in `logs/` | One save per day |
| Chat-driven | Each morning you tell Cowork how it went / paste the log | Most manual, most flexible |

**Phasing:** Track A first (makes logging real and worth capturing) → then the export bridge + `mission-control.json` → then the scheduled morning task that reads, steers, and rebuilds. The loop is only as good as the logs feeding it, so A1 is the keystone.

---

## Decisions for you

1. **Start order** — Track A first (my rec), or stand up a thin slice of the loop early so logging has somewhere to go?
2. **Backing-track realism** — which improvements (you can pick several).
3. **Licks sourcing** — how I get the better vocabulary.
4. **Loop bridge + automation** — how the app hands off, and how much the morning task does on its own.

I'll ask these as quick picks next so we can lock the sequence and start step one.

---

## Recommended sequence (my default if you're happy)

1. **A1** per-block logging + Day Review (keystone)
2. **A5** Tunes solo rebuild (highest daily value)
3. **A4** real licks + ii-V-I loop (biggest content lift — research-backed)
4. **A6** Daily Ears transcription
5. **A3** real Clarke pages + multi-page studies
6. **A2** Today's-6 grouping (quick polish)
7. **Track B** export bridge → `mission-control.json` → morning scheduled task
