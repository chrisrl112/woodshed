#!/usr/bin/env node
/* A4-real-verify.js — compiler-fidelity validator for A4-REAL-LICKS.js
 * Extracts the REAL PAT note-counts/spans from index.html and asserts,
 * for every lick:
 *   1. pattern spans sum to exactly 16 (four 4/4 bars)
 *   2. each cell's n[] length equals its pattern's note count
 *      (rests have no n; spans are still counted)
 *   3. offset spread <= 24 semitones
 *   4. a base in {36,48,60,72} (+keyPc=0) fits the written range 54..82
 *   5. chords map at beats 0,4,8 with legal roman tokens
 * Run:  node A4-real-verify.js
 */
const fs = require('fs');
const path = require('path');
const DIR = __dirname;
const idx = fs.readFileSync(path.join(DIR, 'index.html'), 'utf8');

// --- pull the PAT object literal out of index.html ---
const patStart = idx.indexOf('const PAT={');
const patEnd = idx.indexOf('};', patStart) + 1; // include the closing brace, not the ';'
const patSrc = idx.slice(patStart, patEnd);
// eval in a sandbox to get the real PAT
const PAT = eval('(' + patSrc.replace('const PAT=', '') + ')');

// roman tokens legal in the compiler
const ROMAN = new Set(['I△','I6','I7','ii-7','iiø','V7','V7b9','V7alt','i-','i-△',
 'IV7','VI7','vi-7','II7','bVII7','#io','IVo','V/ii','bIII7','bII7']);

const { A4_REAL_LICKS } = require('./A4-REAL-LICKS.js');

const RANGE_LO = 54, RANGE_HI = 82;
let allPass = true;
const report = [];

for (const L of A4_REAL_LICKS) {
  const errs = [];
  // 1 + 2: spans and note-count match
  let spanSum = 0;
  const offs = [];
  for (const b of L.beats) {
    const P = PAT[b.p];
    if (!P) { errs.push(`unknown pattern '${b.p}'`); continue; }
    spanSum += P.span;
    const noteCount = P.n.length; // note events the pattern expects
    const nLen = (b.n || []).length;
    if (noteCount > 0 && nLen !== noteCount)
      errs.push(`pattern '${b.p}' wants ${noteCount} notes, got ${nLen}`);
    if (noteCount === 0 && nLen !== 0)
      errs.push(`rest pattern '${b.p}' should have no n[], got ${nLen}`);
    (b.n || []).forEach(o => offs.push(o));
  }
  if (spanSum !== 16) errs.push(`spans sum to ${spanSum}, need 16`);

  // 3: spread
  const lo = Math.min(...offs), hi = Math.max(...offs);
  const spread = hi - lo;
  if (spread > 24) errs.push(`offset spread ${spread} > 24`);

  // 4: a base fits 54..82 at keyPc=0
  let fits = false, fitBase = null;
  for (const base of [36, 48, 60, 72]) {
    const ms = offs.map(o => base + o);
    if (Math.min(...ms) >= RANGE_LO && Math.max(...ms) <= RANGE_HI) { fits = true; fitBase = base; break; }
  }
  if (!fits) errs.push(`no base in {36,48,60,72} fits ${RANGE_LO}..${RANGE_HI} (offsets ${lo}..${hi})`);

  // 5: chords
  const beatsWithChord = (L.chords || []).map(c => c[0]).sort((a,b)=>a-b);
  if (JSON.stringify(beatsWithChord) !== JSON.stringify([0,4,8]))
    errs.push(`chord beats ${JSON.stringify(beatsWithChord)} != [0,4,8]`);
  for (const [,tok] of (L.chords||[])) if (!ROMAN.has(tok)) errs.push(`illegal roman token '${tok}'`);

  // minor flag consistency
  if (L.cat === '251min' && !L.minor) errs.push(`cat 251min but minor!=true`);
  if (L.cat !== '251min' && L.minor) errs.push(`minor=true but cat is ${L.cat}`);

  const ok = errs.length === 0;
  allPass = allPass && ok;
  report.push(`${ok?'PASS':'FAIL'}  ${L.id} ${L.name}  [cat=${L.cat}, spans=${spanSum}, spread=${spread}, base=${fitBase}]` +
    (ok ? '' : '\n      - ' + errs.join('\n      - ')));
}

console.log('A4-REAL-LICKS compiler-fidelity check');
console.log('PAT tokens loaded from index.html:', Object.keys(PAT).join(' '));
console.log('licks checked:', A4_REAL_LICKS.length);
console.log('-----------------------------------------------');
console.log(report.join('\n'));
console.log('-----------------------------------------------');
console.log(allPass ? 'ALL LICKS PASS' : 'SOME LICKS FAILED');
process.exit(allPass ? 0 : 1);
