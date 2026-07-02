/* THE WOODSHED — user-imported charts (created by the score-to-woodshed skill).
   Each entry: {id, title, source, key, style, bpm, abc, bars}
   bars = CONCERT-pitch chord array (the band plays these); abc = notation as printed. */
window.USER_CHARTS=(window.USER_CHARTS||[]).concat([{
  id: 'blue-bossa-head-8',
  forTune: 'Blue Bossa',
  title: 'Blue Bossa — head, bars 1–8',
  source: 'Real Book B♭ 6th ed., p.50 — pixel-verified by two independent transcription passes',
  key: 'Dm (written for B♭; concert Cm)',
  style: 'bossa',
  bpm: 140,
  abc: `X:1
T:Blue Bossa — head, bars 1–8 (written for B♭)
C:Kenny Dorham
L:1/8
M:4/4
K:Dm
A2 |:"D-" a3 g fe z d-| d4- dc z B-|"G-7" B4- Ba z g-|"C7" g6 z2 |
"E-7b5" g3 f ed z c-|"A7#5(#9)" c4- cB z A-|"D-" A4- Ag z f-| f6 z2 |]`,
  // CONCERT-pitch chords for the band: written (B♭ part) minus a whole step.
  bars: [['Cm7'], ['Cm7'], ['Fm7'], ['Bb7'], ['Dm7b5'], ['G7alt'], ['Cm7'], ['Cm7']]
}, {
  id: 'solar-head',
  forTune: 'Solar',
  title: 'Solar — head (B♭)',
  source: 'Real Book B♭ 6th ed., p.363 — homr OMR, Chris-verified',
  key: 'D- (written for B♭; concert C-)',
  style: 'swing',
  bpm: 138,
  abc: `X:1
T:Solar — head (written for B♭)
C:Miles Davis
M:C|
L:1/8
K:F
"D-"z d3 ^c2ed  | z (A3 A3)=B  | "A-7"c2c2 =B2d(c  |
"D7"c8)  | "Gmaj7"z =B3 ^A2cB  | z (D3 D2)GA  |
"G-7"B2B2 A2c(B-  | "C7"B6)z (A  | "Fmaj7"A2)GF ED2(_A-  |
"F-7"_A2)GF "Bb7"_ED2(G  | "Ebmaj7"G8)  | "E-7b5"z4 "A7b9"z4  |]`,
  // CONCERT-pitch chords for the band.
  bars: [['C-6'], ['C-6'], ['G-7'], ['C7'], ['Fmaj7'], ['Fmaj7'], ['F-7'], ['Bb7'], ['Ebmaj7'], ['Eb-7', 'Ab7'], ['Dbmaj7'], ['Dm7b5', 'G7b9']]
}, {
  id: 'attya-head',
  forTune: 'All The Things You Are',
  title: 'All The Things You Are — head (B♭)',
  source: 'Real Book B♭ 6th ed., p.22 — per-strip homr + Chris-verified',
  key: 'B♭ (written; concert A♭)',
  style: 'swing',
  bpm: 132,
  abc: `X:1
T:All The Things You Are — head (written for B♭)
C:Jerome Kern · Oscar Hammerstein
M:4/4
L:1/4
K:Bb
"G-7"B4 | "C-7"e3 B | "F7"A A A A | "Bbmaj7"A d2 A |
"Ebmaj7"G G G G | "A7"G ^c2 G | "Dmaj7"^F4- | ^F4 |
"D-7"F4 | "G-7"B3 F | "C7"=E E E E | "Fmaj7"=E A2 E |
"Bbmaj7"D D D D | "B-7b5"D =E/2F/2 "E7"E D | "Amaj7"^C4- | "F#7#5"^C =E A =e |
"B-7"=e3/2 d/2 d2- | "E7"d F ^F d | "Amaj7"^c4- | ^c =E =A ^c |
"G#-7b5"^c3/2 =B/2 B2- | "C#7"=B C ^C B | "F#maj7"^A4- | "D7#5"^A4 |
"G-7"B4 | "C-7"e3 B | "F7"A A A A | "Bbmaj7"A d2 A |
"Ebmaj7"G4 | "Ab7"f3 e | "D-7"F F (3FFF | "C#o7"A3 G |
"C-7"E E G B | "F7"g2 A2 | "Bbmaj7"B4 | "A-7b5"z2 "D7b9"z2 |]`,
  // CONCERT-pitch chords for the band (full AABA changes).
  bars: [['F-7'], ['Bb-7'], ['Eb7'], ['Abmaj7'], ['Dbmaj7'], ['D-7', 'G7'], ['Cmaj7'], ['Cmaj7'], ['C-7'], ['F-7'], ['Bb7'], ['Ebmaj7'], ['Abmaj7'], ['A-7', 'D7'], ['Gmaj7'], ['Gmaj7'], ['A-7'], ['D7'], ['Gmaj7'], ['Gmaj7'], ['F#m7b5'], ['B7b9'], ['Emaj7'], ['C7b13'], ['F-7'], ['Bb-7'], ['Eb7'], ['Abmaj7'], ['Dbmaj7'], ['DbmM7'], ['C-7'], ['Bo7'], ['Bb-7'], ['Eb7'], ['Abmaj7'], ['Gm7b5', 'C7b9']]
}]);
