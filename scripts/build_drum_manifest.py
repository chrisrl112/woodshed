#!/usr/bin/env python3
"""
build_drum_manifest.py — scan assets/drums/ and emit drums-manifest.js (window.DRUM_TRACKS).

For each audio file it parses BPM + style from the filename and detects the
lead-in (seconds of intro/silence before the groove starts) so playback can
begin on the groove, not the dead air. Re-run whenever you add tracks.

    python3 build_drum_manifest.py
"""
import glob, os, re, io, json, subprocess, wave, array, urllib.parse

DRUM_DIR = 'assets/drums'
DOWNBEAT_DIR = 'pipelines/drum-source'   # preferred: files cut to start exactly on the downbeat
OUT = 'charts/drums-manifest.js'
EXT = ('.mp3', '.wav', '.m4a', '.aif', '.aiff', '.flac', '.ogg')

def parse_bpm(name):
    m = re.search(r'(\d{2,3})\s*bpm', name, re.I)        # "150 bpm"
    if m: return int(m.group(1))
    for n in re.findall(r'(?<![\dk])(\d{2,3})(?!k)', name):  # bare tempo like "Bossa 150" (skip "128k")
        if 40 <= int(n) <= 320: return int(n)
    return None

def parse_style(name):
    n = name.lower()
    if 'bossa' in n:                                   return 'bossa', 'Bossa'
    if any(k in n for k in ('samba','latin','mambo','afro','songo','rhumba','rumba','calypso')):
        return 'latin', 'Latin'
    if 'waltz' in n:                                   return 'waltz6', 'Waltz'
    if 'ballad' in n:                                  return 'ballad', 'Ballad'
    if 'funk' in n:                                    return 'funk', 'Funk'    # straight-8th band branch (see _compat / scheduleBar)
    if 'brush' in n:                                   return 'swing', 'Brushes'
    return 'swing', 'Swing'

def detect_leadin(path):
    """Seconds of leading SILENCE to skip — gets playback past the dead air to the track's
    first real sound. This is a starting point only; lock beat-1 to the pocket by ear with
    the per-track nudge in the app (exact downbeat can't be detected reliably offline)."""
    try:
        out = subprocess.run(
            ['ffmpeg','-v','quiet','-i',path,'-ac','1','-ar','8000','-t','25','-f','wav','pipe:1'],
            capture_output=True).stdout
        w = wave.open(io.BytesIO(out)); sr = w.getframerate()
        a = array.array('h'); a.frombytes(w.readframes(w.getnframes()))
        if not a: return 0.0
        peak = max(abs(x) for x in a) or 1
        thr = peak * 0.10                                  # just past silence; first audible hit
        onset = next((i for i, x in enumerate(a) if abs(x) > thr), 0)
        return round(onset / sr, 3)
    except Exception:
        return 0.0

def duration(path):
    try:
        out = subprocess.run(['ffprobe','-v','quiet','-show_entries','format=duration',
                              '-of','csv=p=0', path], capture_output=True, text=True).stdout.strip()
        return float(out)
    except Exception:
        return 0.0

TRIM_DIR = os.path.join(DRUM_DIR, 'trim')
TRIM_OVER = 210     # files longer than this get trimmed...
TRIM_TO   = 180     # ...to this many seconds (loops seamlessly for longer takes)

def prepare(path):
    """Return a light, web-friendly copy to actually load: a <=3-min MP3. Big/uncompressed
    sources (AIFF/WAV) and long files get transcode-trimmed to assets/drums/trim/; short MP3s
    are used as-is. MP3 is encoded gapless (LAME) so decodeAudioData starts at true t=0 —
    keeping a downbeat-cut file on the downbeat. Trims the END, so any leadIn stays valid."""
    ext = os.path.splitext(path)[1].lower()
    if ext == '.mp3' and duration(path) <= TRIM_OVER:
        return path
    os.makedirs(TRIM_DIR, exist_ok=True)
    base = os.path.splitext(os.path.basename(path))[0] + f'__{TRIM_TO}s.mp3'
    out = os.path.join(TRIM_DIR, base)
    if not (os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(path)):
        subprocess.run(['ffmpeg','-nostdin','-v','quiet','-y','-i',path,'-t',str(TRIM_TO),
                        '-c:a','libmp3lame','-b:a','160k', out], check=False)
    return out if os.path.exists(out) else path

def slug(s):
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', s.lower())).strip('-')

def main():
    # Prefer the Downbeat/ folder (files cut to start exactly on beat 1 → leadIn 0, no nudge).
    db_files = sorted(f for f in glob.glob(os.path.join(DOWNBEAT_DIR, '*')) if f.lower().endswith(EXT))
    downbeat = bool(db_files)
    files = db_files if downbeat else sorted(
        f for f in glob.glob(os.path.join(DRUM_DIR, '*')) if f.lower().endswith(EXT))
    print(f"Source: {DOWNBEAT_DIR if downbeat else DRUM_DIR}  ({len(files)} files)")
    tracks = []
    for path in files:
        name = os.path.basename(path)
        bpm = parse_bpm(name)
        style, feel = parse_style(name)
        if not bpm:
            print(f"  ! {name}: no BPM in filename, skipping"); continue
        leadin = 0.0 if downbeat else detect_leadin(path)   # downbeat files already start on beat 1
        use_path = prepare(path)                              # light web-friendly mp3 copy
        rel = use_path.replace(os.sep, '/')
        trimmed_note = '  (trimmed)' if use_path != path else ''
        label = f"{feel} {bpm}"
        tracks.append({
            'id': slug(label),
            'label': label,
            'url': '/'.join(urllib.parse.quote(seg) for seg in rel.split('/')),
            'file': os.path.basename(use_path),
            'bpm': bpm,
            'style': style,
            'feel': feel,
            'leadIn': leadin,
        })
        print(f"  + {label:16s} style={style:7s} bpm={bpm} leadIn={leadin}s{trimmed_note}")
    js = ("/* THE WOODSHED — real drum tracks (generated by build_drum_manifest.py).\n"
          "   Drop audio in pipelines/drum-source/ (raw) or assets/drums/ with BPM + style in the filename, then re-run. */\n"
          "window.DRUM_TRACKS = " + json.dumps(tracks, ensure_ascii=False, indent=1) + ";\n")
    open(OUT, 'w', encoding='utf-8').write(js)
    print(f"Wrote {len(tracks)} tracks to {OUT}")

if __name__ == '__main__':
    main()
