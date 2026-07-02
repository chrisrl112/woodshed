# A4 Vocab Pack — Sourcing & Design Brief

**Deliverable:** 11 new transcribed/adapted jazz vocabulary lines (`L11`–`L21`) for the Woodshed Vocab/Riffs module, in the exact `LICKS` data format.
**Files:** `A4-VOCAB-PACK.js` (the `A4_NEW_LICKS` array), `A4-verify.js` (validator), this brief.
**Weighting:** 6 major ii-V-I · 3 minor ii-V-i · 2 blues.
**Status:** all 11 pass the structural validator (spans=16, note-counts match, offset spread ≤24, fits the F#3–Bb5 written range).

---

## (a) The vocabulary families chosen, and WHY

The existing L1–L10 covered the broad strokes (Parker up/down, one enclosure, a Honeysuckle motif, scale runs, the Camden Hughes arpeggio set). They sounded "correct" but leaned on diatonic running. This pack deliberately fills the gaps that make a line sound like *the language* rather than scale practice — the devices a listener identifies as bebop within two beats:

| Lick | Family | Why it's canonical |
|------|--------|--------------------|
| **L11 Bebop Scale Drop** | Barry Harris **dominant bebop scale** descent | The 8-note dominant scale is the engine of bebop time-feel: adding the natural-7 passing tone makes chord tones fall on every downbeat in straight eighths. Descending it over the V is the single most-taught device in the idiom. |
| **L12 3-to-9 Arpeggio** | **Diminished-7 / 3-to-9** over the dominant | Arpeggiating the dim7 built on the 3rd of a V7 spells 3-5-♭7-♭9 — all strong tensions, zero "avoid" notes. The ♭9→♭7→3 resolution is the most recognizable dominant colour in the music. |
| **L13 Double Enclosure** | **Parker enclosure** (chromatic + diatonic wrap) | Surrounding a target from above and below before landing it is Parker's fingerprint. Two stacked enclosures give the busy, vocal contour you hear all over the Omnibook. |
| **L14 Tritone Sub Slide** | **Tritone substitution** | Playing ♭II7 (D♭7) over the V and resolving down by half-step into the I. The defining "outside-but-inevitable" sound — teaches the ear that altered tensions pull, not clash. |
| **L15 Stacked 3-to-9** | **Bergonzi 3-5-7-9 melodic structures** | Bergonzi's four-note cell (3-5-7-9 of each chord) sequenced down a step from ii to V. Trains hearing chords as upper-structure shapes rather than root-position arpeggios. |
| **L16 Long Line, Altered Tail** | **Cannonball/Parker long eighth-note line** + altered descent | A continuous bar-spanning eighth line (no rests) that walks Dorian up and the **altered scale** down. The relentless forward motion is the hallmark of Cannonball and late-Bird. |
| **L17 Harmonic Minor Cadence** | **Minor ii-V-i** via 5th mode of harmonic minor | The bread-and-butter minor cadence (Autumn Leaves, Alone Together): half-dim arpeggio → ♭9 altered dominant → ♭3. |
| **L18 Minor Drop to the 6** | Parker **minor tail**, resolves to natural-6 (i-6 colour) | A weeping minor line with a ♭9 hammer and a chromatic enclosure of the 3rd, then a Parker lift to the natural 6 to brighten the minor tonic without leaving it. |
| **L19 Altered Sixteenths** | **Altered scale** (7th mode melodic minor) sixteenth cascade | Rhythmic contrast: a fast 16th-note run down the most dissonant/forward-pulling dominant scale, collapsing onto the ♭3. |
| **L20 Bird Blues Tail** | **Charlie Parker blues** (Billie's Bounce / Now's the Time idiom) | The ♭7 trill → blue ♯4 → ♭3-to-3 smear. The most-quoted blues phrase in jazz; this is the language under every shout chorus. |
| **L21 Swing Blues Shout** | **Swing-era major blues** (Armstrong/Lester Young idiom) | The bright major-pentatonic + 6th side of the blues with a triplet shake. Deliberate contrast to the darker bebop blues of L20, plus rhythmic variety (triplets). |

**Rhythm/contour variety (per the spec):** not all straight eighths. L11/L13/L14/L17/L18/L20 use rests and 16th-note ornaments (`8ss`) to break phrases; L16 is a deliberate unbroken eighth line; L19 uses `ssss` sixteenth cascades; L21 uses eighth-note triplets (`ttt`, `tt_`) for swing-era feel. Held resolutions vary across the 3rd, 5th, 9th, ♭3, and natural-6 so the endings don't all sound the same.

## (b) Sources & honest provenance

These are real, citable methods/repertoire. **Important honesty note:** because the lines must be stored as explicit semitone-offset arrays that transpose cleanly into a single 4-bar ii-V-I shape, I wrote *idiomatic lines in the style/method of each source* rather than lifting a specific copyrighted transcription bar-for-bar. Every line marked **"adapted"** in its `src` field is an original construction that faithfully uses the named device — none is claimed as a verbatim transcription. This matches how L1–L5 were already handled (they cite the device, not a specific recording), and is more defensible than mislabeling adaptations as transcriptions.

- **Barry Harris** — bebop-scale method (the dominant 8-note scale; the "add a passing tone so chord tones hit downbeats" rule). Widely documented in his workshops and in *The Barry Harris Harmonic Method*. → L11.
- **David Baker / Jerry Coker** — the "3-to-9" arpeggio and diminished-over-dominant device, standard in *How to Play Bebop* (Baker) and Coker's *Improvising Jazz*. → L12.
- **Charlie Parker** — enclosure vocabulary and blues phrasing; the *Charlie Parker Omnibook* (Billie's Bounce, Now's the Time) is the canonical reference for the contours imitated. → L13, L18, L20.
- **Tritone substitution** — standard theory (Mark Levine, *The Jazz Theory Book*; Coker). → L14.
- **Jerry Bergonzi** — *Inside Improvisation Vol. 1: Melodic Structures* (the 3-5-7-9 four-note cell concept). → L15.
- **Cannonball Adderley / Parker** — the long continuous eighth-note line + altered descent; documented across both players' solos. → L16.
- **Minor ii-V via harmonic-minor 5th mode / altered scale** — standard (Levine; Aebersold Vol. 23 *One Dozen Standards* and the minor ii-V drills). → L17, L19.
- **Swing-era major blues** — Louis Armstrong / Lester Young riff idiom (major pentatonic + 6th, triplet shakes). → L21.
- For comparison, the existing **Camden Hughes "25 Easy ii-V-I Licks"** set (cited in L6–L10) was the model for how an adaptation should read; this pack does not reuse those specific lines.

## (c) How each lick maps to the 4-bar ii-V-I backing loop

The backing loop is **1 bar ii · 1 bar V · 2 bars I** (`chords:[[0,'ii-7'],[4,'V7'],[8,'I△']]`; minor uses `iiø / V7b9 / i-`; blues `I7 / IV7 / I7`). Beat indices: bar 1 = 0–3, bar 2 = 4–7, bars 3–4 = 8–15.

- **Bar 1 (beats 0–3)** establishes the ii (or i / I7): every line opens on or quickly reaches a chord tone of the supertonic. Offsets like 2/5/9/12 = root/♭3/5/♭7 of Dm7 in C.
- **Bar 2 (beats 4–7)** is where the colour lives — the dominant. This is where the enclosures, 3-to-9 dim arpeggios, tritone-sub slides, and altered descents happen. Chromatic approach notes fall on offbeats (the &s); chord tones on the downbeats.
- **Bars 3–4 (beats 8–15)** resolve to the I and hold. Each line lands a tonic-area note (3rd=4, 5th=7, root=0/12, 9th=2/14, or ♭3=3 / natural-6=9 for minor) on or near beat 8, then fills the remainder with rests — exactly the resolution+rest convention of L1–L10.

All offsets sit between 0 and +21 semitones (within the validator's −3…+21 guidance) and every line's spread is ≤18 semitones, comfortably under the 24-semitone (two-octave) ceiling, so they fit the written F#3–Bb5 range in any of the compiler's four tonic bases. The validator confirms a fitting base for each (mostly base 60; L14 fits at base 48).

## (d) Notes for the integrating (BUILD) agent

- **Merge target:** append the `A4_NEW_LICKS` array contents into the existing `LICKS` array in `index.html` (after `L10`, before the closing `]`). IDs `L11`–`L21` do not collide with existing `L1`–`L10`. The `LICK_CATS` map already covers `251maj` / `251min` / `blues`, so no category changes are needed.
- **Format compatibility:** fields exactly match L1–L10 (`id, name, cat, tBpm, [minor], src, beats, chords, lore`). `minor:true` is set only on the three `251min` licks. All rhythm tokens used (`88, 4, 2, 2., r4, r2, 8ss, ssss, ttt, tt_`) exist in the `PAT` dictionary.
- **Ear-First default:** these lines are designed to be *heard and sung back* — the resolutions land on strong, singable tonic-area tones and the dominant-bar tensions resolve by half-step, so they reward an ear-first (play-along, no notation first) practice flow before the staff is revealed.
- **Backing loop:** authored against the 4-bar `ii (1) · V (1) · I (2)` loop; nothing here assumes a longer form. Tempos (`tBpm` 108–128) are practice-realistic for the device — the 16th-note L19 is intentionally the slowest (108).
- **Validator:** `A4-verify.js` can be re-run after the merge (point it at the merged file) to re-confirm spans/note-counts/range. It is self-contained (re-declares `PAT`).

## Confidence & what Chris should review

- **High confidence** on structural correctness (all 11 pass the validator), on the device theory (these are textbook-canonical), and on range/transposition fit.
- **Review item — provenance labeling:** every line is an *idiomatic adaptation*, not a verbatim transcription, and is labeled "adapted" in `src`. If Chris wants literal transcriptions (e.g. an exact Omnibook bar), those would need note-for-note entry from the printed source and would not always fit a single clean 4-bar ii-V-I shape — flag if that's the bar.
- **Review item — taste/voicing:** L19's altered sixteenth cascade and L15's stacked upper-structures are the most "modern"/dense; if the app's audience skews more mainstream-swing, L21 and L20 are the safest, most immediately idiomatic. Worth a listen to confirm L19 doesn't feel like an etude.
- **Minor range note:** L11, L12, L15, L19 reach up to offsets 19–21 (around the 13th/upper octave). They fit the written range per the validator, but in the brightest keys the compiler will pick a lower base — worth a quick audible check that none clip the top.
