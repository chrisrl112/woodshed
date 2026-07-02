#!/usr/bin/env python3
"""
verify_tune_page_coverage.py — wood-45 / milestone M3 — tune→page-image coverage

WHAT THIS PROVES
    Every Real Book page the app's TUNES actually reference (`page:<N>` inside a
    tune data object in index.html) has a corresponding PRE-RENDERED public
    page-image — a manifest entry whose printedPage == N AND whose image file
    exists on disk under pages/. Any app tune page with no covering image is a
    coverage GAP and fails the build.

WHY (Chris's content policy + the public-build path)
    M0 content policy (locked 6/18): the public Woodshed may show the EXACT pages
    used in exercises, rendered as page IMAGES — but the FULL source book is NEVER
    shippable. wood-44 RENDERED those pages and built the manifest; wood-28's
    verify_public_safe.py asserts no source PDFs leak and that the manifest and
    pages/ match two-ways. But neither checks the OTHER direction: that every tune
    the app references is actually COVERED by a public image. This script closes
    that gap, protecting the M3 public-build path: if a tune points at a Real Book
    page we never rendered, the public build would either show nothing or tempt a
    policy-violating fallback to the source PDF. Catch it at build time instead.

    This is purely ADDITIVE and read-only. It writes nothing and changes nothing.

SCOPE — what is and is NOT a failure
    UNIVERSE: tune page references are Real Book pages, so the "tune page universe"
    is manifest entries with source == "Real Book.pdf" (printedPage is the human
    page number that matches the app's page:<N>). Non-Real-Book manifest entries
    (Clarke / Cichowicz method books, which use pdfPage and have printedPage==null)
    are warm-up/etude content, not tunes, and are reported informationally only.

    FAIL (coverage gap): an app tune page:<N> with no Real Book manifest entry at
        printedPage == N, OR whose manifest image file is missing on disk.
    INFORMATIONAL (never fails): ORPHAN/EXTRA — Real Book manifest pages not
        referenced by any tune (e.g. a secondary page rendered but not yet wired).
    SKIPPED (not a gap): a `page:<N>` occurrence with no tune id/title around it is
        not a tune reference (e.g. the PDF viewer's internal `page:1` state) and is
        reported as skipped, not counted against coverage.

HOW TUNE REFS ARE EXTRACTED (robust to very long minified lines)
    The whole file is read and regex-scanned (NOT line-by-line). Each `page:<N>` is
    kept only if a tune `id:'...'` AND `title:'...'` appear in the short window of
    text immediately before it — that anchors the match to a real tune data object
    and excludes incidental `page:` uses elsewhere in the JS.

USAGE
    python3 verify_tune_page_coverage.py [--verbose]
        [--app-html PATH] [--manifest PATH]
    # defaults resolve relative to this script's own directory, so it runs anywhere
    # exit 0 = every tune page is covered; non-zero = coverage gaps (each listed)

stdlib only (argparse, json, re, sys, pathlib) — no pip installs.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Defaults — resolved relative to this script's directory so it runs anywhere.
# --------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent          # .../public-assets
TRUMPET = HERE.parent                            # .../Projects/Trumpet

DEFAULT_APP_HTML = TRUMPET / "index.html"
DEFAULT_MANIFEST = HERE / "page-manifest.json"
PAGES_DIRNAME = "pages"

# The manifest source string that marks the tune page universe (Real Book).
REALBOOK_SOURCE = "Real Book.pdf"

# How far back to look (in characters) for a tune id/title anchoring a page:<N>.
# Tune objects are compact; 320 chars comfortably covers id:'...',title:'...'
# preceding the page field without reaching into a neighbouring object.
ANCHOR_WINDOW = 320

# Match a tune page reference: page : <digits>
PAGE_RE = re.compile(r"page\s*:\s*(\d+)")
# id:'...' and title:'...' (single-quoted JS string literals, escapes tolerated).
ID_RE = re.compile(r"id\s*:\s*'((?:[^'\\]|\\.)*)'")
TITLE_RE = re.compile(r"title\s*:\s*'((?:[^'\\]|\\.)*)'")


def extract_tune_page_refs(html_text):
    """Return (tune_refs, skipped).

    tune_refs: list of dicts {page:int, id:str|None, title:str|None, snippet:str}
               for each page:<N> anchored to a tune object (has id and title near).
    skipped:   list of dicts {page:int, snippet:str} for page:<N> with no tune
               anchor (e.g. the PDF viewer's page:1 state) — informational.
    """
    tune_refs = []
    skipped = []
    for m in PAGE_RE.finditer(html_text):
        page = int(m.group(1))
        win_start = max(0, m.start() - ANCHOR_WINDOW)
        window = html_text[win_start:m.start()]
        ids = ID_RE.findall(window)
        titles = TITLE_RE.findall(window)
        snip_start = max(0, m.start() - 60)
        snippet = html_text[snip_start:m.end() + 20].replace("\n", " ")
        if ids and titles:
            tune_refs.append({
                "page": page,
                "id": ids[-1],
                "title": titles[-1],
                "snippet": snippet,
            })
        else:
            skipped.append({"page": page, "snippet": snippet})
    return tune_refs, skipped


def load_manifest(manifest_path):
    """Return (entries, error). entries is the parsed JSON list, error is a str or None."""
    if not manifest_path.is_file():
        return None, "manifest not found: {}".format(manifest_path)
    try:
        entries = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return None, "manifest unreadable / invalid JSON: {} ({})".format(manifest_path, e)
    if not isinstance(entries, list):
        return None, "manifest must be a JSON array of entries: {}".format(manifest_path)
    return entries, None


def build_realbook_index(entries):
    """Map printedPage(int) -> list of Real Book manifest entries at that page."""
    index = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if entry.get("source") != REALBOOK_SOURCE:
            continue
        pp = entry.get("printedPage")
        if not isinstance(pp, int):
            continue
        index.setdefault(pp, []).append(entry)
    return index


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Build-time coverage verifier (wood-45 / M3): assert every tune "
            "page:<N> reference in the app has a covering Real Book page-image "
            "(manifest entry at printedPage==N with the image file on disk). "
            "Exit 0 = fully covered, non-zero = coverage gaps."
        ),
        epilog=(
            "Orphan/extra manifest pages (rendered but not referenced by a tune) "
            "are informational only and never cause failure. The complementary "
            "no-PDF-leak / manifest<->pages two-way check is wood-28's "
            "verify_public_safe.py."
        ),
    )
    parser.add_argument("--app-html", default=str(DEFAULT_APP_HTML),
                        help="Path to the app HTML (default: ../index.html).")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST),
                        help="Path to page-manifest.json (default: ./page-manifest.json).")
    parser.add_argument("--verbose", action="store_true",
                        help="Print COVERED / MISSING / ORPHAN / SKIPPED detail lists.")
    args = parser.parse_args(argv)

    app_html = Path(args.app_html).resolve()
    manifest_path = Path(args.manifest).resolve()
    pages_dir = manifest_path.parent / PAGES_DIRNAME

    print("Woodshed tune->page-image coverage verifier (wood-45, M3)")
    print("App HTML : {}".format(app_html))
    print("Manifest : {}".format(manifest_path))
    print("Pages dir: {}".format(pages_dir))
    print("-" * 70)

    # --- Load inputs ---
    if not app_html.is_file():
        print("FAIL: app HTML not found: {}".format(app_html))
        return 1
    html_text = app_html.read_text(encoding="utf-8")

    entries, err = load_manifest(manifest_path)
    if err:
        print("FAIL: {}".format(err))
        return 1

    tune_refs, skipped = extract_tune_page_refs(html_text)
    rb_index = build_realbook_index(entries)

    # --- Classify each tune ref as COVERED or MISSING ---
    covered = []   # (ref, entry, image_rel)
    missing = []   # (ref, reason)
    referenced_pages = set()

    for ref in tune_refs:
        page = ref["page"]
        referenced_pages.add(page)
        matches = rb_index.get(page, [])
        if not matches:
            missing.append((ref, "no Real Book manifest entry at printedPage == {}".format(page)))
            continue
        # Prefer a match whose image file exists on disk.
        ok_entry = None
        for entry in matches:
            img_rel = entry.get("image", "")
            if img_rel and (manifest_path.parent / img_rel).is_file():
                ok_entry = entry
                break
        if ok_entry is None:
            entry = matches[0]
            img_rel = entry.get("image", "<no image field>")
            missing.append((ref,
                            "manifest entry at printedPage == {} exists (id={!r}) "
                            "but its image file is missing on disk: {}".format(
                                page, entry.get("id", "?"), img_rel)))
        else:
            covered.append((ref, ok_entry, ok_entry.get("image")))

    # --- ORPHAN / EXTRA: Real Book manifest pages no tune references (informational) ---
    orphans = []
    for pp in sorted(rb_index):
        if pp not in referenced_pages:
            for entry in rb_index[pp]:
                orphans.append((pp, entry))

    # --- Report ---
    print("[summary] tune page refs found : {}".format(len(tune_refs)))
    print("[summary]   COVERED            : {}".format(len(covered)))
    print("[summary]   MISSING (gaps)     : {}".format(len(missing)))
    print("[summary] Real Book manifest pages (universe): {}".format(len(rb_index)))
    print("[summary]   ORPHAN/EXTRA (info): {}".format(len(orphans)))
    print("[summary] non-tune page: refs skipped       : {}".format(len(skipped)))

    if args.verbose:
        print("-" * 70)
        print("COVERED (app page -> image file):")
        for ref, entry, img in sorted(covered, key=lambda r: r[0]["page"]):
            print("  - p{:>3}  {:<32}  ->  {}".format(ref["page"], ref["title"][:32], img))

        print("MISSING (coverage GAPS — app references a page with no usable image):")
        if not missing:
            print("  (none)")
        for ref, reason in sorted(missing, key=lambda r: r[0]["page"]):
            print("  - p{:>3}  {:<32}  [{}]  {}".format(
                ref["page"], (ref["title"] or "?")[:32], ref["id"] or "?", reason))

        print("ORPHAN/EXTRA (Real Book pages rendered but not referenced by a tune — info only):")
        if not orphans:
            print("  (none)")
        for pp, entry in orphans:
            print("  - p{:>3}  id={:<24}  {}".format(pp, str(entry.get("id", "?")), entry.get("image", "?")))

        print("SKIPPED non-tune page: refs (no tune id/title anchor — not a gap):")
        if not skipped:
            print("  (none)")
        for s in skipped:
            print("  - page:{}   snippet: ...{}...".format(s["page"], s["snippet"].strip()))

    print("-" * 70)
    if missing:
        print("RESULT: FAIL — {} tune page reference(s) have no covering image. "
              "Coverage GAP(s) above must be rendered (separate task; needs source "
              "PDFs) or the app reference corrected.".format(len(missing)))
        return 1
    print("RESULT: PASS — all {} tune page reference(s) are covered by an existing "
          "Real Book page-image.".format(len(tune_refs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
