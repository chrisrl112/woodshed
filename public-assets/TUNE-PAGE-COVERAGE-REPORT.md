# Tune → Page-Image Coverage Report (wood-45 / M3)

**Tool:** `public-assets/verify_tune_page_coverage.py`
**Generated for:** wood-45 ("Tunes public treatment — Real Book tune pages may show
as page-images; full book never available"), milestone M3.
**Run date:** 2026-06-25.

---

## What this checks (and why)

The verifier proves the **missing direction** of the existing public-bundle checks:

- **wood-44** rendered the exact pages the app uses and wrote `page-manifest.json`.
- **wood-28** (`verify_public_safe.py`) asserts no source PDFs leak and that the
  manifest and `pages/` match two-ways.
- **Nothing** checked that **every tune the app actually references is covered by a
  public page-image.** That is this tool's job.

For every tune `page:<N>` reference inside `index.html`, it asserts there is a
manifest entry with `source == "Real Book.pdf"` and `printedPage == N` **whose image
file actually exists** under `public-assets/pages/`.

**Why it matters (M0 + M3):** the M0 content policy ships only the *exact* pages used,
as images, and never the full book. If a tune points at a Real Book page that was never
rendered, the M3 public build would show nothing for that tune — or tempt a
policy-violating fallback to the source PDF. This catches that at build time.

It is **stdlib-only, read-only, and additive** — it writes nothing and edits nothing.

### Classification rules
- **COVERED** — tune `page:<N>` has a Real Book manifest entry at `printedPage == N`
  and the image file exists. (pass)
- **MISSING (gap)** — tune `page:<N>` with no Real Book manifest entry at that page,
  or whose manifest image file is missing on disk. **(fails the build)**
- **ORPHAN/EXTRA** — Real Book manifest page rendered but referenced by no tune.
  *Informational only; never fails.*
- **SKIPPED** — a `page:<N>` with no tune `id`/`title` around it (e.g. the PDF
  viewer's internal `page:1` state). *Not a tune ref, not a gap.*

Tune refs are extracted by reading the whole file and regex-scanning it (robust to
`index.html`'s very long minified lines); a `page:<N>` is only counted as a tune ref
if a tune `id:'...'` **and** `title:'...'` appear in the short text window just before
it — which is how the PDF-viewer `page:1` is correctly excluded.

## How to run

```
cd "Projects/Trumpet/public-assets"
python3 verify_tune_page_coverage.py --verbose
```

Exit `0` = every tune page is covered; exit non-zero = coverage gaps (each listed).
Paths resolve relative to the script's own directory, so it runs from anywhere. Override
with `--app-html <path>` and `--manifest <path>` if needed.

---

## ACTUAL current findings (2026-06-25)

**Verdict: FAIL (exit 1) — 1 coverage gap.**

| Metric | Count |
|---|---|
| Tune `page:` refs found | 25 |
| COVERED | 24 |
| **MISSING (gaps)** | **1** |
| Real Book manifest pages (universe) | 25 |
| ORPHAN/EXTRA (info) | 1 |
| Non-tune `page:` refs skipped | 1 |

### The one gap — Solar page number mismatch
- **Tune `solar` ("Solar", Miles Davis) references `page:363` in `index.html`**, but
  there is **no Real Book manifest entry at printedPage 363**. → reported MISSING.
- The rendered image we *do* have is **`pages/realbook-p365-solar.png`** at
  `printedPage:365`, which **no tune references** → reported as the lone ORPHAN/EXTRA.

So this is **not** a "page was never rendered" gap — it is a **2-page number mismatch
between the app and the manifest** for the same tune (Solar). One of the two is wrong:
either the app's `page:363` should be `365`, or the rendered/manifest page should be
363. `[confirm: which page number is the correct printed Real Book page for Solar —
the app's 363 or the manifest's 365? Resolving that picks the fix.]`

**Follow-on (do NOT do tonight — needs the source PDF / a separate task):**
- Decide the correct Solar printed page, then EITHER correct `index.html` `solar.page`
  to match the existing `p365` image, OR re-render Solar at `p363` and update the
  manifest. This is an app-data / render task, not something to fix blind.

### The skipped (non-tune) ref — correctly ignored
- `page:1` inside `const PDFV={doc:null,page:1,...}` is the PDF viewer's internal state,
  not a tune reference. The tool skips it (no tune id/title anchor). Not a gap.

### Coverage otherwise is clean
The other **24** tune references all resolve to an existing Real Book page-image
(includes the secondary `page:37` Au Privave head used by the Straight No Chaser tune).
No tune points at a non-Real-Book source. The non-tune Clarke/Cichowicz method-book
images in the manifest are warm-up/etude content and are out of the tune universe by
design (they use `pdfPage`, `printedPage == null`).

---

## What Chris / the night manager should eyeball first
1. **The Solar 363↔365 mismatch** — this is a real app/manifest divergence, the single
   thing to resolve. Pick the correct page, then fix the one side that's wrong.
2. Once Solar is reconciled, this verifier should go **green (exit 0)** and can be wired
   into the M3 public-build CI alongside `verify_public_safe.py`.
