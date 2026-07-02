# Changelog — The Woodshed spoke (hub-ingestion contract)

All notable changes to **the Woodshed's published hub-ingestion contract** are
documented here. This is the changelog the Compound Interests hub reads to know
what changed in this spoke's published surface over time (the third leg of the
hub-and-spoke contract: **manifest + heartbeat + changelog**, hub ingests
automatically).

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this contract adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Scope note: versions here track the **published contract** (manifest + the data
artifacts the hub fetches alongside it), *not* the Woodshed app's internal build.
The app evolves independently; this file only moves when the public contract the
hub depends on changes.

## [1.0.0] — 2026-06-24

Initial published hub-ingestion contract for the Woodshed spoke (wood-48, M4).

### Added

- **`manifest.json`** — the spoke's published project manifest, validating
  against the hub's **Manifest schema v1** (`schema_version` `"1.0"`;
  `additionalProperties:false`). Carries `slug` `the-woodshed`, `status` `beta`,
  `maturity` `3`, `started` `2025-09`, `accent`/`accent_hex` `brass`/`#B5894E`,
  the four `ai_roles`, five `loops`, `demo.type` `video`,
  `links.page` `/projects/the-woodshed`, three heartbeat metric definitions
  (`streak_days` / `sessions_total` / `hours_total`), and four `patterns`. Kept
  field-for-field in sync with the hub-side canonical manifest
  (`build-prep/projects/the-woodshed/manifest.json`).
- **Data artifacts the hub fetches alongside the manifest** (already published;
  the contract points at them, it does not recreate them):
  - **`snapshot.json`** (`schemaVersion` `"1.0"`) — the public, read-only
    progress projection (streak / week / tunes / PRs / weekly objectives). Its
    metric keys map to the manifest's heartbeat keys so the hub's metric join
    works unchanged. Consumers must guard on `schemaVersion` and honor
    `source.illustrative` (label as a sample when `true`).
  - **`page-manifest.json`** — the 40 copyright-safe method-book page images
    (`{id,title,source,printedPage,pdfPage,image,note}`), the safe image layer
    the hub may surface. Full source PDFs are never shipped (M0 locked-content
    policy).
- **`MANIFEST-README.md`** — documents the manifest as the hub-ingestion entry
  point, how it maps to hub schema v1, which data artifacts the hub fetches
  alongside it, and the guardrails honored.
- **`build_manifest.py`** — stdlib-only validator: checks `manifest.json`
  against hub schema v1 (required keys, types, enums, `additionalProperties`),
  asserts it stays in sync with the hub-side canonical manifest, and verifies
  the referenced data artifacts exist on disk. Exits non-zero on any violation.

### Privacy / honesty posture

- **Sample-student / read-only only.** No metric values live in `manifest.json`
  (it carries metric *definitions*, never values — values are read at render
  time from the snapshot). The hub-facing progress is the whitelist-projected
  `snapshot.json`; no private free-text, identifiers, file paths, or raw logs.
- **Dormant-by-default.** The hub's embed activates only when a real snapshot
  URL is configured; with nothing configured it shows the existing walkthrough
  video, never a fabricated "live" surface. Stale snapshots never render as live
  (`computeStaleNote()` / `DORMANT_DAYS=14`); every unbound metric renders `—`.
- **No fabricated numbers.** Every manifest field traces to the hub-side
  canonical manifest or the embed spec; anything unsourced is written as a
  `[confirm: …]` marker rather than invented.

[1.0.0]: #100--2026-06-24
