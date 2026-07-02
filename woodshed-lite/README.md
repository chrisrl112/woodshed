# Woodshed Lite

The public, hosted demo of the Woodshed — the page that runs the validation funnel
(M0 → M3). One scroll: a hook, two live stations (Warmup + Jam), a funnel.

**Full spec:** [`../docs/woodshed-lite-spec.md`](../docs/woodshed-lite-spec.md)

---

## The one rule: no fork, no drift

Lite is **not** a copy of the Woodshed. It is a *thin landing shell* that mounts the
**same engine** the full app uses, plus a build step that bundles a PD-safe subset for
static hosting.

- The engine (band, comping, drums, metronome, chart rendering) has **one home**:
  the canonical `../index.html`. Lite mounts it — it never re-implements it.
- The musical content is a **filter, not a copy**: `lite.config.js` is an allowlist of
  tune/warmup IDs that already live in `../charts/`.
- You hand-maintain only the **marketing chrome** (hero/funnel copy) and the **~6-line
  config**. Everything musical flows from canonical on rebuild.
- Lite is a **build target, not a branch.** Change the Woodshed → re-run the build →
  redeploy. Never hand-edit the engine in two places.

If you ever find yourself copy-pasting engine code into this folder, stop — that's the
drift this whole design exists to prevent.

---

## Files

| File | Hand-maintained? | What it is |
|---|---|---|
| `index.html` | ✅ yes | Landing shell — hero, pitch, funnel, footer, station *slots*. Marketing chrome only. |
| `lite.config.js` | ✅ yes | Which tunes/warmup Lite shows + funnel embed IDs + copy knobs. |
| `src/landing.css` | ✅ yes | Marketing-chrome styles (inherits the Blue Note look). |
| `src/mount.js` | ✅ yes | Mounts the shared engine into the two station slots. |
| `build-lite.sh` | rarely | Extract engine + filter charts + assemble + run gate → `dist/`. |
| `dist/` | ❌ never | Build output. Regenerated every build. Disposable. Do not hand-edit. |

---

## Build & deploy

```sh
# from the Trumpet project root:
./woodshed-lite/build-lite.sh        # → woodshed-lite/dist/  (runs the copyright gate)
```

The build:
1. Extracts the marked engine spans from `../index.html` → `dist/engine.js`
2. Filters `../charts/` to the `lite.config.js` allowlist → `dist/charts.lite.js`
3. Copies shared vendor libs + PD assets for the chosen tunes → `dist/`
4. Assembles `dist/index.html` (shell + engine + charts + mount)
5. Runs `../publish.sh` (the copyright gate) — **failure = hard stop, no deploy**

Then deploy `dist/` manually to **Cloudflare Pages / Netlify** (free static host).
The gate certifies the bundle; it never publishes. Deploy stays your manual step.

---

## Before the first real build — two Day-1 spikes

Both are flagged in the spec §3 and §8. Resolve them before building anything else:

1. **Engine boots without app state.** Confirm the extracted engine renders a chart +
   moving playhead and plays the band when handed a bare `{abc, bars, bpm, style}` —
   no `S`, no `todaysPicks`, no curriculum. The chart renderer is the risk.
2. **Audio works statically.** Confirm the band plays from `dist/` served by a dumb
   static server with `woodshed_server.py` **off**. The audio is client-side, so it
   should — but verify, don't assume.

These are the single biggest technical risks in the plan. One session resolves both.

---

## Status

Scaffold only (Jun 29, 2026). Stubs are marked `TODO`. Nothing is wired yet —
this folder is ready to build *into*, per the spec.
