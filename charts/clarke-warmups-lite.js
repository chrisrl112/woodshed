/* charts/clarke-warmups-lite.js — Clarke Second Study exercises shown in the
   woodshed-lite Warmup station. Ex.27 + Ex.28 are Chris's ground-truth
   transcription, verified bar-for-bar against Technical Studies.pdf p.8 (see
   archive/transcription-verify/clarke-ex27-VERIFIED.md). Ex.29–32 come from the
   verified score-engine export (pipelines/score-engine/output/clarke/,
   VERIFY-REPORT.md — all "OK", Ex.27 pitch_acc=1.0); the Second Study is the
   same shape transposed up a semitone through the keys, each resolving to a
   tonic whole note (the OMR export's "half + rest" ending is a whole-note
   misread — normalized here to `,8` to match the verified 27/28 ground truth).
   H.L. Clarke, 1912 — public domain. Notation only (no chord/bars data). */
window.CLARKE_WARMUPS = [
  {
    id: 'clarke-2-ex27', key: 'G', keyLabel: 'G major', tempo: 'half=80-120',
    abc: `X:1\nM:C|\nL:1/8\nK:G\n(G,A,B,G, A,B,CA, | B,CDB, G,A,B,G, | A,B,CA, F,G,A,F, | G,B,A,G, A,CB,A,) :| G,8 |]\n`,
  },
  {
    id: 'clarke-2-ex28', key: 'Ab', keyLabel: 'A♭ major', tempo: 'half=80-120',
    abc: `X:1\nM:C|\nL:1/8\nK:Ab\n(A,B,CA, B,CDB, | CDEC A,B,CA, | B,CDB, G,A,B,G, | A,CB,A, B,DCB,) :| A,8 |]\n`,
  },
  {
    id: 'clarke-2-ex29', key: 'A', keyLabel: 'A major', tempo: 'half=80-120',
    abc: `X:1\nM:C|\nL:1/8\nK:A\n(A,B,CA, B,CDB, | CDEC A,B,CA, | B,CDB, G,A,B,G, | A,CB,A, B,DCB,) :| A,8 |]\n`,
  },
  {
    id: 'clarke-2-ex30', key: 'Bb', keyLabel: 'B♭ major', tempo: 'half=80-120',
    abc: `X:1\nM:C|\nL:1/8\nK:Bb\n(B,CDB, CDEC | DEFD B,CDB, | CDEC A,B,CA, | B,DCB, CEDC) :| B,8 |]\n`,
  },
  {
    id: 'clarke-2-ex31', key: 'B', keyLabel: 'B major', tempo: 'half=80-120',
    abc: `X:1\nM:C|\nL:1/8\nK:B\n(B,CDB, CDEC | DEFD B,CDB, | CDEC A,B,CA, | B,DCB, CEDC) :| B,8 |]\n`,
  },
  {
    id: 'clarke-2-ex32', key: 'C', keyLabel: 'C major', tempo: 'half=80-120',
    abc: `X:1\nM:C|\nL:1/8\nK:C\n(CDEC DEFD | EFGE CDEC | DEFD B,CDB, | CEDC DFED) :| C8 |]\n`,
  },
];
