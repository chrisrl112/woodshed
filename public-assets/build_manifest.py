#!/usr/bin/env python3
"""
build_manifest.py — wood-48 / milestone M4 (published hub-ingestion contract)

Validates the Woodshed spoke's PUBLISHED project manifest (manifest.json) — the
entry point the Compound Interests hub ingests. It is the publish (spoke) side of
the hub-and-spoke contract (manifest + heartbeat + changelog). This is a checker,
not a generator: it READS and VALIDATES only, writes nothing, and exits non-zero
on any violation, so a bad manifest never ships.

WHAT IT CHECKS
  1. manifest.json parses as JSON and validates against the hub's Manifest
     schema v1 (Portfolio Hub/build-prep/schemas/manifest.schema.json):
       - required top-level keys present
       - additionalProperties:false (no unknown top-level keys)
       - core types, the schema's enums (status / loop automation / demo type /
         patterns), and the schema's key patterns (slug, started, links.page)
     This is a minimal, hand-rolled stdlib check — NO jsonschema pip dependency,
     same no-pip philosophy as render_snapshot.py / verify_public_safe.py.
  2. The published manifest stays IN SYNC with the hub-side canonical manifest
     (Portfolio Hub/build-prep/projects/the-woodshed/manifest.json) on every
     shared field — the two must not drift.
  3. The data artifacts the hub fetches alongside the manifest (snapshot.json,
     page-manifest.json) EXIST on disk.

Run (idempotent / read-only):
    cd "Projects/Trumpet/public-assets"
    python3 build_manifest.py

stdlib only (json, os, re, sys).
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))           # .../public-assets
TRUMPET = os.path.dirname(HERE)                              # .../Projects/Trumpet
PROJECTS = os.path.dirname(TRUMPET)                          # .../Projects

MANIFEST_PATH = os.path.join(HERE, "manifest.json")
SNAPSHOT_PATH = os.path.join(HERE, "snapshot.json")
PAGE_MANIFEST_PATH = os.path.join(HERE, "page-manifest.json")

# Hub-side canonical sources (read-only references).
HUB_SCHEMA_PATH = os.path.join(
    PROJECTS, "Portfolio Hub", "build-prep", "schemas", "manifest.schema.json"
)
HUB_CANONICAL_PATH = os.path.join(
    PROJECTS, "Portfolio Hub", "build-prep", "projects", "the-woodshed", "manifest.json"
)

# ---- Hub schema v1 facts (mirrored from manifest.schema.json so the check is
#      self-contained; the schema file is also loaded below to cross-check the
#      required-key list, so a drift in the real schema is caught too). ----
REQUIRED_KEYS = [
    "schema_version", "slug", "name", "tagline", "status", "maturity",
    "started", "visibility", "stack", "ai_roles", "loops", "demo", "links",
    "metrics", "patterns",
]
OPTIONAL_KEYS = ["accent", "accent_hex"]
ALLOWED_TOP_KEYS = set(REQUIRED_KEYS) | set(OPTIONAL_KEYS)

STATUS_ENUM = {"live", "beta", "concept", "dormant", "retired"}
AUTOMATION_ENUM = {"full", "human-approve", "manual"}
DEMO_TYPE_ENUM = {"embed", "launch", "video", "watch-only"}
PATTERN_ENUM = {
    "adversarial-review", "committee-synthesis", "researcher-critic-editor",
    "daily-loop", "heartbeat-monitoring", "staleness-honesty",
    "human-approve-gate", "manifest-driven-content", "curator-agent",
}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
STARTED_RE = re.compile(r"^[0-9]{4}-(0[1-9]|1[0-2])$")
PAGE_RE = re.compile(r"^/projects/[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")

# Fields compared for hub-side / spoke sync (every shared top-level key).
SYNC_KEYS = REQUIRED_KEYS + OPTIONAL_KEYS


def fail(errors):
    print("FAIL — build_manifest.py found {} problem(s):".format(len(errors)))
    for e in errors:
        print("  - {}".format(e))
    sys.exit(1)


def load_json(path, errors, label):
    if not os.path.exists(path):
        errors.append("{}: file not found at {}".format(label, path))
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        errors.append("{}: invalid JSON — {}".format(label, exc))
        return None


def is_nonempty_str(v):
    return isinstance(v, str) and len(v) >= 1


# bool is a subclass of int in Python; reject it where a real int is required.
def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def validate_schema(m, errors):
    """Minimal stdlib validation of manifest m against hub schema v1."""
    if not isinstance(m, dict):
        errors.append("schema: top-level value must be an object")
        return

    # additionalProperties:false + required keys
    for k in m.keys():
        if k not in ALLOWED_TOP_KEYS:
            errors.append("schema: unknown top-level key '{}' (additionalProperties:false)".format(k))
    for k in REQUIRED_KEYS:
        if k not in m:
            errors.append("schema: missing required key '{}'".format(k))

    # schema_version
    if m.get("schema_version") != "1.0":
        errors.append("schema: schema_version must be const \"1.0\"")

    # slug
    slug = m.get("slug")
    if not is_nonempty_str(slug) or not SLUG_RE.match(slug or ""):
        errors.append("schema: slug must be a url-safe string")

    # name / tagline
    for k in ("name", "tagline"):
        if not is_nonempty_str(m.get(k)):
            errors.append("schema: {} must be a non-empty string".format(k))

    # status
    if m.get("status") not in STATUS_ENUM:
        errors.append("schema: status must be one of {}".format(sorted(STATUS_ENUM)))

    # maturity 1..5 integer
    mat = m.get("maturity")
    if not is_int(mat) or not (1 <= mat <= 5):
        errors.append("schema: maturity must be an integer 1-5")

    # started YYYY-MM
    started = m.get("started")
    if not isinstance(started, str) or not STARTED_RE.match(started or ""):
        errors.append("schema: started must match YYYY-MM")

    # accent_hex (optional)
    if "accent_hex" in m and not (isinstance(m["accent_hex"], str) and HEX_RE.match(m["accent_hex"])):
        errors.append("schema: accent_hex must be a #RRGGBB hex string")
    if "accent" in m and not isinstance(m["accent"], str):
        errors.append("schema: accent must be a string")

    # visibility { public: bool }
    vis = m.get("visibility")
    if not isinstance(vis, dict) or "public" not in vis or not isinstance(vis.get("public"), bool):
        errors.append("schema: visibility must be an object with boolean 'public'")
    elif set(vis.keys()) - {"public"}:
        errors.append("schema: visibility has unknown keys (additionalProperties:false)")

    # stack / ai_roles: non-empty arrays of non-empty strings
    for k in ("stack", "ai_roles"):
        arr = m.get(k)
        if not isinstance(arr, list) or len(arr) < 1 or not all(is_nonempty_str(x) for x in arr):
            errors.append("schema: {} must be a non-empty array of non-empty strings".format(k))

    # loops
    loops = m.get("loops")
    if not isinstance(loops, list) or len(loops) < 1:
        errors.append("schema: loops must be a non-empty array")
    else:
        for i, lp in enumerate(loops):
            if not isinstance(lp, dict):
                errors.append("schema: loops[{}] must be an object".format(i))
                continue
            for rk in ("cadence", "name", "automation"):
                if rk not in lp:
                    errors.append("schema: loops[{}] missing '{}'".format(i, rk))
            if not is_nonempty_str(lp.get("cadence")):
                errors.append("schema: loops[{}].cadence must be a non-empty string".format(i))
            if not is_nonempty_str(lp.get("name")):
                errors.append("schema: loops[{}].name must be a non-empty string".format(i))
            if lp.get("automation") not in AUTOMATION_ENUM:
                errors.append("schema: loops[{}].automation must be one of {}".format(i, sorted(AUTOMATION_ENUM)))
            if "note" in lp and not isinstance(lp["note"], str):
                errors.append("schema: loops[{}].note must be a string".format(i))
            unknown = set(lp.keys()) - {"cadence", "name", "automation", "note"}
            if unknown:
                errors.append("schema: loops[{}] has unknown keys {} (additionalProperties:false)".format(i, sorted(unknown)))

    # demo { type [, url, fallback, note] }; fallback REQUIRED when type==embed
    demo = m.get("demo")
    if not isinstance(demo, dict) or "type" not in demo:
        errors.append("schema: demo must be an object with 'type'")
    else:
        if demo.get("type") not in DEMO_TYPE_ENUM:
            errors.append("schema: demo.type must be one of {}".format(sorted(DEMO_TYPE_ENUM)))
        if demo.get("type") == "embed" and "fallback" not in demo:
            errors.append("schema: demo.fallback is REQUIRED when demo.type == 'embed'")
        unknown = set(demo.keys()) - {"type", "url", "fallback", "note"}
        if unknown:
            errors.append("schema: demo has unknown keys {} (additionalProperties:false)".format(sorted(unknown)))

    # links { page [, live, repo] }
    links = m.get("links")
    if not isinstance(links, dict) or "page" not in links:
        errors.append("schema: links must be an object with 'page'")
    else:
        page = links.get("page")
        if not isinstance(page, str) or not PAGE_RE.match(page or ""):
            errors.append("schema: links.page must match /projects/<slug>")
        elif isinstance(slug, str) and page != "/projects/{}".format(slug):
            errors.append("schema: links.page must equal /projects/{slug} (slug/page mismatch)")
        unknown = set(links.keys()) - {"page", "live", "repo"}
        if unknown:
            errors.append("schema: links has unknown keys {} (additionalProperties:false)".format(sorted(unknown)))

    # metrics: array of {label, source, key}
    metrics = m.get("metrics")
    if not isinstance(metrics, list):
        errors.append("schema: metrics must be an array")
    else:
        for i, mt in enumerate(metrics):
            if not isinstance(mt, dict):
                errors.append("schema: metrics[{}] must be an object".format(i))
                continue
            for rk in ("label", "source", "key"):
                if not is_nonempty_str(mt.get(rk)):
                    errors.append("schema: metrics[{}].{} must be a non-empty string".format(i, rk))
            unknown = set(mt.keys()) - {"label", "source", "key"}
            if unknown:
                errors.append("schema: metrics[{}] has unknown keys {} (additionalProperties:false)".format(i, sorted(unknown)))

    # patterns: array of enum strings
    patterns = m.get("patterns")
    if not isinstance(patterns, list):
        errors.append("schema: patterns must be an array")
    else:
        for i, p in enumerate(patterns):
            if p not in PATTERN_ENUM:
                errors.append("schema: patterns[{}] '{}' not in the pattern vocabulary".format(i, p))


def cross_check_required_keys(errors):
    """Cross-check our REQUIRED_KEYS against the real hub schema file, so a drift
    in the published schema's required list is caught rather than silently
    diverging from this checker."""
    schema = load_json(HUB_SCHEMA_PATH, errors, "hub schema")
    if schema is None:
        return
    real_required = schema.get("required")
    if real_required is None:
        errors.append("hub schema: no 'required' list found")
        return
    if set(real_required) != set(REQUIRED_KEYS):
        errors.append(
            "hub schema drift: schema.required {} != checker REQUIRED_KEYS {}".format(
                sorted(real_required), sorted(REQUIRED_KEYS)
            )
        )


def check_sync(published, errors):
    """Assert the published manifest matches the hub-side canonical manifest on
    every shared field."""
    canonical = load_json(HUB_CANONICAL_PATH, errors, "hub canonical manifest")
    if canonical is None:
        return
    for k in SYNC_KEYS:
        in_pub = k in published
        in_can = k in canonical
        if in_pub != in_can:
            errors.append(
                "sync: key '{}' present in {} but not the other (published={}, canonical={})".format(
                    k, "published" if in_pub else "canonical", in_pub, in_can
                )
            )
            continue
        if in_pub and published.get(k) != canonical.get(k):
            errors.append(
                "sync: field '{}' differs from hub canonical manifest".format(k)
            )
    # Also catch any top-level key the canonical has that we don't compare.
    extra = (set(published.keys()) | set(canonical.keys())) - set(SYNC_KEYS)
    if extra:
        errors.append("sync: unexpected top-level key(s) outside the sync set: {}".format(sorted(extra)))


def check_artifacts(errors):
    """Verify the data artifacts the hub fetches alongside the manifest exist."""
    for label, path in (("snapshot.json", SNAPSHOT_PATH),
                        ("page-manifest.json", PAGE_MANIFEST_PATH)):
        if not os.path.exists(path):
            errors.append("artifact: required data artifact '{}' not found at {}".format(label, path))


def main():
    errors = []

    manifest = load_json(MANIFEST_PATH, errors, "manifest.json")
    if manifest is not None:
        validate_schema(manifest, errors)
        check_sync(manifest, errors)
    cross_check_required_keys(errors)
    check_artifacts(errors)

    if errors:
        fail(errors)

    print("PASS — manifest.json is schema-valid (hub v1), in sync with the hub")
    print("       canonical manifest, and its data artifacts (snapshot.json,")
    print("       page-manifest.json) exist on disk.")
    sys.exit(0)


if __name__ == "__main__":
    main()
