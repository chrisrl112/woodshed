# Ripping iReal Pro Charts into the Woodshed — Feasibility Brief

**Date:** June 27, 2026
**Question:** Can I mass-download iReal Pro's charts (and MIDI) and ingest them into my practice app?
**Short answer:** Yes for the **chord changes** — fully solved, batchable, and exactly what the Woodshed needs. **No / don't bother** for MIDI — iReal doesn't store MIDI files, and your app already generates its own backing band from chord bars. The real prize is the chord/structure data, not audio.

---

## 1. What an iReal Pro chart actually is

iReal Pro doesn't store sheet music or audio. A "song" is a compact text string holding:

- Title, composer, **style/groove** (e.g. Medium Swing, Bossa), **key**, transpose, **BPM**, repeat count, time signature
- The **chord progression** on a fixed bar grid, with section markers (A/B/C), repeats, codas, endings

**No melody. No audio. No MIDI.** The backing tracks you hear are generated on the fly from `style + chords` — the same thing your Woodshed Band engine does. So there's no MIDI to "rip"; there's a chord grid to parse.

### Two URL formats
- **`irealbook://`** — the *old* format. Human-readable after URL-decoding, and **officially documented** by iReal Pro as an open protocol for generating charts programmatically.
- **`irealb://`** — the *current* format. Obfuscated/scrambled, but **fully reverse-engineered** years ago. Every serious tool reads it without issue.

Example of what a parser pulls out (Dear Old Stockholm, via pyRealParser):
```
Title: Dear Old Stockholm | Style: Medium Swing | Key: D- | 4/4
*A{T44D- |Eh7 A7b9|G-7 C7|F^7 | ... }*B[F^7 |G-7 C7| ... ]
→ flattened: ['D-','Eh7A7b9','G-7C7','F^7', ...]
```
That flattened bar array maps almost directly onto your concert-pitch `bars` structure in `charts.js` / `USER_CHARTS`.

---

## 2. Where the songs live (the banks)

iReal Pro ships the **app with zero songs** — deliberately, to stay clean on copyright. Songs live in the community:

- **Main Playlists page** (`irealpro.com/main-playlists`) — official curated genre sets you download as a single file.
- **Forums** (`forums.irealpro.com`) — thousands of user-shared playlists. The flagship is the community **Jazz Standards** master list, which has grown over the years: **Jazz 1300 → 1350 → 1400 → 1410 → 1460**. The "1350" you remember is just an older snapshot of the same evolving list — grab the latest (1460) instead.
- **How sharing works:** a playlist is exported as an HTML file (or a long `irealb://` URL with songs joined by `===`). You tap the link to import into the app — or feed that same file to a parser. One file = hundreds of songs.

**This is the unlock:** one Jazz 1460 HTML file → ~1,460 standards' worth of chords/keys/styles in a single parse.

---

## 3. Getting it out — the tooling (all batch-capable)

| Tool | Lang | Output | Best for |
|---|---|---|---|
| **ireal-musicxml** (infojunkie) | Node/JS | MusicXML + parsed JSON (cells, chords, key, style, bpm) | **Primary pick.** Has a CLI + library; gives you structured chord data *and* notation. Actively maintained (v2, 2024). |
| **chirp** (same author) | Web app | MusicXML / MuseScore / MIDI, batch | Zero-install GUI; upload a playlist, download converted files. Good for a quick test run. |
| **pyRealParser** | Python | Chord string + per-bar arrays + metadata | Cleanest if you want to script the transform into your JS format directly. |
| **musicxml-midi** | service | MIDI accompaniment from the MusicXML | Only if you ever want actual MIDI files (you probably don't). |

In-app export (Export → Chord Chart → MusicXML, or → MIDI) works **one song at a time, UI-only** — not batchable. Ignore it for bulk; it's a fallback for one-offs. The iReal MIDI export is just a rendering of the playback, not source data.

---

## 4. Recommended pipeline for the Woodshed

You don't want MusicXML or MIDI as your end state — you want your existing `bars` (concert pitch) + key + style structure. Shortest path:

1. **Download** the latest Jazz playlist (Jazz 1460) HTML from the forum / main-playlists page. Add any genre playlists you want.
2. **Parse** with `ireal-musicxml` (for rich structured output incl. style→groove) or `pyRealParser` (if you'd rather transform in Python). Both turn the obfuscated string into per-bar chord arrays + metadata.
3. **Transform** into your schema: map iReal chord symbols → your chord vocab (you already handle `^7 -7 h7 o7 7b9 7alt`), keep data in **concert pitch** (your convention; iReal is concert too, so no shift), carry `key`/`style`→your Band styles (swing/bossa/latin/waltz6/ballad)/`bpm`.
4. **Write** into `charts.js` as `USER_CHARTS` entries → they render in Tune Vault "My Charts" and drive your generated Band automatically. No MIDI needed — your engine builds the rhythm section from the bars.
5. **De-dupe & verify** against your existing hand-verified jam dozen (those came from *his book* and beat any auto-import — keep yours as the source of truth where they overlap; flag conflicts rather than overwrite).

Net effect: your 24 curated tunes can expand to hundreds of changes-ready tunes for the Band/solo blocks, while your verified core stays authoritative.

### Watch-outs
- **Symbol mapping gaps:** iReal has alt chords / sub-bars / rhythmic-hit notation your parser may flatten oddly. Spot-check a sample of 20 against the source.
- **Chords only:** no heads/melody — fine for your Band + solo practice, but these won't replace your transcribed `score-to-woodshed` charts where you want the actual tune.
- **Style→groove fidelity:** iReal has dozens of grooves; map them down to your 5 Band styles with a lookup table, defaulting sensibly.

---

## 5. Legal / etiquette note (brief, not preachy)

iReal Pro keeps itself clean by never distributing songs; the chord progressions to standards circulate in a long-standing gray area. For **personal practice** this is the same thing every player does with a Real Book. Just keep it personal — don't redistribute a scraped bank publicly, and you're squarely in normal-musician territory.

---

## 6. Bottom line

- **Mass download of charts:** yes — one playlist file = hundreds of tunes, parsed in minutes.
- **MIDI:** skip it — iReal has none to give, and your app doesn't need it.
- **Effort:** a short script (a few hours) using `ireal-musicxml` or `pyRealParser` → a one-time bulk import into `charts.js`, then re-run whenever you grab a new playlist.
- **Recommendation:** Do a 20-song proof run through `chirp` first to eyeball fidelity, then build the `pyRealParser`/`ireal-musicxml` → `USER_CHARTS` transform as a small reusable importer.

*Want me to build that importer next? I can write the parse→transform→charts.js script and run a test batch against a Jazz 1460 file.*
