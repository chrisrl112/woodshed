#!/usr/bin/env python3
"""
verify_public_safe.py — wood-28 (static / build-time half) — public-bundle guardrail

WHAT THIS ENFORCES
    A build/CI-style gate over the `public-assets/` bundle. Run it against the
    bundle before shipping; it ASSERTS the bundle is safe to publish and exits
    non-zero (with a clear report) if any check fails.

WHY (Chris's content policy, locked 6/18 — milestone M0)
    The public Woodshed POC may show the EXACT method-book / Real-Book pages
    used in exercises, rendered as page IMAGES — but the FULL source book must
    NEVER be downloadable or available. wood-44 pre-rendered exactly the pages
    the app embeds into `pages/` and recorded them in `page-manifest.json` (the
    public-build contract). This script makes that policy mechanically
    enforceable so a stray PDF, an un-manifested page, an oversized scan, or a
    non-image file can't silently leak into a public deploy.

SCOPE — what is and is NOT covered here
    COVERED (this file): the STATIC, build-time half of wood-28. It inspects the
    files in the public bundle and refuses to pass if they violate the policy.
    NOT COVERED (separate task): the RUNTIME, serve-time block — making the live
    app refuse to serve source PDFs at request time. That is wood-42 (EPHEMERAL
    mode), which is BLOCKED on wood-32. Passing this script does NOT imply the
    runtime gate exists; it only certifies the shipped bundle's contents.

CHECKS (see the four CHECK functions below)
    1. No source PDFs / book files anywhere in the bundle (*.pdf/.mxl/.musicxml).
    2. Manifest integrity — every image referenced exists, and every image file
       in pages/ is accounted for in the manifest (no stray/un-manifested page).
    3. No oversized asset (a full book scan would blow MAX_ASSET_BYTES; a single
       page won't).
    4. Files under pages/ must be in the raster-image whitelist.

USAGE
    python3 verify_public_safe.py [PUBLIC_ASSETS_DIR]
    # default PUBLIC_ASSETS_DIR = the directory this script lives in
    # exit 0 = safe to ship, exit 1 = violations (each listed)

stdlib only (os, sys, json, pathlib, argparse) — no pip installs.
"""

import argparse
import json
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Tunable constants (kept at top so they are easy to find / edit).
# --------------------------------------------------------------------------

# Max size for any single file in the bundle. wood-44's README states the
# bundle honors a "no >5 MB file" rule; a single ~150 DPI page PNG is well
# under this, while a full book scan/PDF would exceed it. (Chosen per that
# documented rule; edit here if the page DPI/ceiling policy changes.)
MAX_ASSET_BYTES = 5 * 1024 * 1024  # 5 MB

# Source-book / full-document formats that must NEVER appear in the public
# bundle (the whole point of the policy). Extensions are matched case-insensitively.
FORBIDDEN_SOURCE_EXTS = {".pdf", ".mxl", ".musicxml", ".xml"}

# Raster-image formats permitted under pages/. Anything else under pages/ is a
# violation (a non-image file there is suspicious / unauthorized content).
ALLOWED_PAGE_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

# The public-build contract file (lives at the bundle root).
MANIFEST_NAME = "page-manifest.json"
PAGES_DIRNAME = "pages"


# --------------------------------------------------------------------------
# Checks. Each returns a list[str] of violation messages ([] == pass).
# --------------------------------------------------------------------------

def check_no_source_books(bundle: Path) -> list:
    """CHECK 1 — no source PDFs / full-book files anywhere under the bundle."""
    violations = []
    for p in sorted(bundle.rglob("*")):
        if p.is_file() and p.suffix.lower() in FORBIDDEN_SOURCE_EXTS:
            violations.append(
                f"forbidden source-book file in bundle: {p.relative_to(bundle)} "
                f"(extension {p.suffix.lower()} is never shippable)"
            )
    return violations


def check_manifest_integrity(bundle: Path) -> list:
    """CHECK 2 — manifest <-> pages/ are an exact, two-way match.

    Every image referenced by the manifest must exist on disk, AND every image
    file present in pages/ must be referenced by the manifest (no stray /
    un-manifested page — an un-manifested page is a potential unauthorized book
    page leaking into the public build).
    """
    violations = []
    manifest_path = bundle / MANIFEST_NAME
    pages_dir = bundle / PAGES_DIRNAME

    if not manifest_path.is_file():
        return [f"manifest not found: {MANIFEST_NAME} (cannot verify bundle)"]

    try:
        entries = json.loads(manifest_path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        return [f"manifest unreadable / invalid JSON: {MANIFEST_NAME} ({e})"]

    if not isinstance(entries, list):
        return [f"manifest must be a JSON array of entries: {MANIFEST_NAME}"]

    # Collect referenced images (relative to bundle root, as stored in manifest).
    referenced = set()
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict) or "image" not in entry:
            violations.append(f"manifest entry #{i} has no 'image' field")
            continue
        img_rel = entry["image"]
        referenced.add(img_rel)
        if not (bundle / img_rel).is_file():
            violations.append(
                f"manifest references missing image: {img_rel} "
                f"(entry id={entry.get('id', '?')!r})"
            )

    # Collect actual image files on disk under pages/.
    on_disk = set()
    if pages_dir.is_dir():
        for p in sorted(pages_dir.rglob("*")):
            if p.is_file():
                on_disk.add(p.relative_to(bundle).as_posix())
    else:
        violations.append(f"pages directory not found: {PAGES_DIRNAME}/")

    # Any file in pages/ not referenced by the manifest = stray / un-manifested.
    for rel in sorted(on_disk - referenced):
        violations.append(
            f"stray un-manifested page in {PAGES_DIRNAME}/: {rel} "
            f"(not in {MANIFEST_NAME} — possible unauthorized page leak)"
        )

    return violations


def check_no_oversized_assets(bundle: Path) -> list:
    """CHECK 3 — no single file exceeds MAX_ASSET_BYTES."""
    violations = []
    for p in sorted(bundle.rglob("*")):
        if p.is_file():
            size = p.stat().st_size
            if size > MAX_ASSET_BYTES:
                violations.append(
                    f"oversized asset: {p.relative_to(bundle)} "
                    f"({size:,} bytes > MAX_ASSET_BYTES {MAX_ASSET_BYTES:,})"
                )
    return violations


def check_pages_image_whitelist(bundle: Path) -> list:
    """CHECK 4 — every file under pages/ is an allowed raster image."""
    violations = []
    pages_dir = bundle / PAGES_DIRNAME
    if not pages_dir.is_dir():
        return []  # absence is reported by CHECK 2
    for p in sorted(pages_dir.rglob("*")):
        if p.is_file() and p.suffix.lower() not in ALLOWED_PAGE_IMAGE_EXTS:
            violations.append(
                f"non-image file under {PAGES_DIRNAME}/: {p.relative_to(bundle)} "
                f"(allowed: {', '.join(sorted(ALLOWED_PAGE_IMAGE_EXTS))})"
            )
    return violations


CHECKS = [
    ("No source PDFs / book files in bundle", check_no_source_books),
    ("Manifest <-> pages/ integrity",         check_manifest_integrity),
    ("No oversized assets (<= MAX_ASSET_BYTES)", check_no_oversized_assets),
    ("pages/ image-format whitelist",         check_pages_image_whitelist),
]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build-time guardrail: assert the public-assets bundle is safe to "
            "ship under Chris's content policy (exact pages as images OK; full "
            "source books NEVER shippable). Exit 0 = safe, 1 = violations."
        ),
        epilog=(
            "Note: the RUNTIME serve-time block (refusing to serve source PDFs "
            "at request time) is a separate task, wood-42 (EPHEMERAL mode, "
            "blocked on wood-32), and is NOT covered by this script."
        ),
    )
    parser.add_argument(
        "public_assets_dir",
        nargs="?",
        default=str(Path(__file__).resolve().parent),
        help="Path to the public-assets directory (default: this script's dir).",
    )
    args = parser.parse_args(argv)

    bundle = Path(args.public_assets_dir).resolve()
    print(f"Woodshed public-bundle guardrail (wood-28, static half)")
    print(f"Bundle: {bundle}")
    print(f"MAX_ASSET_BYTES = {MAX_ASSET_BYTES:,}")
    print("-" * 70)

    if not bundle.is_dir():
        print(f"FAIL: not a directory: {bundle}")
        return 1

    all_violations = []
    for label, fn in CHECKS:
        violations = fn(bundle)
        status = "PASS" if not violations else f"FAIL ({len(violations)})"
        print(f"[{status}] {label}")
        for v in violations:
            print(f"        - {v}")
        all_violations.extend(violations)

    print("-" * 70)
    if all_violations:
        print(f"RESULT: FAIL — {len(all_violations)} violation(s). "
              f"Bundle is NOT safe to ship.")
        return 1
    print("RESULT: PASS — bundle is safe to ship.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
