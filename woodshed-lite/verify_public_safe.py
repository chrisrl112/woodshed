#!/usr/bin/env python3
"""
Copyright gate for Woodshed Lite.

Rules:
  - abc: null           → changes-only, always safe
  - abc with only chord symbols + 'x' spacers → changes-only, always safe
  - abc with real pitch letters → BLOCKED unless tune.year <= 1930 (PD)

Usage: python3 verify_public_safe.py lite.config.js
"""
import re, pathlib, sys

def abc_has_melody(abc_str):
    """Return True if the ABC body contains real pitch letters (not just x spacers)."""
    # Strip ABC header fields (lines like X:, T:, M:, L:, K:, C:)
    lines = abc_str.split('\\n')
    body_lines = [l for l in lines if not re.match(r'^[A-Z]:', l.strip())]
    body = ' '.join(body_lines)
    # Remove chord symbol annotations: "..."
    body = re.sub(r'"[^"]*"', '', body)
    # Remove x spacers, bar lines, digits, spaces, decorators
    body = re.sub(r'[x|0-9/\s\'\-,\.!]', '', body)
    # If any note pitch letter remains, it's a melody
    return bool(re.search(r'[A-Ga-g]', body))

config_path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'lite.config.js')
if not config_path.exists():
    sys.exit(f'ERROR: {config_path} not found')

text = config_path.read_text()

errors = []

# Find all abc: `...` template literals
for m in re.finditer(r'abc:\s*`([^`]*)`', text):
    abc = m.group(1)
    if abc_has_melody(abc):
        # Find associated year field (search backwards in the tune block)
        before = text[:m.start()]
        year_m = re.search(r'year:\s*(\d{4})', before[-500:])
        if year_m:
            year = int(year_m.group(1))
            if year <= 1930:
                continue  # Public domain — OK
        errors.append(
            f'Lead sheet melody detected (non-PD): {abc[:60]!r}...\n'
            f'  Add year: XXXX to the tune entry. Only year <= 1930 is PD-safe.'
        )

if errors:
    print('COPYRIGHT GATE FAILED:')
    for e in errors:
        print(f'  {e}')
    sys.exit(1)

abc_count  = len(re.findall(r'abc:\s*`', text))
null_count = len(re.findall(r'abc:\s*null', text))
print(f'Copyright gate PASSED  '
      f'({abc_count} changes-only ABC, {null_count} changes-only null)')
