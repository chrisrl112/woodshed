#!/usr/bin/env python3
"""
ireal_import.py — Bulk-import iReal Pro charts into the Woodshed.

Pipeline:  irealb:// playlist (file or URL string)
       ->  pyRealParser (decodes the obfuscated format)
       ->  normalize iReal chord symbols to the app's parseChord vocabulary
       ->  per-bar CONCERT chord array  +  a chords-only ABC chart
       ->  charts-ireal.js  ( window.USER_CHARTS = (...).concat([...]) )

The Woodshed's Band engine reads `bars` (array of bars, each a list of concert
chord symbols). iReal stores changes at CONCERT pitch already, so no transpose.
No melody exists in iReal data — these are changes/Band charts, by design.

Usage:
    pip install pyRealParser --break-system-packages
    python3 ireal_import.py <playlist.txt> [-o charts-ireal.js] [--limit N]

The input file may contain either a raw `irealb://...` URL or HTML exported by
iReal Pro that contains such a URL.
"""
import re, sys, json, argparse, html, urllib.parse
from pyRealParser import Tune

# ---------------------------------------------------------------- chord mapping
# The app's parseChord() matches a suffix regex then defaults unmatched -> dom7.
# It already understands: maj7, 6, m7b5(ø), dim7(o), mM7, m6, m7(-), 7alt(+),
# 7b9/7#9, 7#11, 7sus(sus), and bare/7 -> dominant.  We only have to translate
# iReal's caret(^ = major) and h(= half-diminished); the rest pass straight in.

def _norm_quality(q: str) -> str:
    q = q.replace('(', '').replace(')', '')
    q = re.sub(r'-\^(\d*)', 'mM7', q)   # minor-major  (C-^7)
    q = re.sub(r'\^(\d*)', 'maj7', q)   # major        (C^, C^7, C^9 -> Cmaj7)
    q = re.sub(r'h(\d*)', 'm7b5', q)    # half-dim      (Eh7 -> Em7b5)
    return q

def to_app_chord(tok: str):
    """iReal chord token -> a parseChord-friendly symbol, or None for N.C."""
    tok = tok.replace('(', '').replace(')', '').strip()
    if not tok or tok.lower() in ('n', 'nc', 'n.c.', 'x', 'r', 'p', 'w'):
        return None
    tok = tok.split('/')[0]             # drop slash bass; band plays the chord
    m = re.match(r'^([A-G][b#]?)(.*)$', tok)
    if not m:
        return None
    return m.group(1) + _norm_quality(m.group(2))

def to_display(tok: str) -> str:
    """Pretty chart text for the ABC lead sheet (keeps slash basses)."""
    tok = tok.replace('(', '').replace(')', '').strip()
    tok = tok.replace('-^', '-Δ').replace('^', 'Δ')  # ^ -> Δ
    tok = re.sub(r'h(\d*)', 'ø\\1', tok)                  # h -> ø
    tok = re.sub(r'(?<=[A-G#b])o(\d*)', '°\\1', tok)      # o -> ° (dim)
    return tok

# --------------------------------------------------------------- bar splitting
# pyRealParser's measures_as_strings flattens repeats/codas but concatenates
# multiple chords in a bar ('G-7C7'). Split before any root letter A-G that is
# not the first char and not a slash bass (preceded by '/').

def split_chords(measure: str):
    measure = measure.strip()
    if not measure:
        return []
    parts, buf = [], ''
    for i, ch in enumerate(measure):
        if ch in 'ABCDEFG' and buf and buf[-1] != '/':
            parts.append(buf); buf = ch
        else:
            buf += ch
    if buf:
        parts.append(buf)
    return [p for p in parts if p.strip()]

# --------------------------------------------------------------------- styles
def map_style(s: str) -> str:
    s = (s or '').lower()
    if 'bossa' in s: return 'bossa'
    if any(k in s for k in ('latin', 'samba', 'afro', 'mambo', 'cha', 'calypso',
                            'baiao', 'songo', 'bolero', 'rhumba', 'rumba')):
        return 'latin'
    if 'waltz' in s: return 'waltz6'
    if 'ballad' in s: return 'ballad'
    return 'swing'

DEFAULT_BPM = {'ballad': 72, 'bossa': 140, 'latin': 190, 'waltz6': 160, 'swing': 160}

def pretty_key(k: str) -> str:
    return (k or 'C').replace('-', 'm')

def abc_key(k: str) -> str:
    k = k or 'C'
    root = k.replace('-', '')
    return root + ('m' if '-' in k else '')

def slugify(t: str) -> str:
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', t.lower())).strip('-') or 'tune'

# ----------------------------------------------------------------- ABC builder
def build_abc(title, composer, key, bars_display, meter='4/4'):
    beats = 3 if meter.startswith('3') else 4
    head = (f"X:1\nT:{title}\n" + (f"C:{composer}\n" if composer else '')
            + f"M:{meter}\nL:1/4\nK:{abc_key(key)}\n")
    lines, line = [], []
    for bar in bars_display:
        chords = bar if bar else ['']
        n = len(chords)
        # distribute `beats` invisible rests across the chords in the bar
        if n == 1:
            spans = [beats]
        elif n >= beats:
            spans = [1] * beats
            chords = chords[:beats]
        else:
            base, extra = divmod(beats, n)
            spans = [base + (1 if i < extra else 0) for i in range(n)]
        cell = ''
        for c, sp in zip(chords, spans):
            tag = f'"{c}"' if c else ''
            cell += f'{tag}x{sp} '
        line.append(cell.strip())
        if len(line) == 4:
            lines.append(' | '.join(line) + ' |'); line = []
    if line:
        lines.append(' | '.join(line) + ' |')
    return head + '\n'.join(lines)

# --------------------------------------------------------------------- convert
def convert_tune(t):
    measures = [m for m in t.measures_as_strings]
    bars, bars_display, prev = [], [], None
    for meas in measures:
        toks = split_chords(meas)
        app = [c for c in (to_app_chord(x) for x in toks) if c]
        disp = [to_display(x) for x in toks if to_app_chord(x)]
        if not app:                     # N.C. / blank -> hold previous chord
            if prev:
                bars.append(list(prev)); bars_display.append(list(prev_d))
            continue
        bars.append(app); bars_display.append(disp)
        prev, prev_d = app, disp
    if not bars:
        return None
    style = map_style(t.style)
    meter = f"{t.time_signature[0]}/{t.time_signature[1]}" if t.time_signature else '4/4'
    bpm = int(t.bpm) if str(t.bpm).strip().isdigit() and int(t.bpm) > 0 else DEFAULT_BPM[style]
    return {
        'id': slugify(t.title),
        'title': t.title,
        'source': f"iReal Pro import — {t.composer or 'Unknown'}",
        'key': pretty_key(t.key) + ' (concert)',
        'style': style,
        'bpm': int(bpm),
        'abc': build_abc(t.title, t.composer, t.key, bars_display, meter),
        'bars': bars,
    }

def extract_url(text: str) -> str:
    text = html.unescape(text)
    m = re.search(r'irealb(?:ook)?://\S+', text)
    return m.group(0) if m else text.strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input')
    ap.add_argument('-o', '--out', default='charts/charts-ireal.js')
    ap.add_argument('--limit', type=int, default=0)
    args = ap.parse_args()

    raw = open(args.input, encoding='utf-8').read()
    url = extract_url(raw)
    tunes = Tune.parse_ireal_url(url)
    if args.limit:
        tunes = tunes[:args.limit]

    charts, seen, errs = [], {}, 0
    for t in tunes:
        try:
            c = convert_tune(t)
            if not c:
                continue
            if c['id'] in seen:
                seen[c['id']] += 1
                c['id'] = f"{c['id']}-{seen[c['id']]}"
            else:
                seen[c['id']] = 1
            charts.append(c)
        except Exception as e:
            errs += 1
            print(f"  ! skipped {getattr(t,'title','?')}: {e}", file=sys.stderr)

    banner = ("/* THE WOODSHED — iReal Pro bulk import (generated by ireal_import.py).\n"
              "   Chords only (iReal has no melody); CONCERT pitch; band-ready.\n"
              f"   {len(charts)} charts. Re-run the importer to regenerate. */\n")
    body = "window.USER_CHARTS=(window.USER_CHARTS||[]).concat(\n"
    body += json.dumps(charts, ensure_ascii=False, indent=1)
    body += "\n);\n"
    open(args.out, 'w', encoding='utf-8').write(banner + body)
    print(f"Wrote {len(charts)} charts to {args.out}  ({errs} skipped)")

if __name__ == '__main__':
    main()
