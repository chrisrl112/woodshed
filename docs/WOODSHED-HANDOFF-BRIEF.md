# The Woodshed — Handoff Brief

**App:** `Trumpet/index.html` — single-file vanilla-JS jazz-trumpet practice portal (abcjs + pdf.js + Web Audio). Served via `Start Woodshed.command` → `woodshed_server.py` on localhost:8420 (force-restarts on launch). Verifier harnesses live in `omr/_verify_*.mjs` (jsdom; run with `node`).

## What was built this session

**1. iReal Pro import.** `ireal_import.py` parses an `irealb://` playlist (pyRealParser) → `charts-ireal.js` (1,459 charts, chords-only, concert pitch). Source: `Jazz 1460.html`. Loaded lazily (only when "My Charts" opens) to keep page load fast; My Charts renders a capped, searchable slice (was freezing on 1,460 abcjs renders).

**2. Band engine upgrades** (all in `index.html`):
- **Real drums** (`DrumLoop`): drop audio in `lib/drums/Downbeat/` (named "Style BPM"), run `build_drum_manifest.py` → `drums-manifest.js`; trims to gapless 3-min mp3s. Per-tune picker (🥁), tempo-follows via playbackRate, sample-accurate downbeat start, mutes synth kit. Curated tunes only.
- **Comping engine** (`COMP_FEELS` evans/garland/jamal + `voiceLead`): voice-led rootless voicings, idiomatic off-beat rhythms, anticipations, humanization, "sustain"/"busy" live knobs, per-tune feel picker (🎹). Replaced the old mechanical comp.
- **Mid-take fixes:** sound source frozen per take (no synth→sample swap); `DrumLoop.whenReady` cues so one click plays correctly (no stop/replay).

**3. Reel Studio** (`launchReel`, 🎬 button on Today + each tune): 1080×1920 canvas overlay for TikTok, recorded via MediaRecorder (mp4-preferred). Implements the Claude-design spec: green chroma field + floating tan card, "THE WOODSHED" masthead + orange bar, NOW PLAYING·MODE·KEY kicker, Real Book notation strip (head only), divided chord cells (current measure orange, lights only on the song's downbeat after count-in), Stop→save dialog. Compact/right-safe so TikTok's UI doesn't overlap. Settings persist.

**4. Real Book line cropping — the hard part.** Auto-detecting staves on the scans is unreliable (light/broken staff lines, shared pages, OCR can't read titles). Built a **calibrate-once tool** (🎯 Calibrate lines): renders the tune's page, user drags one box per line top→bottom, saved per tune in localStorage (`woodshed_reelcal`, via `ReelCal`). `drawNotation` uses calibrated boxes first, auto-detection (`detectSystems`) as fallback. Variable measures-per-line supported via per-tune `lineBars` (e.g. solar `[3,3,3,3]`, recordame `[2,3,3,3,3,2]`).

## Known issues / next steps
- **Calibrate the reel tunes** Chris actually posts (Solar first — its page shares with another tune). Auto-detect won't be right for shared-page/3-per-line tunes until calibrated.
- **Curated chord accuracy:** the imported "Jazz 1460" community playlist is NOT identical to Chris's own iReal Pro charts (diverges per tune — TWNBAY proved it). The `overlayIreal` auto-overlay is intentionally OFF (`charts-curated.js` not loaded). Fix curated changes by editing inline `TUNES[].bars` (concert pitch) from Chris's iReal. Best long-term: have Chris export HIS iReal playlist and regenerate `build_curated.py` from that, then re-enable the overlay. TWNBAY already hand-corrected.
- Reel calibration UX: could add click-top/click-bottom or snapping if drag-boxes feel fiddly.
- Verifiers to run after edits: `omr/_verify_reel.mjs`, `_verify_comp.mjs`, `_verify_drums.mjs`, `_verify_systems.mjs` (note: `const` globals tested via `window.eval`; jsdom can't render real canvas/audio — visual + recording are Chris-verified only).

## Memory
Durable notes saved under the space's memory: `project-woodshed-portal`, `-ireal-importer`, `-drums`, `-comping`, `-reel` (read these first).
