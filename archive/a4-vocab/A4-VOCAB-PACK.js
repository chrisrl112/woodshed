/* ====================================================================
   A4 VOCAB PACK — new ii-V-I & blues vocabulary (L11 onward)
   --------------------------------------------------------------------
   Drop-in compatible with the existing LICKS array in index.html.
   The BUILD agent merges this array into LICKS.

   FORMAT (mirrors L1–L10):
     - offsets in n:[] are SEMITONES FROM THE I-CHORD ROOT (tonic).
       Minor: from the i root. Blues: from the I7 root.
       Reference (tonic=0): D=2 E=4 F=5 F#=6 G=7 Ab=8 A=9 Bb=10 B=11
       C(oct)=12 Db=13 D=14 Eb=15 E=16 ...
     - p = rhythm token per beat (see PAT dict). Spans MUST sum to 16.
     - bar1 (beats 0–3)=ii material · bar2 (4–7)=V · bars3–4 (8–15)=I + rest.
     - Each lick ends on a held tonic-area note + rests to fill bar 4.

   PROVENANCE: see A4-VOCAB-BRIEF.md. Lines marked "transcribed" follow a
   published source closely; "adapted" are idiomatic lines written in the
   named style/method (Barry Harris bebop scale, Parker enclosure, etc.).
   ==================================================================== */
const A4_NEW_LICKS = [

 /* ---------- MAJOR ii-V-I (6) ---------- */

 /* L11 — Barry Harris bebop-scale descent. The signature move: descend the
    G dominant-bebop scale (Mixolydian + the major-7 passing tone) so that
    every chord tone of G7 lands on a downbeat, then resolve down to the 5th
    of the I. Bar 1 sets it up by arpeggiating up the ii. */
 {id:'L11',name:'Bebop Scale Drop',cat:'251maj',tBpm:120,src:'Barry Harris bebop-scale method (dominant 8-note scale), adapted',
  beats:[{p:'88',n:[2,5]},{p:'88',n:[9,12]},{p:'88',n:[14,9]},{p:'r4'},
         {p:'88',n:[19,18]},{p:'88',n:[17,16]},{p:'88',n:[14,12]},{p:'88',n:[11,9]},
         {p:'2',n:[7]},{p:'r2'},{p:'r2'},{p:'r2'}],
  chords:[[0,'ii-7'],[4,'V7'],[8,'I△']],
  lore:'Barry Harris\'s core idea: the dominant bebop scale (Mixolydian plus the natural-7 passing tone) has 8 notes, so descending in straight eighths from G drops a chord tone onto every downbeat. Bar 2 falls G–F♯–F–E–D–C–B–A; land on G, the 5th of the I, for a settled close.'},

 /* L12 — "3-to-9" arpeggio over the V (the Bdim7 / G7b9 sound). The most
    common bebop device on a dominant: play the diminished-7 arpeggio built
    on the 3rd, which spells 3-5-b7-b9. Resolve b7→3 into the I. */
 {id:'L12',name:'3-to-9 Arpeggio',cat:'251maj',tBpm:124,src:'David Baker / Jerry Coker "3-to-9" dominant device, adapted',
  beats:[{p:'88',n:[5,9]},{p:'88',n:[12,14]},{p:'88',n:[12,9]},{p:'r4'},
         {p:'88',n:[11,14]},{p:'88',n:[17,20]},{p:'88',n:[17,14]},{p:'88',n:[11,8]},
         {p:'2',n:[4]},{p:'r2'},{p:'r2'},{p:'r2'}],
  chords:[[0,'ii-7'],[4,'V7'],[8,'I△']],
  lore:'Over G7, arpeggiate the B-diminished-7 (B–D–F–A♭ = the 3, 5, ♭7 and ♭9 of the chord). It is the single most-used dominant colour in bebop because every note is a strong tension. The ♭9 (A♭) falls back through F (♭7) to E, the 3rd of Cmaj7 — the classic ♭7→3 resolution.'},

 /* L13 — Parker double enclosure of the 3rd of I. Two chromatic-and-diatonic
    wraps that surround the target before landing it. */
 {id:'L13',name:'Double Enclosure',cat:'251maj',tBpm:116,src:'Charlie Parker enclosure vocabulary (Omnibook idiom), adapted',
  beats:[{p:'88',n:[9,7]},{p:'88',n:[5,4]},{p:'88',n:[5,2]},{p:'r4'},
         {p:'8ss',n:[7,8,7]},{p:'88',n:[5,6]},{p:'88',n:[8,6]},{p:'88',n:[5,3]},
         {p:'2',n:[4]},{p:'r2'},{p:'r2'},{p:'r2'}],
  chords:[[0,'ii-7'],[4,'V7'],[8,'I△']],
  lore:'Enclosure is Parker\'s fingerprint: approach a target from above and below before sounding it. Bar 2 wraps G7\'s root (G–A♭–G–F) then curls F–F♯–A♭–F♯ toward the goal. Beats 8–9 enclose E (the 3rd of C) from F above and E♭ below before the held resolution.'},

 /* L14 — Tritone-sub approach. On the V, imply Db7 (the tritone substitute)
    by descending its arpeggio, which resolves by half-step into the I. */
 {id:'L14',name:'Tritone Sub Slide',cat:'251maj',tBpm:118,src:'Tritone-substitution dominant approach (Coker/Levine idiom), adapted',
  beats:[{p:'88',n:[9,12]},{p:'88',n:[14,16]},{p:'88',n:[14,12]},{p:'r4'},
         {p:'88',n:[13,17]},{p:'88',n:[20,17]},{p:'88',n:[13,11]},{p:'88',n:[10,8]},
         {p:'2.',n:[7]},{p:'r2'},{p:'r2'},{p:'r4'}],
  chords:[[0,'ii-7'],[4,'V7'],[8,'I△']],
  lore:'Over G7 you can play D♭7 — the tritone sub — and the line resolves down by half-step into C. Bar 2 arpeggiates D♭–F–A♭ (= the ♭5, ♭7, ♭9 alterations of G7), then chromatically slides B–B♭–A♭ down to G, the 5th of the I. The half-step pull is what makes the alteration sound inevitable rather than wrong.'},

 /* L15 — 3-to-9 over the ii AND the V (Bergonzi-style sequence). Arpeggiate
    from the 3rd up through the 9th on each chord; the shape sequences down. */
 {id:'L15',name:'Stacked 3-to-9',cat:'251maj',tBpm:122,src:'Jerry Bergonzi "Inside Improvisation Vol.1: Melodic Structures" (4-note 3-5-7-9 cells), adapted',
  beats:[{p:'88',n:[5,9]},{p:'88',n:[12,16]},{p:'2',n:[14]},
         {p:'88',n:[11,14]},{p:'88',n:[17,21]},{p:'2',n:[20]},
         {p:'88',n:[16,12]},{p:'88',n:[11,9]},{p:'2',n:[7]},{p:'r2'},{p:'r2'}],
  chords:[[0,'ii-7'],[4,'V7'],[8,'I△']],
  lore:'Bergonzi\'s melodic-structures idea: play the 3-5-7-9 of each chord as a four-note cell. Over Dm7 that is F–A–C–E; over G7, B–D–F–A — the same shape moved down a step. Bars 3–4 spill the upper structure back down to G, resolving the line on the 5th of the I.'},

 /* L16 — Cannonball/Parker "long eighth-note line" with a turnaround feel:
    Dorian up, altered-dominant down with a bebop chromatic, lands on 9th. */
 {id:'L16',name:'Long Line, Altered Tail',cat:'251maj',tBpm:126,src:'Cannonball Adderley / Parker long-line idiom, adapted',
  beats:[{p:'88',n:[4,5]},{p:'88',n:[7,9]},{p:'88',n:[11,12]},{p:'88',n:[14,12]},
         {p:'88',n:[15,14]},{p:'88',n:[12,11]},{p:'88',n:[8,7]},{p:'88',n:[6,5]},
         {p:'2',n:[2]},{p:'r2'},{p:'r2'},{p:'r2'}],
  chords:[[0,'ii-7'],[4,'V7'],[8,'I△']],
  lore:'A flowing eighth-note line that never stops to breathe — Cannonball\'s trademark. Bar 1 walks D Dorian up to the 9th; bar 2 descends G altered: E♭ (♭13) and B♭ (♯9/blue) are the spice, pulling through F♯ to land on D, the open 9th of Cmaj7, for a modern unresolved colour.'},

 /* ---------- MINOR ii-V-i (3) ---------- */

 /* L17 — Half-diminished arpeggio up, harmonic-minor altered V down, land b3.
    The bread-and-butter minor cadence (Autumn Leaves, Alone Together). */
 {id:'L17',name:'Harmonic Minor Cadence',cat:'251min',tBpm:116,minor:true,src:'Standard minor ii-V-i (harmonic-minor 5th mode) idiom, adapted',
  beats:[{p:'88',n:[2,5]},{p:'88',n:[8,11]},{p:'88',n:[14,11]},{p:'r4'},
         {p:'88',n:[8,7]},{p:'88',n:[8,11]},{p:'88',n:[8,7]},{p:'88',n:[5,4]},
         {p:'2',n:[3]},{p:'r2'},{p:'r2'},{p:'r2'}],
  chords:[[0,'iiø'],[4,'V7b9'],[8,'i-']],
  lore:'Over the iiø (Dm7♭5) arpeggiate D–F–A♭–C, the half-diminished sound. The V7♭9 borrows the 5th mode of A harmonic minor: G♯ (the 3rd) and B♭ (the ♭9) circle the dominant before the line resolves down to E♭, the ♭3 of the C-minor tonic.'},

 /* L18 — Minor line with a "b9-to-root" Parker drop on the V and a 6/9 close.
    Ends on the natural 6 (color tone of the i-6 chord) for a brighter minor. */
 {id:'L18',name:'Minor Drop to the 6',cat:'251min',tBpm:112,minor:true,src:'Parker minor-blues / minor ii-V tail idiom, adapted',
  beats:[{p:'88',n:[8,5]},{p:'88',n:[2,5]},{p:'88',n:[8,12]},{p:'r4'},
         {p:'8ss',n:[8,8,7]},{p:'88',n:[5,4]},{p:'88',n:[5,7]},{p:'88',n:[8,7]},
         {p:'2',n:[3]},{p:'2',n:[9]},{p:'r2'},{p:'r2'}],
  chords:[[0,'iiø'],[4,'V7b9'],[8,'i-']],
  lore:'A weeping minor line. Bar 2 hammers the ♭9 (A♭) of the V before falling G–E–E♭–E (a chromatic enclosure of the 3rd, G♯/A♭). It resolves to E♭ (the ♭3 of the i) then lifts to A — the natural 6 of the i-6 chord — a Parker move that brightens the minor without leaving it.'},

 /* L19 — Ascending half-dim into a fast altered-scale descent (16ths) on V.
    More virtuosic; the sixteenth burst gives rhythmic contrast. */
 {id:'L19',name:'Altered Sixteenths',cat:'251min',tBpm:108,minor:true,src:'Altered-scale (7th mode melodic minor) descent, adapted',
  beats:[{p:'88',n:[2,5]},{p:'88',n:[8,11]},{p:'2',n:[14]},
         {p:'ssss',n:[20,18,17,15]},{p:'ssss',n:[14,12,11,8]},{p:'r2'},
         {p:'2',n:[3]},{p:'r2'},{p:'r2'},{p:'r2'}],
  chords:[[0,'iiø'],[4,'V7b9'],[8,'i-']],
  lore:'Bar 1 climbs the Dm7♭5 to the 11th and holds. Bar 2 is a sixteenth-note cascade down the G altered scale (G–F–E♭–D♭–B–A♭ territory, the 7th mode of A♭ melodic minor) — the most dissonant, most forward-pulling dominant colour there is. It collapses onto E♭, the ♭3 of the minor tonic.'},

 /* ---------- BLUES (2) ---------- */

 /* L20 — Charlie Parker blues tail. The classic descending bebop blues lick
    with the b3-to-3 "blue" smear and a 6th-degree turnaround tag. */
 {id:'L20',name:'Bird Blues Tail',cat:'blues',tBpm:128,src:'Charlie Parker blues vocabulary (Omnibook "Now\'s the Time"/"Billie\'s Bounce" idiom), adapted',
  beats:[{p:'8ss',n:[10,12,10]},{p:'88',n:[9,7]},{p:'88',n:[6,5]},{p:'88',n:[3,4]},
         {p:'88',n:[5,9]},{p:'88',n:[10,9]},{p:'88',n:[7,5]},{p:'r4'},
         {p:'8ss',n:[3,4,3]},{p:'88',n:[0,3]},{p:'2',n:[0]},{p:'r2'},{p:'r2'}],
  chords:[[0,'I7'],[4,'IV7'],[8,'I7']],
  lore:'The most-quoted phrase in jazz: the ♭7 (B♭) trill down through the blue ♯4 (F♯) and the ♭3→3 smear (E♭→E) — exactly Bird\'s opening on "Billie\'s Bounce." Over the IV7 it rides the 6th, then the tag rocks E♭–E–C to settle on the tonic. This is the language under every shout chorus.'},

 /* L21 — Major-blues / "Honeysuckle" riff with the 6th and a triplet shake.
    Sweeter, more swing-era; contrasts with the Bird tail. */
 {id:'L21',name:'Swing Blues Shout',cat:'blues',tBpm:120,src:'Swing-era major-blues riff (Louis Armstrong / Lester Young idiom), adapted',
  beats:[{p:'88',n:[7,9]},{p:'4',n:[10]},{p:'ttt',n:[12,10,9]},{p:'88',n:[7,9]},
         {p:'88',n:[10,12]},{p:'88',n:[9,7]},{p:'88',n:[4,5]},{p:'r4'},
         {p:'88',n:[7,9]},{p:'tt_',n:[10,12]},{p:'2',n:[0]},{p:'r2'},{p:'r2'}],
  chords:[[0,'I7'],[4,'IV7'],[8,'I7']],
  lore:'The bright side of the blues — the major-pentatonic + 6th sound that Louis and Lester lived in. The triplet shake (C–B♭–A) over the I7 is a horn-section riff figure; bar 2 leans on the IV7\'s flat-7 and 6th. The tag swings up with a triplet pickup and drops home to the root.'}
];
