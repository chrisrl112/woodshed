# public-assets/ — published hub-ingestion manifest (wood-48 / M4)

This documents **`manifest.json`**, the Woodshed spoke's **published project
manifest** — the entry point the Compound Interests portfolio hub
("chrisliquin.com") ingests to render the Woodshed automatically.

The hub model is **hub-and-spoke**: each project publishes a **manifest +
heartbeat + changelog**, and the hub ingests automatically. This is the
**publish (spoke) side** of that contract. Where `snapshot.json` ships Chris's
real progress as read-only data and `page-manifest.json` ships the safe page
images, **`manifest.json` is the structural identity card** the hub reads first:
who this project is, its status/maturity, its loops, and *where to read its
metric values from* (it carries metric **definitions**, never values).

## Files (all new, additive)

- **`manifest.json`** — the published spoke manifest. Validates against the
  hub's **Manifest schema v1**. The single ingestion entry point.
- **`CHANGELOG.md`** — Keep-a-Changelog / semver record of what changed in this
  spoke's published contract over time (the third leg of the contract).
- **`build_manifest.py`** — stdlib-only validator/checker (no `jsonschema`
  pip dependency), in the same spirit as `render_snapshot.py` /
  `verify_public_safe.py`.

## How it maps to the hub schema v1

The manifest is validated in the hub's CI against
`Portfolio Hub/build-prep/schemas/manifest.schema.json`
(`$id: …/manifest.schema.json`, `additionalProperties:false`). Required top-level
keys, exactly: `schema_version`, `slug`, `name`, `tagline`, `status`,
`maturity`, `started`, `visibility`, `stack`, `ai_roles`, `loops`, `demo`,
`links`, `metrics`, `patterns`. (`accent` / `accent_hex` are optional and are
included.) Highlights:

| Field | Value here | Hub use |
|---|---|---|
| `schema_version` | `"1.0"` | version guard (`const` "1.0") |
| `slug` | `the-woodshed` | must match `links.page` = `/projects/the-woodshed` |
| `status` | `beta` | StatusBadge; auto-flips to `dormant` after 14 days without a heartbeat |
| `maturity` | `3` | MaturityMeter (1–5) |
| `demo.type` | `video` | §7 LIVE block; flips to `embed`/`launch` only when a phase ships (embed spec §4e) |
| `metrics[]` | `streak_days` / `sessions_total` / `hours_total` | metric **definitions** (label/source/key); values read at render time from the heartbeat/snapshot |
| `patterns[]` | `daily-loop`, `heartbeat-monitoring`, `human-approve-gate`, `staleness-honesty` | cross-cutting pattern tags (enum-constrained) |

### Kept in sync with the hub-side canonical manifest

The content here is **mirrored field-for-field** from the hub's canonical copy,
`Portfolio Hub/build-prep/projects/the-woodshed/manifest.json`. The two must not
drift. `build_manifest.py` asserts this on every run (diffs the shared fields and
fails on any mismatch), so a change on one side that isn't reflected on the other
is caught, not shipped.

## Which data artifacts the hub fetches alongside the manifest

The hub schema forbids extra top-level keys (`additionalProperties:false`), so
the manifest **cannot itself carry pointers** to the data artifacts. Those
pointers are surfaced here (and in `CHANGELOG.md`) instead — this README is the
index. The hub fetches, alongside the manifest:

- **`snapshot.json`** (`schemaVersion` `"1.0"`) — the public read-only progress
  projection. Its metric keys (`streak_days` / `sessions_total` / `hours_total`)
  map 1:1 to the manifest's heartbeat metric keys, so the hub's metric join
  works unchanged. **Guard on `schemaVersion`** before rendering; if it is higher
  than the embed was built for, degrade gracefully. **Honor
  `source.illustrative`**: when `true`, label the display as a sample / demo
  (representative shape, not Chris's live numbers). Treat as **read-only** — the
  hub displays it, never writes back. (See `SNAPSHOT-README.md`.)
- **`page-manifest.json`** — the 40 copyright-safe method-book page images
  (`{id,title,source,printedPage,pdfPage,image,note}`), the safe image layer the
  hub may surface (e.g. a "what the curriculum draws from" rail). **Full source
  PDFs are never shippable** (M0 locked-content policy) — only the `pages/*.png`.

### Dormant-by-default

Per the embed spec, the hub's Woodshed embed is **dormant-by-default**: it
renders the native card only when a real, fresh snapshot URL is configured. With
nothing configured it shows the existing walkthrough video — never a fabricated
"live" surface. A **stale** snapshot (past `DORMANT_DAYS=14` via
`computeStaleNote()`) never renders as live, and any unbound metric renders `—`,
never a guessed number.

## How to regenerate / validate

```bash
cd "Projects/Trumpet/public-assets"
python3 build_manifest.py
```

- stdlib only — no pip installs (no `jsonschema`).
- **Idempotent / read-only**: `build_manifest.py` only *reads and validates*; it
  writes nothing and exits non-zero on any violation, so a bad manifest never
  ships. It checks (1) `manifest.json` against hub schema v1 (required keys,
  types, enums, `additionalProperties:false`), (2) sync with the hub-side
  canonical manifest on the shared fields, and (3) that the referenced data
  artifacts (`snapshot.json`, `page-manifest.json`) exist on disk.
- `manifest.json` is **hand-authored to mirror the hub canonical copy**; it is
  not generated from upstream state. When the hub-side manifest changes, update
  this copy to match and re-run the validator.

## `[confirm:]` items

- `demo.type` is `video` (the honest interim per embed spec §1/§4e). It flips to
  `embed` (phase 1 native card) or `launch` (phase 2 iframe) **only when that
  phase actually ships** — a hub-side coordination call, not this spoke's to make
  unilaterally. Until then, `video` is correct and intentional.
- The stable public **URLs** the hub will fetch these artifacts from
  (`PUBLIC_WOODSHED_SNAPSHOT_URL`, etc.) are set hub-side once the Woodshed is
  publicly hosted (wood-46); this contract defines the files, not their hosting.

## Guardrails honored

- `index.html` and `charts.js` were **not** touched (another task owns
  `index.html`).
- Purely **additive**: only new files created under `public-assets/`.
- `manifest.json` is kept **schema-valid** (no extra top-level keys) *and*
  **in sync** with the hub-side canonical manifest — the validator enforces both.
- No live numbers invented; the manifest carries metric **definitions**, never
  values. Anything unsourced is a `[confirm: …]` marker.
- No external/irreversible actions — files written to disk only.
