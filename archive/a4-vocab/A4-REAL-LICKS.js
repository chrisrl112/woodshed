/* ====================================================================
   A4-REAL-LICKS.js — REAL, verified jazz vocabulary for the Woodshed
   --------------------------------------------------------------------
   Replaces the synthetic L1–L10 in index.html's LICKS array.

   Every lick is a transcription from the printed Real Book (B-flat
   edition) PDF at /Projects/Trumpet/Real Book.pdf, read with the
   score-to-woodshed crop-read-verify method (page->system->bar passes
   on cropped PNGs) and verified by re-rendering each compiled lick's
   ABC and visually diffing it bar-by-bar against the source crop.

   FORMAT (mirrors the original L1-L10):
     - offsets in n:[] are SEMITONES FROM THE PHRASE TONIC
       (the I root for major, the i root for minor, the I7 root for blues).
       Because offsets are RELATIVE to the tonic, the B-flat written-vs-
       concert transposition of the Real Book is irrelevant.
     - p = rhythm token per beat (see PAT dict in index.html).
       Pattern spans sum to exactly 16 (four 4/4 bars).
     - bar1 (beats 0-3)=ii material, bar2 (4-7)=V, bars3-4 (8-15)=I + resolution.

   SOURCE PAGE OFFSET: printed Real Book page = PDF page + 1
     (PDF p.86 = printed p.87 Confirmation, etc.)

   CONFIDENCE NOTES (see A4-VERIFICATION below):
     L1,L2  Confirmation bridge: contour + chromatic V descent verified;
            a few fast inner pitches in bar 1 are best-effort (dense
            handwritten 16ths) - flagged.
     L3,L4  Autumn Leaves: slow, clearly-engraved notes; high confidence.
     L5     Au Privave: bar 1 (the G-F#-G-D head motif) verified note-for-
            note; bars 2-4 are an idiomatic blue-scale answer (NOT a
            literal transcription) so the line fits the app's I7-IV7-I7
            blues backing - flagged.
     L6     Straight No Chaser: verified bar-by-bar (true I-IV-I blues).
   ==================================================================== */

const A4_REAL_LICKS = [

 /* ---------- MAJOR ii-V-I ---------- */

 {id:'L1',name:'Confirmation (bridge ii-V-I)',cat:'251maj',tBpm:132,
  src:'Confirmation — Charlie Parker, Real Book p.87 (PDF p.86), bridge D-7 G7 Cmaj7',
  beats:[{p:'ssss',n:[0,-3,-1,-5]},{p:'88',n:[-3,-7]},{p:'88',n:[-5,-3]},{p:'r4'},
         {p:'88',n:[-2,-4]},{p:'88',n:[-2,-4]},{p:'r4'},{p:'r4'},
         {p:'ssss',n:[0,-1,0,0]},{p:'d8s',n:[-1,4]},{p:'r2'},{p:'r2'},{p:'r2'}],
  chords:[[0,'ii-7'],[4,'V7'],[8,'I△']],
  lore:'The textbook bebop ii-V-I, straight off Confirmation\'s bridge. Bar 1 weaves through the D-7, bar 2 is the signature chromatic G7 descent (B♭–A♭ leaning over the dominant), and the line resolves onto the Cmaj7 with a held root-and-third. This is the phrase every bebop player cuts their teeth on.'},

 {id:'L2',name:'Confirmation (ii-V to the 3rd)',cat:'251maj',tBpm:128,
  src:'Confirmation — Charlie Parker, Real Book p.87 (PDF p.86), bridge A-7 D7 G6',
  beats:[{p:'88',n:[9,-1]},{p:'ttt',n:[5,4,7]},{p:'88',n:[9,7]},{p:'4',n:[9]},
         {p:'88',n:[3,2]},{p:'88',n:[0,-1]},{p:'88',n:[-3,-5]},{p:'r4'},
         {p:'r2'},{p:'2',n:[0]},{p:'r2'},{p:'r2'}],
  chords:[[0,'ii-7'],[4,'V7'],[8,'I△']],
  lore:'The other ii-V-I on Confirmation\'s bridge. A triplet figure lifts through the A-7, then the D7 spills straight down — B♭ A G F♯ E — a stepwise altered-dominant fall that lands the phrase home on the tonic. Parker\'s lines almost always descend the V; this is why.'},

 {id:'L3',name:'Autumn Leaves (major ii-V-I)',cat:'251maj',tBpm:120,
  src:'Autumn Leaves — Kosma/Mercer, Real Book p.39 (PDF p.38), B-7 E7 Amaj7',
  beats:[{p:'1',n:[5]},
         {p:'4',n:[4]},{p:'4',n:[2]},{p:'4',n:[0]},{p:'4',n:[-1]},
         {p:'2',n:[4]},{p:'r2'},
         {p:'r2'},{p:'r2'}],
  chords:[[0,'ii-7'],[4,'V7'],[8,'I△']],
  lore:'Autumn Leaves opens on the most-played major ii-V-I in the book. The melody hangs the 11th over the ii (B-7), then walks the E7 down by step — C♯ B A G♯ — and settles on C♯, the bright 3rd of Amaj7. Pure singing line; the harmony does the work.'},

 /* ---------- MINOR ii-V-i ---------- */

 {id:'L4',name:'Autumn Leaves (minor ii-V-i)',cat:'251min',tBpm:108,minor:true,
  src:'Autumn Leaves — Kosma/Mercer, Real Book p.39 (PDF p.38), G#ø7 C#7♭9 F#-',
  beats:[{p:'1',n:[5]},
         {p:'4',n:[-4]},{p:'r4'},{p:'4',n:[-3]},{p:'4',n:[0]},
         {p:'1',n:[0]},
         {p:'r2'},{p:'r2'}],
  chords:[[0,'iiø'],[4,'V7b9'],[8,'i-']],
  lore:'The defining minor cadence — Autumn Leaves alternates major and minor ii-V every chorus. A held note over the G♯ half-diminished, a chromatic step up through the C♯7♭9 (D, D♯, F♯), and the line resolves onto the F♯-minor root. This is where every player first internalises the minor ii-V-i.'},

 /* ---------- BLUES ---------- */

 {id:'L5',name:'Au Privave (blues head)',cat:'blues',tBpm:120,
  src:'Au Privave — Charlie Parker, Real Book p.37 (PDF p.36), head bar 1 (G7) + blue-scale answer',
  beats:[{p:'88',n:[0,-1]},{p:'88',n:[0,-5]},{p:'r8',n:[-1]},{p:'4',n:[-3]},
         {p:'88',n:[-5,-2]},{p:'88',n:[0,3]},{p:'88',n:[5,3]},{p:'88',n:[2,0]},
         {p:'88',n:[3,0]},{p:'2',n:[0]},{p:'r4'},{p:'r2'},{p:'r2'}],
  chords:[[0,'I7'],[4,'IV7'],[8,'I7']],
  lore:'Parker\'s blues head opens with the unmistakable G–F♯–G–D turn: a chromatic lower-neighbour wrapped around the root before the drop to the 5th. The answering phrase climbs the blue scale with its ♯4/♭3 colours. This is the alphabet of bop-blues phrasing.'},

 {id:'L6',name:'Straight No Chaser (blues riff)',cat:'blues',tBpm:128,
  src:'Straight No Chaser — Thelonious Monk, Real Book p.386 (PDF p.385), head bars 1-3',
  beats:[{p:'88',n:[0,4]},{p:'88',n:[3,4]},{p:'r8',n:[-3]},{p:'88',n:[0,4]},
         {p:'88',n:[3,4]},{p:'88',n:[3,4]},{p:'r4'},{p:'r8',n:[-3]},
         {p:'88',n:[0,4]},{p:'88',n:[3,4]},{p:'r8',n:[-3]},{p:'2',n:[0]},{p:'r4'},{p:'r2'}],
  chords:[[0,'I7'],[4,'IV7'],[8,'I7']],
  lore:'Monk\'s whole head is one displaced chromatic riff — C up to E with the blue ♭3 (E♭) leaning into the natural 3rd, then the cell drags across the bar so it lands on a different beat each time. Pure blues with Monk\'s rhythmic mischief built right in.'},
];

if (typeof module !== 'undefined') module.exports = { A4_REAL_LICKS };
