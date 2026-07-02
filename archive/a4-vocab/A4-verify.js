/* A4-verify.js — validates A4-VOCAB-PACK.js against the compiler's structural rules.
   Run: node A4-verify.js  (from the Trumpet folder) */
const fs = require('fs');
const path = require('path');

// PAT dictionary copied from index.html (note-counts + spans)
const PAT = {
  '4':{span:1,notes:1}, '2':{span:2,notes:1}, '2.':{span:3,notes:1}, '1':{span:4,notes:1},
  '88':{span:1,notes:2},
  'ttt':{span:1,notes:3},
  'ssss':{span:1,notes:4},
  '8ss':{span:1,notes:3},
  'ss8':{span:1,notes:3},
  'd8s':{span:1,notes:2},
  'r8':{span:1,notes:0}, 'r4':{span:1,notes:0}, 'r2':{span:2,notes:0},
  'tt_':{span:1,notes:2}, '_tt':{span:1,notes:2},
  'x6':{span:1,notes:6}
};
const RANGE_LO=54, RANGE_HI=82;

// load the pack
const src = fs.readFileSync(path.join(__dirname,'A4-VOCAB-PACK.js'),'utf8');
const A4_NEW_LICKS = eval(src + '\n;A4_NEW_LICKS');

let allPass = true;
console.log('=== A4 VOCAB PACK VERIFICATION ===\n');
for (const lick of A4_NEW_LICKS) {
  const errs = [];
  // 1. spans sum to 16
  let span = 0;
  for (const b of lick.beats) {
    const P = PAT[b.p];
    if (!P) { errs.push(`unknown pattern '${b.p}'`); continue; }
    span += P.span;
    // 2. n-length matches note-count
    const nlen = (b.n||[]).length;
    if (nlen !== P.notes) errs.push(`cell '${b.p}' needs ${P.notes} notes, has ${nlen}`);
  }
  if (span !== 16) errs.push(`span sum = ${span} (must be 16)`);

  // 3. offset span <= 24 and fits 54..82 with some base
  const offs = [];
  lick.beats.forEach(b=>(b.n||[]).forEach(o=>offs.push(o)));
  const lo = Math.min(...offs), hi = Math.max(...offs);
  const spread = hi - lo;
  if (spread > 24) errs.push(`offset spread ${spread} > 24`);
  // try the compiler's bases (keyPc=0 for C; worst case any key shifts equally,
  // but we check the existence of SOME base 36/48/60/72 that fits — matching compileLick)
  let fits = false, fitBase = null;
  for (const base of [36,48,60,72]) {
    if (base+lo >= RANGE_LO && base+hi <= RANGE_HI) { fits = true; fitBase = base; break; }
  }
  if (!fits) errs.push(`no base in {36,48,60,72} fits offsets [${lo}..${hi}] into 54..82`);

  const status = errs.length ? 'FAIL' : 'PASS';
  if (errs.length) allPass = false;
  console.log(`${lick.id} ${status} — span=${span}, off=[${lo}..${hi}] spread=${spread}${fitBase!==null?`, base=${fitBase}`:''}`);
  errs.forEach(e=>console.log(`     ! ${e}`));
}
console.log(`\n=== ${allPass ? 'ALL LICKS PASS' : 'SOME LICKS FAILED'} (${A4_NEW_LICKS.length} licks) ===`);
process.exit(allPass ? 0 : 1);
