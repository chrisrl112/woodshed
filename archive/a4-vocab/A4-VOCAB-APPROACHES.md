# A4 Jazz Vocabulary → Woodshed — Approaches Log & Next Options
*Paused 2026-06-13. Chris fatigued with failure; revisit fresh.*

## What we tried (and why each fell short)
1. **Hand-authored offset arrays** ("in the style of"). Theoretically correct, didn't *sound* like the language. Rejected.
2. **OMR from Real Book PDF scans.** Reading dense/handwritten notation from images is error-prone; transcriptions were "almost good but weird." Rejected.
3. **Weimar Jazz Database (WJazzD) auto-windowed ii-V-I extraction.** Pitches exact, deterministic — but auto-chosen windows were decontextualized "weird snippets." Rejected.
4. **WJazzD + human picks from rendered solo charts.** Right idea (Chris's ear selects, pipeline snips). But engraving performance data into clean readable notation kept producing problems (over-sustain, choppy 16ths, spurious accidentals, chord-label clipping). One lick (Chet Baker, "Let's Get Lost" bars 9–11) was approved and locked before fatigue set in.

**Core lesson (corrected):** WJazzD is *performance* transcription — accurate to the recording's micro-timing, but **NOT a clean source for vocabulary.** Chris's read: the timing is messy/weird and the rhythms don't clean up; many solos carry odd subdivisions (quintuplets/septuplets/etc.). So the problem was BOTH (a) source-data quality for this purpose AND (b) engraving performance timing into readable notation. **Do not treat WJazzD as a clean "answer key" next time.** Favor sources that are already clean/idiomatic (method books, hand-entered lines, or Chris playing them in) over any performance-transcription database.

## Assets already built (reusable next time)
- `wjazzd.db` (456 real solo transcriptions, note-level + chords) in this folder.
- `tools/wjazz_extract.py` — finds ii-V-I windows, maps to the app's lick format (deterministic).
- `tools/solo_av.py` — renders any solo (or bar range) to chart PNG + matching audio WAV.
- `tools/render_lick.py` — renders a single chosen lick to chart + audio for approval.
- `tools/solo_audio.py` — pure sonification of any solo (verified faithful).
- One approved lick installed: **L1** in `index.html` `LICKS`. Backups: `index.html.bak-20260613-*`.

---

## Four fresh approaches to try next time

### Approach A — Method-book vocabulary, entered once (skip transcription entirely)
Type in 15–20 canonical lines from a trusted source you already respect (Aebersold ii-V-I vol., Coker *Patterns for Jazz*, Bergonzi *Melodic Structures*), as clean data by hand, verified by ear in the app.
- **Dodges:** no OMR, no engraving-from-performance, no decontextualized snippets.
- **Effort:** low–medium (manual entry). **Risk:** low. **Quality:** high, fully under your control.
- **Needs:** you pick the source book; ~1 sitting to enter + ear-check.

### Approach B — MIDI-first, never engrave
Build the whole feature around MIDI/note-events, not notation. Import lick MIDI (Omnibook MIDI sets, transcription MIDIs), audition by **ear** in the app, store as note-events. Notation becomes optional/decorative.
- **Dodges:** the entire engraving rabbit hole — the thing that actually kept failing.
- **Effort:** medium. **Risk:** low–medium (sourcing MIDI). **Quality:** high (audio is the bar, and audio always worked).
- **Needs:** a MIDI lick source; a simple in-app "play / keep / cut" auditioner.

### Approach C — Capture your own vocabulary (you play it in)
You're the player. Add a "capture a lick" mode: play a 2-5-1 into the mic, the app records it (and/or pitch-detects), tags it with the changes, stores it. Your phrasing, your tone, zero transcription error.
- **Dodges:** transcription AND engraving entirely; pedagogically ideal (your own voice).
- **Effort:** medium (leverages existing tuner/pitch infra in the Woodshed). **Risk:** medium (pitch detection accuracy if you want notation; trivial if audio-only).
- **Needs:** decide audio-only vs. pitch-to-notation; a record/tag UI.

### Approach D — Learn whole solos, not snippets (reframe the feature)
Drop "isolated licks." Instead load a full solo (audio + the chart we *can* generate well enough at solo scale) and practice play-along / transcription against it. Vocabulary enters in context, the way players actually absorb it.
- **Dodges:** the "weird decontextualized snippet" problem you flagged from the start.
- **Effort:** medium (mostly already built — `solo_av.py`). **Risk:** low. **Quality:** high musically; changes the feature's intent (study vs. drill).
- **Needs:** your call on whether the Woodshed should host "solo study" alongside lick drilling.

---

## Recommendation for the restart
Start with **A or B** for a fast, trustworthy win (a small set of lines that definitely sound right), and consider **D** as the longer-term feature reframe. **C** is the most "you" and worth a spike once the basics work. Avoid re-entering the OMR / engrave-from-performance path — that's the proven dead end.

**Decision to make first:** audio-only vocabulary (fastest, always worked) vs. notation-backed (prettier, but the hard part). Pick that and the approach follows.
