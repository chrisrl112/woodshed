#!/usr/bin/env python3
"""
render_snapshot.py — wood-43 / milestone M3 (public read-only data snapshot)

Serializes Chris's running practice state (the in-app object S, promoted to disk
as mission-control.json) into a PUBLIC, READ-ONLY snapshot that the live public
Woodshed site loads to show his real progress (streak / week / tunes / PRs /
objectives) with NOTHING private leaked. This is the data sibling of the
page-image bundle (render_pages.py): one generator, one schema/contract
(snapshot.schema.json), one example output, all stdlib-only and reproducible.

PRIVACY POLICY (the whole point)
    The public projection includes ONLY shareable progress: streak, week
    number + focus theme, per-tune rung COUNT + memorized/verified booleans,
    PR bests/goals, and weekly-objective progress. It DELIBERATELY DROPS every
    private field: raw rung DATES, exact verified dates, pin state, spaced-
    review internals, monthly steering notes, the localStorage key, and any
    journal / lore / notes / log free-text / feedback / device id / file path.
    What's omitted (and why) is documented in snapshot.schema.json $omitted and
    enforced by construction here: we read named public fields only, never the
    whole object, so a new private upstream field cannot silently flow through.

INPUT (production vs. on-disk-today)
    In production the app's Export-Sync card POSTs the running state to
    woodshed_server.py (/save-brain -> mission-control.json). So the live INPUT
    is mission-control.json. When that file is ABSENT (the normal case on disk
    today — the live numbers live only in the browser, localStorage
    'woodshed_v1'), we fall back to mission-control.example.json so the pipeline
    is always runnable. The example is ILLUSTRATIVE shape, not live data, and we
    carry its label forward.

OUTPUT
    public-assets/snapshot.json        — the live artifact the site loads.
    public-assets/snapshot.example.json — written ONLY when run off the example
                                          input, so there is a committed,
                                          clearly-illustrative reference output.

VALIDATION
    The script validates its own output against snapshot.schema.json with a
    minimal, hand-rolled stdlib check (required keys + basic types) — same
    no-pip philosophy as the repo's other scripts. No jsonschema dependency.

Regenerate (idempotent / reproducible):
    cd "Projects/Trumpet"
    python3 public-assets/render_snapshot.py

stdlib only (json, os, sys, argparse).
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # Projects/Trumpet

LIVE_INPUT = os.path.join(ROOT, "mission-control.json")
EXAMPLE_INPUT = os.path.join(ROOT, "mission-control.example.json")
SCHEMA_PATH = os.path.join(HERE, "snapshot.schema.json")
OUT_LIVE = os.path.join(HERE, "snapshot.json")
OUT_EXAMPLE = os.path.join(HERE, "snapshot.example.json")

SCHEMA_VERSION = "1.0"

# Illustrative banner carried onto example output (so it can never be mistaken
# for live data). The real-vs-illustrative status is ALSO machine-readable under
# source.illustrative; this string is the human banner.
ILLUSTRATIVE_BANNER = (
    "ILLUSTRATIVE EXAMPLE — NOT CHRIS'S LIVE DATA. This public snapshot was "
    "projected from mission-control.example.json (representative shape only; "
    "live numbers live in the browser localStorage 'woodshed_v1' and are not "
    "on disk). Every figure here traces to the example input; nothing private "
    "is included. Regenerate with public-assets/render_snapshot.py."
)


# --------------------------------------------------------------------------
# Projection — read NAMED public fields only (never the whole object).
# --------------------------------------------------------------------------

def project(state, input_name, generated_at_iso):
    """Project a mission-control state object to the public snapshot shape.

    Reads only the explicit public fields; private fields are never touched, so
    they cannot leak even if upstream adds new ones.
    """
    illustrative = (input_name == "mission-control.example.json")

    snap = {}

    # Banner only when illustrative, so the live snapshot stays clean.
    if illustrative:
        snap["__comment__"] = ILLUSTRATIVE_BANNER

    snap["schemaVersion"] = SCHEMA_VERSION
    snap["generatedAt"] = generated_at_iso
    snap["source"] = {
        "input": input_name,
        "exportedAt": state.get("generatedAt"),
        "illustrative": illustrative,
    }

    # streak / lastDay — simple non-identifying scalars.
    snap["streak"] = int(state.get("streak", 0))
    snap["lastDay"] = state.get("lastDay")  # date or null

    # week — number + focus theme only (no per-block plan text).
    wk = state.get("week", {}) or {}
    idx = int(wk.get("index", 0))
    snap["week"] = {
        "index": idx,
        "displayNumber": int(wk.get("displayNumber", idx + 1)),
        "focus": wk.get("focus"),
    }

    # primaryTune / rotation — ids only.
    primary = state.get("primaryTune")
    snap["primaryTune"] = primary
    snap["rotation"] = list(state.get("rotation", []) or [])

    # tunes — per-tune PUBLIC progress; rung DATES + exact verified DATE dropped.
    pub_tunes = {}
    for tid, t in (state.get("tunes", {}) or {}).items():
        if not isinstance(t, dict):
            continue
        verified = bool(t.get("verifiedDate"))  # boolean-ize; drop the date
        entry = {
            "title": t.get("title", tid),
            "rungStatus": int(t.get("rungStatus", 0)),
            "memorized": bool(t.get("memorized", False)),
            "verified": verified,
        }
        if primary is not None and tid == primary:
            entry["isPrimary"] = True
        pub_tunes[tid] = entry
    snap["tunes"] = pub_tunes

    # weeklyObjectives — progress summary; labels are curriculum text, not notes.
    objectives = []
    met_count = 0
    for o in (state.get("weeklyObjectives", []) or []):
        if not isinstance(o, dict):
            continue
        current = o.get("current", 0)
        target = o.get("target", 0)
        met = o.get("met")
        if met is None:
            try:
                met = current >= target
            except TypeError:
                met = False
        met = bool(met)
        if met:
            met_count += 1
        objectives.append({
            "label": o.get("label", ""),
            "current": current,
            "target": target,
            "met": met,
        })
    snap["weeklyObjectives"] = objectives
    snap["weeklyObjectivesSummary"] = {"met": met_count, "total": len(objectives)}

    # prTargets — numeric bests/goals + last-logged date + derived pctToGoal.
    pr_out = {}
    for pid, pr in (state.get("prTargets", {}) or {}).items():
        if not isinstance(pr, dict):
            continue
        best = int(pr.get("best", 0))
        goal = pr.get("goal")
        pct = None
        if isinstance(goal, (int, float)) and goal:
            pct = min(100, round(100 * best / goal))
        pr_out[pid] = {
            "best": best,
            "goal": int(goal) if isinstance(goal, (int, float)) else goal,
            "lastLogged": pr.get("lastLogged"),
            "pctToGoal": pct,
        }
    snap["prTargets"] = pr_out

    return snap


# --------------------------------------------------------------------------
# Minimal stdlib validation against snapshot.schema.json (no jsonschema dep).
# Checks: required top-level keys present, a few core types, per-tune required
# keys, and that the projection has not leaked any forbidden private key.
# --------------------------------------------------------------------------

FORBIDDEN_KEYS = {
    "rungDates", "verifiedDate", "rungDates", "pinned", "pin", "pinnedTune",
    "reviewTunes", "reviewSchedule", "monthlyObjectives", "appStateKey",
    "journal", "lore", "notes", "feedback", "deviceId", "path",
}


def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def validate(snap, schema):
    """Return list[str] of violations ([] == valid)."""
    v = []

    required = schema.get("required", [])
    for key in required:
        if key not in snap:
            v.append(f"missing required top-level key: {key!r}")

    # Core type spot-checks.
    if not isinstance(snap.get("streak"), int):
        v.append("streak must be an integer")
    if not isinstance(snap.get("rotation"), list):
        v.append("rotation must be an array")
    if not isinstance(snap.get("tunes"), dict):
        v.append("tunes must be an object")
    if not isinstance(snap.get("prTargets"), dict):
        v.append("prTargets must be an object")
    if not isinstance(snap.get("week"), dict):
        v.append("week must be an object")
    else:
        for k in ("index", "displayNumber"):
            if k not in snap["week"]:
                v.append(f"week missing required key: {k!r}")

    src = snap.get("source")
    if not isinstance(src, dict):
        v.append("source must be an object")
    else:
        if src.get("input") not in ("mission-control.json",
                                    "mission-control.example.json"):
            v.append(f"source.input invalid: {src.get('input')!r}")
        if not isinstance(src.get("illustrative"), bool):
            v.append("source.illustrative must be a boolean")

    # Per-tune required keys + forbidden-key sweep.
    tune_req = ["title", "rungStatus", "memorized", "verified"]
    for tid, t in (snap.get("tunes") or {}).items():
        if not isinstance(t, dict):
            v.append(f"tunes[{tid!r}] must be an object")
            continue
        for k in tune_req:
            if k not in t:
                v.append(f"tunes[{tid!r}] missing required key: {k!r}")
        for k in t:
            if k in FORBIDDEN_KEYS:
                v.append(f"tunes[{tid!r}] leaked forbidden private key: {k!r}")

    # Top-level forbidden-key sweep (defense in depth).
    for k in snap:
        if k in FORBIDDEN_KEYS:
            v.append(f"snapshot leaked forbidden private key: {k!r}")

    return v


# --------------------------------------------------------------------------

def choose_input():
    """Return (path, name). Prefer the live export; fall back to the example."""
    if os.path.isfile(LIVE_INPUT):
        return LIVE_INPUT, "mission-control.json"
    return EXAMPLE_INPUT, "mission-control.example.json"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Project the Woodshed practice brain (mission-control.json, or the "
            "illustrative example fallback) into the PUBLIC read-only snapshot "
            "the live site loads. Stdlib only; reproducible; idempotent."
        ),
    )
    parser.add_argument(
        "--generated-at",
        default=None,
        help=("Override the generatedAt timestamp (ISO-8601). When omitted and "
              "running off the example, a FIXED timestamp tied to the example's "
              "own generatedAt is used so example output is deterministic."),
    )
    args = parser.parse_args(argv)

    in_path, in_name = choose_input()
    print("Woodshed public snapshot generator (wood-43, M3)")
    print("-" * 70)
    if not os.path.isfile(in_path):
        print(f"FAIL: input not found: {in_path}")
        return 1
    print(f"Input : {os.path.relpath(in_path, ROOT)}  "
          f"({'LIVE export' if in_name == 'mission-control.json' else 'illustrative fallback'})")

    with open(in_path) as f:
        state = json.load(f)

    # Deterministic generatedAt: reproducible/idempotent output. For the example
    # input we anchor to the example's own generatedAt so re-runs are byte-stable
    # and never invent a fresh wall-clock value. For a live export, default to the
    # upstream export timestamp; allow --generated-at to override either.
    if args.generated_at:
        generated_at = args.generated_at
    else:
        generated_at = state.get("generatedAt")
        if not generated_at:
            # Flagged inline rather than backfilling a fabricated default.
            generated_at = "[confirm: input had no generatedAt timestamp]"

    snap = project(state, in_name, generated_at)

    # Validate before writing.
    schema = load_schema()
    violations = validate(snap, schema)
    if violations:
        print("[FAIL] snapshot did not validate against snapshot.schema.json:")
        for vmsg in violations:
            print(f"        - {vmsg}")
        return 1
    print(f"[PASS] snapshot validates ({len(snap)} top-level keys, "
          f"{len(snap['tunes'])} tunes, {len(snap['prTargets'])} PR targets)")

    text = json.dumps(snap, indent=2) + "\n"

    # Always write the live artifact the site loads.
    with open(OUT_LIVE, "w") as f:
        f.write(text)
    print(f"Wrote {os.path.relpath(OUT_LIVE, ROOT)}")

    # When projecting the example, also write the committed example reference.
    if in_name == "mission-control.example.json":
        with open(OUT_EXAMPLE, "w") as f:
            f.write(text)
        print(f"Wrote {os.path.relpath(OUT_EXAMPLE, ROOT)} (illustrative reference)")

    print("-" * 70)
    print("RESULT: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
