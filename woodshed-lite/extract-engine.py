#!/usr/bin/env python3
"""
Extracts engine blocks from index.html -> dist/engine.js.
Run from Trumpet/ (the parent of woodshed-lite/).

No markers needed in index.html: blocks are located by unique
function-name anchors and closed by brace-depth tracking.
"""
import re, pathlib, sys

SRC  = pathlib.Path('index.html')
DIST = pathlib.Path('woodshed-lite/dist/engine.js')

if not SRC.exists():
    sys.exit('ERROR: index.html not found — run from Trumpet/ directory')

src   = SRC.read_text()
lines = src.splitlines()

def find_line(pat, start=0):
    for i, l in enumerate(lines[start:], start):
        if re.search(pat, l):
            return i
    raise RuntimeError(f'Pattern not found after line {start}: {pat!r}')

def brace_close(start):
    """Return index of the line containing the matching closing brace."""
    depth = 0
    for i, l in enumerate(lines[start:], start):
        depth += l.count('{') - l.count('}')
        if depth == 0 and i > start:
            return i
    raise RuntimeError(f'No closing brace found from line {start}')

chunks = []

# ── Block 1: 'use strict' + theory core + compileLick + renderABC ────────────
s = find_line(r"'use strict';")
e = brace_close(find_line(r'^function renderABC\b', s))
chunks.append(('theory+lick+renderABC', lines[s:e+1]))

# ── Block 2: full audio engine (AUDIO CORE comment → makeVamp end) ────────────
# Includes AC, Sampled, DrumLoop, Metro, ExMetro, Synth, mulberry,
# voiceLead, COMP_FEELS, compBar, CompFeel, compOptions, Band, makeVamp.
# Tuner/Drone/IntervalTrainer ride along as inert dead code — acceptable for v1.
s = find_line(r'/\* ={10,} AUDIO CORE')
e = brace_close(find_line(r'^function makeVamp\b', s))
chunks.append(('audio-engine', lines[s:e+1]))

# ── Block 3: small helper functions ──────────────────────────────────────────
for fn in ['todayKey', 'toast', 'mountABC', 'chordChartHTML']:
    s = find_line(rf'^function {fn}\b')
    e = brace_close(s)
    chunks.append((fn, lines[s:e+1]))

# ── Block 4: chart renderers (normTitle → renderUserCharts) ──────────────────
s = find_line(r'^function normTitle\b')
e = brace_close(find_line(r'^function renderUserCharts\b', s))
chunks.append(('chart-renderers', lines[s:e+1]))

# ── Assemble ──────────────────────────────────────────────────────────────────
DIST.parent.mkdir(parents=True, exist_ok=True)
parts = []
for name, chunk in chunks:
    parts.append(f'// <wsl:block:{name}>')
    parts.append('\n'.join(chunk))
    parts.append(f'// </wsl:block:{name}>')
    parts.append('')

DIST.write_text('\n'.join(parts))
total = sum(len(c) for _, c in chunks)
print(f'engine.js: {total} lines across {len(chunks)} blocks  '
      f'(from {len(lines)}-line index.html)')
print(f'Written to {DIST}')
