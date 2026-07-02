#!/usr/bin/env python3
"""
Woodshed Heartbeat Emitter — The Woodshed -> Compound Interests hub (wood-47)
----------------------------------------------------------------------------
Push-only. Reads the PUBLIC snapshot the proven pipeline already writes
(public-assets/snapshot.json, produced by render_snapshot.py / wood-43) and
upserts ONE heartbeat row to Supabase so the Woodshed card on chrisliquin.com
flips from "awaiting first report" to a live reporting dot with real values.
Does NOT re-run the practice brain, re-export, or touch any existing file.

Honest-by-construction: last_report = the snapshot's OWN export timestamp
(source.exportedAt, falling back to generatedAt) — NEVER now(). So if Chris
stops practicing/exporting, the snapshot timestamp freezes, last_report
freezes, and the hub degrades the card to stale on its own. The emitter can
never make a dead project look alive.

This is the "heartbeat" leg of the hub's manifest+heartbeat+changelog
ingestion contract; the manifest (wood-48) and snapshot (wood-43) already
shipped. It targets the push contract in
build-prep/SUPABASE-HEARTBEATS-SPEC.md §4.

USAGE
  python3 woodshed_heartbeat.py --once   # build + print payload, attempt POST (default)
  python3 woodshed_heartbeat.py          # same as --once; run on a launchd cadence
  With NO creds present (the normal state during prep): prints the payload and
  SKIPS the POST, exit 0. Nothing external happens without creds.

CONFIG (heartbeat.config.local.json — git-ignored, NEVER committed):
  {
    "supabase_url": "https://<project-ref>.supabase.co",
    "supabase_service_role_key": "<service_role JWT — bypasses RLS, host-only>"
  }
The service_role key bypasses RLS and lives ONLY in Chris's runtime. The public
site only ever uses the read-only anon key. See the spec §6 (OPSEC).

The three manifest-declared heartbeat metric keys are EXACTLY:
  streak_days, sessions_total, hours_total

  - streak_days   <- snapshot.streak (cast int). REAL. Always emitted.
  - sessions_total <- [confirm: sessions_total] NO real source field exists in
                      snapshot.json or the upstream brain on disk yet -> OMITTED
                      from metric_values. The site renders an honest em-dash for
                      an undeclared value; we never fabricate one.
  - hours_total    <- [confirm: hours_total] same — no real source field exists
                      yet -> OMITTED. Add session/hours tracking to the brain
                      export + snapshot, OR drop these two keys from the
                      manifest. See the spec's headline open item.

stdlib only (json, os, sys, datetime, urllib) — matching render_snapshot.py /
verify_public_safe.py's zero-dependency, no-pip posture.
"""
import datetime as dt
import json
import os
import sys
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
SNAPSHOT = os.path.join(HERE, "snapshot.json")
LOCAL = os.path.join(HERE, "heartbeat.config.local.json")
SLUG = "the-woodshed"


def log(*a):
    print("[woodshed-heartbeat]", *a, file=sys.stderr)


def load_json(path):
    with open(path) as f:
        return json.load(f)


def load_snapshot():
    """Load the public snapshot the site already loads. Raises on missing /
    unparseable so main() can fail soft (skip POST) — never fabricate freshness."""
    return load_json(SNAPSHOT)


def to_utc_iso(s):
    """Normalize an ISO-8601 timestamp string to UTC ISO-8601 with a trailing 'Z'.

    The snapshot's timestamps (source.exportedAt / generatedAt) are produced by
    render_snapshot.py and are already ISO-8601 Z (e.g. '2026-06-13T08:40:00.000Z').
    We parse and re-emit in canonical second-precision UTC 'Z' form. Returns None
    if the input is falsy or unparseable (caller decides what to do)."""
    if not s:
        return None
    try:
        raw = s.strip()
        # fromisoformat (pre-3.11) doesn't accept a trailing 'Z'; map it to +00:00.
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        d = dt.datetime.fromisoformat(raw)
        if d.tzinfo is None:
            # Naive timestamp: treat as UTC (snapshot timestamps are emitted in UTC Z).
            d = d.replace(tzinfo=dt.timezone.utc)
        return d.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        log("could not parse timestamp", repr(s), "->", e)
        return None


def build_payload(snap):
    """Build the upsert payload from the snapshot. Emits streak_days (real),
    OMITS sessions_total / hours_total (no real source — flagged [confirm:]),
    and uses the snapshot's OWN export time for the timestamps (the honesty
    mechanism), NOT now(). Returns the payload dict."""
    source = snap.get("source") or {}

    # Honesty mechanism: the file's own timestamp, never now().
    # Prefer the brain's real export time; fall back to the snapshot's generatedAt.
    stamp = to_utc_iso(source.get("exportedAt")) or to_utc_iso(snap.get("generatedAt"))

    # streak_days — the one REAL, high-confidence metric. Always emit.
    metric_values = {}
    if "streak" in snap and snap.get("streak") is not None:
        metric_values["streak_days"] = int(snap["streak"])

    # sessions_total / hours_total — NO real source field exists yet, on disk or
    # in the upstream brain. OMIT rather than fabricate. [confirm: sessions_total]
    # [confirm: hours_total]. The site shows an honest em-dash for an undeclared
    # value; the manifest stays the declaration authority.

    # note — keep the public number honest about its provenance. If the snapshot
    # is illustrative (example fallback, not live numbers), say so plainly.
    note = None
    if source.get("illustrative"):
        note = "illustrative snapshot — not live data"

    return {
        "project_slug": SLUG,
        "last_report": stamp,           # file-derived, NOT now() — see module docstring
        "last_activity": stamp,         # same: last real sign-of-life is the last export
        "status": "live",               # informational only; manifest stays badge authority,
                                        # and the hub's staleness guard degrades a stale card
        "metric_values": metric_values, # only streak_days; the two unsourced keys are omitted
        "note": note,
    }


def post(payload, local):
    """Upsert one row to Supabase via the REST endpoint (merge-duplicates on the
    project_slug PK). service_role key in apikey + Authorization. Returns the HTTP
    status code."""
    url = local["supabase_url"].rstrip("/") + "/rest/v1/heartbeats"
    key = local["supabase_service_role_key"]
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "apikey": key,
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        log("POST", r.getcode())
        return r.getcode()


def main(argv=None):
    # --once is the only mode; accept it (and bare invocation) for an explicit CLI.
    argv = sys.argv[1:] if argv is None else argv
    for a in argv:
        if a not in ("--once",):
            log("unknown arg", repr(a), "(only --once is supported); continuing")

    # Honesty corollary: if the snapshot is missing or unparseable, SKIP the POST
    # entirely so the last good timestamp stands and ages into stale on its own.
    if not os.path.exists(SNAPSHOT):
        log("snapshot.json missing -> skip POST (site degrades honestly)")
        return 0
    try:
        snap = load_snapshot()
    except Exception as e:
        log("snapshot.json unparseable -> skip POST:", e)
        return 0  # fail soft, never fabricate

    try:
        payload = build_payload(snap)
    except Exception as e:
        log("could not build payload -> skip POST:", e)
        return 0  # fail soft

    # If we couldn't derive an honest timestamp, do not POST a fabricated freshness.
    if not payload.get("last_report"):
        log("no honest timestamp in snapshot -> skip POST (never stamp now())")
        return 0

    # Always show what we would send.
    print(json.dumps(payload, indent=2))

    # Read creds from the git-ignored local config. Absent -> print + skip (no POST).
    local = {}
    if os.path.exists(LOCAL):
        try:
            local = load_json(LOCAL)
        except Exception as e:
            log("heartbeat.config.local.json unparseable -> skip POST:", e)
            return 0
    if not local.get("supabase_url") or not local.get("supabase_service_role_key"):
        log("supabase creds not set -> skip POST (dry run; nothing external happened)")
        return 0

    try:
        post(payload, local)
    except urllib.error.HTTPError as e:
        log("HTTP", e.code, e.read().decode()[:300])
        return 0  # log, don't crash the launchd job
    except Exception as e:
        log("post failed (network?):", e)
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
