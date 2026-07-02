# public-assets/ — copyright-safe page images (wood-44 / M3)

This folder holds the **only** method-book and Real-Book page images the public
Woodshed POC is allowed to ship. It implements Chris's locked content policy
(M0):

> The public POC may show the **exact** method-book / Real-Book pages used in
> exercises, rendered as page images. The **full source PDFs are never
> shippable.**

So: only the specific pages the app actually embeds get rendered here, and the
source PDFs (`Real Book.pdf`, `Technical Studies.pdf`, `Cichowicz.pdf`) are
**never** copied into this folder. (Verified: no PDF and no >5 MB file lives
under `public-assets/`.)

## Contents

- `pages/` — 40 PNG images at ~150 DPI (one PDF page each).
- `page-manifest.json` — the contract the public build (wood-28 / wood-46)
  consumes. An array of entries; each records:
  - `id`, `title` — exercise/tune identity (matches the app's `TUNES` ids etc.)
  - `source` — which source PDF the page came from
  - `printedPage` — the printed page number (Real Book only; `null` otherwise)
  - `pdfPage` — the actual PDF page index that was rendered
  - `image` — relative path to the PNG (e.g. `pages/realbook-p386-...png`)
  - `note` — how the index was derived
  - `confirm` / `default` — uncertainty / default-selection flags (see below)
- `render_pages.py` — the reproducible generator.

## What was rendered (40 pages)

| Source | Pages | Notes |
|---|---|---|
| Real Book (`Real Book.pdf`) | 25 | 24 tunes wired into the app + 1 `page2` (Au Privave, the Bird head shown with Straight No Chaser). `pdfPage = printedPage − 1` (`RB_OFFSET=-1`). |
| Clarke (`Technical Studies.pdf`) | 7 | 6 study sections; "Second Study" spans 2 pages (pdf 6 & 7). `pdf:` numbers are PDF page indices directly. |
| Cichowicz (`Cichowicz.pdf`) | 8 | Long-tone Groups A–G (pdf 11–17, the warm-up card's reachable range) + "Set 2" (pdf 21). Warm-up default is **Group D** (pdf 14). |

### Page-index ground truth (from `index.html`)
- **Real Book:** `RB_FILE='Real Book.pdf'`, `RB_OFFSET=-1`. The app opens a tune
  with `PDFV.open(RB_FILE, printedPage + RB_OFFSET, ...)`, so the rendered PDF
  page is `printedPage − 1`. Printed page numbers come straight from each tune's
  `page:` (and `page2:`) field in the `TUNES` table.
- **Clarke:** `CLARKE_SECTIONS=[{name,pdf:N,(pages:[...])}]`. The `pdf:` value
  (or `pages:` array) is the PDF page index; no offset.
- **Cichowicz:** `CICH_SECTIONS=[{name,pdf:N}]`, `pdf:` is the PDF page index.
  The warm-up card (`FocusRender.warmup`) defaults to Group D and exposes an
  inline pager bounded to `CICH_LO..CICH_HI` = pdf **11..17** (Groups A–G).

## `[confirm:]` / flagged items
- **Cichowicz "Set 2 — Groups A–G" (pdf 21)** — flagged `confirm`. It exists in
  `CICH_SECTIONS` and the config page-picker, but is **not** reachable from the
  warm-up inline pager (which caps at pdf 17). Rendered for completeness; the
  public build should decide whether to surface it.
- **Clarke "Fourth Study" (pdf 12) and "Fifth Study" (pdf 17)** — flagged
  `confirm` because the source marks these section pages `approx:true` (the page
  is the section's best-known start, not an exercise-exact anchor).

Everything else maps deterministically and is rendered exact.

## How to regenerate

```bash
cd "Projects/Trumpet"
python3 public-assets/render_pages.py
```

Requires `/usr/bin/pdftoppm` (poppler-utils). The script reads the page set from
the constants mirrored out of `index.html`; if the app's `TUNES`,
`CLARKE_SECTIONS`, or `CICH_SECTIONS` change, update the lists at the top of
`render_pages.py` to match, then re-run. The script renders each page with:

```
pdftoppm -png -r 150 -f <pdfPage> -l <pdfPage> -singlefile "<source.pdf>" pages/<name>
```

and rewrites `page-manifest.json`.

## Guardrails honored
- `index.html` and `charts.js` were **not** modified by this task (read-only).
- No source PDF was copied into `public-assets/`.
- Purely additive: new folder + new files; source PDFs untouched.
