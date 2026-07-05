# Branding

Brand strategy, voice/positioning, and guidelines go here.

**The actual served logo/icon files stay in `/assets/brand_assets/`, not here.** `index.html` (line ~494) hardcodes `assets/brand_assets/woodshed-logo-transparent.png` as the live logo, and the app server serves the project root statically — moving that folder would break the live site unless every reference gets updated too. Not worth the risk for a folder-tidiness win, so the source files stay put. This folder is for the *thinking* behind the brand (positioning, tone, guidelines, name/identity decisions), not the asset files themselves.

**Logo v2 (2026-07-04):** Chris generated a refined axe mark and dropped it here as `new-logo.svg`. That file is actually a 4096×4096 JPEG wrapped in an SVG container (not real vector paths) — `new-logo-source-4096.jpg` is the same image extracted cleanly, kept here as the archival source. From it we built a true flat-vector version, snapped to the app's actual brand colors (`--brass:#e84e10`, `--ink:#1a150f` — see `index.html`'s `:root`, not the `#B5894E` in `public-assets/manifest.json`, which is stale/wrong), and it's now live as the canonical logo in `/assets/brand_assets/` (all 10 files) plus root `favicon.svg` and `apple-touch-icon.png`. Same filenames as before, so no code changes were needed anywhere.
