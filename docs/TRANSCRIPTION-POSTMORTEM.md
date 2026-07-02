# Transcription Post-Mortem — Sourcing Jazz Vocabulary for the Woodshed

**Date:** 2026-06-13
**Purpose:** Feeds the **wood-12** decision ("pick the sheet-music transcription strategy"). This brief informs that call; it does not make it.
**Status:** The A4 vocab effort is **PAUSED** at Chris's request (paused 2026-06-13, fatigue with the failure loop). This is a catalog of everything tried, why each fell short, and a ranked recommendation for the restart.

---

## TL;DR

- **The lesson:** every approach that tried to *engrave performance timing into clean, readable notation* failed; every approach where **audio was the bar succeeded**. The pitch data was almost always fine — the rhythm/notation step is where it broke.
- **WJazzD is performance transcription, not an answer key.** Its pitches are exact, but its micro-timing carries odd subdivisions (quintuplets/septuplets) that do not clean up into drillable bars.
- **Recommended path:** **method-book hand-entry, audio-first** (Approach A) — 15-20 canonical lines typed in once from a source Chris trusts, verified by ear, notation optional/decorative. Lowest effort, lowest risk, dodges both failure axes.
- **The one decision Chris must make first:** **audio-only vs. notation-backed vocabulary.** Everything downstream follows from that single choice.

---

## The goal & why it's hard

**What we actually need:** a small library of idiomatic jazz vocabulary (ii-V-I lines, minor ii-V-i, blues) the Woodshed app can drill — primarily **audio** the user can hear and sing back, and **optionally** clean notation on the staff. The format is the `LICKS` array (semitone-offset arrays + rhythm tokens + chord map over a 4-bar ii·V·I·I loop).

**Two distinct failure axes — keep them separate:**
- **(a) Source-data quality.** Is the *content* idiomatic and in-context? Hand-authored "in the style of" lines were theoretically correct but didn't *sound* like the language. Auto-windowed database snippets were decontextualized.
- **(b) Engraving performance-timing into clean readable notation.** Even with perfect pitch data, turning a real performance's micro-timing into a clean, drillable staff produced over-sustain, choppy 16ths, spurious accidentals, and chord-label clipping.

Almost every approach below failed on (a), (b), or both. Crucially, **audio-only sidesteps (b) entirely** — and (b) is the axis that actually kept breaking.

---

## Approaches tried — catalog

### 1. Hand-authored offset arrays ("in the style of")
- **What it was:** Lines written by hand as semitone-offset arrays that faithfully use a named device (bebop scale, enclosure, 3-to-9, tritone sub, etc.), transposing cleanly into the 4-bar ii-V-I shape. This is how L1-L10 and the A4 pack (L11-L21) were built.
- **Worked:** Structurally perfect — all 11 A4 lines pass the validator (spans=16, note-counts match, range/transposition fit). Device theory is textbook-canonical. **High confidence on correctness.**
- **Fell short:** They are *idiomatic adaptations, not transcriptions* — honestly labeled "adapted" in `src`. The earliest hand-authored attempts "didn't *sound* like the language" — theoretically correct, musically generic (scale-practice feel). Rejected as the primary method.
- **Current state:** A4 pack (L11-L21) is **built and validator-clean but NOT merged** (paused before integration). L1-L10 already live in `index.html`. No measured "sound-quality" accuracy figure exists — judgment is by ear `[confirm: no numeric quality metric]`.

### 2. OMR from Real Book PDF scans (ad-hoc)
- **What it was:** Read dense/handwritten Real Book notation directly from page images into notes.
- **Worked:** Conceptually the dream (photograph a chart → playable).
- **Fell short:** Reading dense/handwritten notation from images is error-prone; transcriptions came out "almost good but weird." Rejected.
- **Current state:** Rejected as an ad-hoc approach; this motivated building the dedicated `omr-engine` (see #3). No standalone accuracy number for the ad-hoc attempts `[confirm]`.

### 3. The dedicated `omr-engine` skill (pure-algorithmic OMR)
- **What it was:** A from-scratch, eval-backed OMR engine (`omr.py`, numpy + PIL, no ML) to read single-staff treble-clef music — engraved renders and hand-drawn/photocopied Real Book pages — into `(x, pitch, dur16)` events, emitting JSON or ABC. Packaged as a skill (Stage 6 done).
- **Worked — and this is the most technically successful artifact in the project:**
  - **Pitch is near-perfect.** Engraved notes-only (seeds 0-49): **100% count / 100% pitch / 100% duration.** Random-key eval (G5): **13/13, ~99.8% pitch.**
  - **Accidentals (G3):** ~92% pitch (12/13).
  - **Hand-drawn gate (G4):** licks page **line 1 = 22/22 count/pitch/dur** (perfect on one verified line).
  - **Real Book key signatures (G6):** **6/6 pages**, ink-verified on Chris's hand-lettered Bb Real Book scan, zero false positives across 46 systems.
  - **Dotted quarter (G7):** **39/39 = 100%.**
- **Fell short (the limits that matter for vocabulary):**
  - **No triplets** (the hardest case, deferred) and **no tie-duration merging** (tie arcs are suppressed so they don't phantom-read, but two tied notes return as two notes, not one summed duration).
  - **Dotted eighth in a beamed dotted-8th+16th: ~66%** (the hard tail).
  - **Full-transcription accuracy on real Real Book melody lines was NEVER evaluated** — G6 covers key signatures only; a full-tune melody gate is still TODO. So the headline figures are per-stage, not "transcribe a whole Real Book solo correctly."
  - No multi-voice/grand staff, no bass/alto clef, no ornaments, no chord symbols.
- **Current state:** **Built, packaged, gates green** (G1-G7). It is a genuinely strong *notation reader for clean single lines* — but it does not solve the vocabulary problem, because (a) the Real Book's value is in solos/heads it can't yet fully transcribe (triplets, ties, syncopation styling), and (b) it reads *printed* notation, which is the clean-source case, not the messy-performance case. A standalone-skill-vs-fold-into-`score-to-woodshed` decision is **deferred to Chris**.

### 4. The `score-to-woodshed` crop-read-verify loop (this is wood-12 option "a")
- **What it was:** An LLM-driven transcription loop: render the source → read in three zoom passes (page → system → bar) → write ABC → **re-render and visually diff bar-by-bar against the source** → import to the Woodshed `charts.js` (playable notation + generated backing band).
- **Worked:** The verification loop is the real value — it catches its own errors. "Sweet spot" is single-line music (lead sheets, horn parts, etudes, melodies with chords). Handles transposition correctly (concert chords = written − 2 for the Bb Real Book).
- **Fell short:** It is a careful, **manual, multi-round process** (two clean verification rounds is the *norm*; dense pages take more). It explicitly **declines piano/grand-staff/multi-voice** (top line only). Real-Book "handwritten font" needs extra zoom passes. No throughput accuracy number is published — verification is qualitative ("a transcription that hasn't been re-rendered and diffed is a guess") `[confirm: no quantitative accuracy figure]`.
- **Current state:** **Available as a skill, working.** It is the sanctioned path for turning a *printed chart* into a verified Woodshed entry. It does not by itself source idiomatic *vocabulary*; it transcribes whatever page you point it at, and it still pays the engraving-cleanliness tax on messy sources.

### 5. WJazzD auto-windowed ii-V-I extraction
- **What it was:** Use the Weimar Jazz Database (`wjazzd.db`, **456 real solo transcriptions**, note-level + chords). `tools/wjazz_extract.py` finds ii-V-I windows automatically and maps them to the app's lick format (deterministic).
- **Worked:** **Pitches are exact and deterministic** — no transcription error, real recorded language.
- **Fell short:** The **auto-chosen windows were decontextualized "weird snippets"** — failure axis (a). A machine picking the window has no ear for where the phrase actually begins and ends.
- **Current state:** Tool built and reusable (`tools/wjazz_extract.py`); approach **rejected** for auto-windowing.

### 6. WJazzD + human picks from rendered solo charts
- **What it was:** The right idea — **Chris's ear selects** the phrase, the pipeline snips it. `tools/solo_av.py` renders any solo (or bar range) to chart PNG + matching audio WAV; `tools/render_lick.py` renders a single chosen lick to chart + audio for approval; `tools/solo_audio.py` is pure sonification (verified faithful).
- **Worked:** Audio rendering worked (sonification verified faithful). Human selection fixes the decontextualization of #5. **One lick was approved and locked: Chet Baker, "Let's Get Lost," bars 9-11 → lick L1.**
- **Fell short:** **Engraving the performance data into clean readable notation kept producing problems** — over-sustain, choppy 16ths, spurious accidentals, chord-label clipping. Failure axis (b). Fatigue set in here.
- **Current state:** **One approved/locked result** (L1 in `index.html` `LICKS`; backups `index.html.bak-20260613-*`). Pipeline reusable. The notation step is the dead end, not the audio.

> **Discrepancy to note:** the A4 brief (#1) describes L1-L10 as authored "in the style of" devices (citing the device, not a recording), while the approaches log says L1 is the locked **Chet Baker** WJazzD pick. Both can be true if L1 was *replaced* by the Chet Baker pick during the WJazzD effort — but the exact current contents of L1 should be confirmed against `index.html` before relying on either description. `[confirm: current identity of L1 in index.html]`

---

## Cross-cutting lessons

1. **Audio always worked. Engraving always broke.** Every failure that caused fatigue lives on failure axis (b) — converting real performance timing into a clean staff. Sonification and audio playback were never the problem.
2. **WJazzD is *performance* transcription, not a clean answer key.** Accurate to the recording's micro-timing — which is exactly why its rhythms don't clean up. Many solos carry odd subdivisions (quintuplets/septuplets). **Do not treat WJazzD as a clean source for drillable vocabulary next time.**
3. **A machine can't pick the phrase; pitch was never the bottleneck.** Auto-windowing fails on context; the engine reads pitch at ~100%. The scarce resource is *a human ear choosing the right phrase* and *a clean rhythmic representation* — not note-detection accuracy.
4. **The OMR engine is real and reusable, but it's a printed-notation reader, not a vocabulary source.** It shines on clean single lines; it doesn't yet do the triplets/ties/syncopation that real solos demand, and full-tune accuracy is unmeasured.
5. **Favor sources that are already clean and idiomatic** — method books, hand-entered lines, or Chris playing them in — over any performance-transcription database.

---

## Ranked options forward

Scored on **Effort** (to first usable result), **Risk**, **Quality** (musical trustworthiness), and **Dodges (a)/(b)** (does it sidestep the two failure axes).

| # | Path | Effort | Risk | Quality | Dodges (a) source | Dodges (b) engraving |
|---|------|--------|------|---------|-------------------|----------------------|
| **1** | **Method-book hand-entry, audio-first** (Approach A) — type 15-20 canonical lines from a trusted book (Aebersold ii-V-I, Coker *Patterns for Jazz*, Bergonzi *Melodic Structures*), verify by ear, notation optional | **Low-Med** | **Low** | **High** | ✅ (trusted source) | ✅ (no engraving-from-performance) |
| **2** | **MIDI-first, never engrave** (Approach B) — build the feature on note-events; import lick MIDI (Omnibook MIDI, transcription MIDIs), audition by ear, store as events; notation decorative | Med | Low-Med (MIDI sourcing) | High | ✅ | ✅ |
| **3** | **Whole-solo study** (Approach D) — drop isolated licks; load a full solo (audio + the chart `solo_av.py` can already make) and practice in context | Med (mostly built) | Low | High musically | ✅ (context restored) | ⚠️ partial (chart still engraved, but solo-scale tolerance) |
| **4** | **Capture-your-own** (Approach C) — "capture a lick" mode: play a 2-5-1 into the mic, app records/pitch-detects, tags with changes | Med | Med (pitch-to-notation; trivial if audio-only) | High (your own voice) | ✅ | ✅ if audio-only |
| **5** | **`score-to-woodshed` sanctioned loop** (wood-12 option "a") — crop-read-verify a printed chart into verified ABC + Woodshed import | Med per chart | Low (verification catches errors) | High on clean single-line sources | ⚠️ (depends on chart chosen) | ⚠️ pays cleanliness tax on messy sources |
| **6** | **OMR-engine assisted entry** — use `omr.py` to read printed lines, verify/correct by ear | Med | Med (triplets/ties/full-tune unproven) | High pitch, uncertain rhythm | ⚠️ | ❌ (engraving is the core open problem) |
| — | ~~Hand-authored "in the style of"~~ | Low | Low | **Med (didn't sound like the language)** | ❌ | ✅ |
| — | ~~OMR/engrave-from-performance (WJazzD → clean notation)~~ | High | High | **The proven dead end** | ❌ | ❌ |

---

## Recommendation (for Chris's wood-12 call — not a decision made for him)

**The single simplest viable path forward: Approach A — method-book hand-entry, audio-first.**

**Rationale:**
- It **dodges both failure axes**: a trusted method book solves source quality (a), and entering lines as data + verifying by ear skips engraving-from-performance entirely (b) — the thing that actually kept failing.
- It is the **fastest route to a trustworthy win**: ~one sitting to enter and ear-check a small set of lines that *definitely sound right*, fully under Chris's control.
- It **reuses what already works** (the validator, the 4-bar loop, the LICKS format, audio playback) and **avoids the proven dead end** (engrave-from-performance).

**Sequencing suggestion:** start with **A (or B if a good MIDI lick source is on hand)** for the fast win; treat **D (whole-solo study)** as the longer-term feature reframe and **C (capture-your-own)** as a worthwhile spike once the basics work. Reserve **`score-to-woodshed`** for when Chris wants a *specific printed chart* digitized — it's the right tool for that, just not for sourcing vocabulary in bulk.

**The one decision Chris must make first:** **audio-only vocabulary vs. notation-backed.**
- *Audio-only* = fastest, always worked, sidesteps every engraving problem.
- *Notation-backed* = prettier on the staff, but it's the hard part that caused the fatigue.

**Pick that one thing and the approach follows.** If audio-only → A or B are trivial and immediate. If notation-backed → A is still the safest (clean printed source beats messy performance), but budget for the engraving tax.

---

## Open `[confirm]` items

- **No numeric "sound-quality" / idiomatic-correctness metric** exists for any approach — judgments ("didn't sound like the language," "weird snippets," "almost good but weird") are by ear, not measured. Treat quality claims as qualitative.
- **`score-to-woodshed` has no published throughput/accuracy figure** — its verification is qualitative (visual bar-by-bar diff), not a percentage.
- **Ad-hoc OMR-from-Real-Book attempts (#2) have no standalone accuracy number** — only the later `omr-engine` is eval-backed.
- **OMR-engine full-tune transcription accuracy on real Real Book melodies is unmeasured** — G6 covers key signatures only; the published 100%/99.8% figures are per-stage (notes-only, keys, dotted quarter), not whole-solo.
- **L1 identity discrepancy:** the A4 brief implies L1 is a style-of adaptation; the approaches log says L1 is the locked Chet Baker "Let's Get Lost" pick. Confirm the current contents of L1 in `index.html` before relying on either.
- **A4 pack merge status:** L11-L21 are validator-clean but appear NOT yet merged into `index.html` (effort paused before integration) — confirm before assuming they're live.
