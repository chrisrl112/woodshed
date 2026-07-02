# The Woodshed — Project Map

Jazz-trumpet practice portal + transcription/reel production pipelines. This file is the
orientation map; the folder is organized into **what ships** (served by the local web app),
**what builds it** (tooling), and **everything else** (source material, docs, archive).

## Run it
- **Launch app:** double-click `Start Woodshed.command` (serves this folder at http://localhost:8420 and opens it). `Stop Woodshed.command` kills it.
- **Pre-publish gate:** `./publish.sh` (runs `public-assets/ci_check.py`; certifies the bundle, does not deploy).
- **Build scripts run from the project root** (paths are root-relative), e.g. `python3 scripts/build_drum_manifest.py`.

## Top-level layout

| Path | What it is | Served? |
|------|-----------|---------|
| `index.html` | The entire app (single file). | ✅ entry |
| `favicon.svg` | Favicon. | ✅ |
| `charts/` | Chart data JS — `charts.js`, `charts-ireal.js`, `charts-curated.js`, `drums-manifest.js`. | ✅ |
| `vendor/` | Third-party libs — abcjs, pdf.js (+worker), qrcode. (soundfont loads from CDN.) | ✅ |
| `assets/leadsheets/` | Lead-sheet images + musicxml the app displays. | ✅ |
| `assets/warmups/` | Clarke study sheet PNGs shown in the app. | ✅ |
| `assets/drums/trim/` | The 12 served drum loops (web-friendly mp3s). | ✅ |
| `reference/` | PDFs the app opens at runtime (Real Book, Technical Studies, Cichowicz) + Real Christmas. | ✅ on demand |
| `public-assets/` | Hub publish bundle: manifest, page renders, snapshot, CI gate. Wired to the server + `publish.sh`. | build/publish |
| `woodshed_server.py` | Local server (static + `/save-day` `/save-brain` `/save-feedback`). Writes `mission-control.json`, `feedback.jsonl`, `logs/` here at runtime. | — |
| `pipelines/` | Build/production tooling — `score-engine/` (transcription), `omr/`, `reels/` (TikTok pipeline), `tools/`, `drum-source/` (raw drum samples), `wjazz/` (Weimar DB). | no |
| `scripts/` | Build/maintenance scripts — `build_drum_manifest.py`, `build_curated.py`, `ireal_import.py`, `prune_backups.py`, `woodshed_feedback_agent.py`, `git-hooks/`. | no |
| `docs/` | All briefs, specs, plans, postmortems. | no |
| `archive/` | Dormant material — `a4-vocab/` (lick experiment data, now embedded in the app), `transcription-verify/`, `standalone-exports/`, `_lead-autumn-scratch/`, the pre-cleanup snapshot. | no |
| root `*.json` | Config surface — `mission-control.example/schema`, `plan-override.example`, `woodshed-config.example`, `woodshed-copy.json`. Kept at root (read by tools via root-relative paths). | — |

## How the served paths connect (don't break these)
- `index.html` loads JS from `charts/` + `vendor/`, images from `assets/`, and opens PDFs via `getDocument('reference/'+...)`.
- `charts/drums-manifest.js` references `assets/drums/trim/*.mp3`. Regenerate with `python3 scripts/build_drum_manifest.py` (reads raw from `pipelines/drum-source`, trims into `assets/drums/trim`, writes `charts/drums-manifest.js`).
- `build_curated.py` / `ireal_import.py` read/write inside `charts/`.
- `woodshed_server.py` must stay at root: it writes `mission-control.json` here and calls `public-assets/render_snapshot.py`, which reads root-level `mission-control.json` / `mission-control.example.json`.

## Rebuild the transcription venv (deleted in cleanup, regenerable)
The 486 MB `score-engine/experiments/.venv-homr` was removed. Package list saved at
`pipelines/score-engine/experiments/homr-venv-packages.txt` (key package: `homr`). Recreate with
`python3 -m venv` + `pip install homr` (offline/AGPL — keep it out of any published bundle).

## Notes
- **No git here.** Manual `.bak` files were the only history and were deleted in this cleanup; a pre-cleanup snapshot of the critical source files is in `archive/`. Consider `git init` for real history going forward.
- A **Reels auto-watch daemon** (`pipelines/reels/Start Auto-Watch.command`) may recreate an empty `Reels/` at the root if it's still running against the old path. Restart it to point at `pipelines/reels/`.
