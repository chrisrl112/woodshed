#!/usr/bin/env python3
"""woodshed_feedback_agent.py — the WRITER half of the Woodshed feedback loop (wood-15, M5).

Reads yesterday's practice feedback (feedback.jsonl) plus the read-only mission-control
brain and emits a patch-form `plan-override.json` that steers the upcoming day's plan.

This is the missing middle of the loop. The READER (loadPlanOverride() / applyPlanOverride())
and the capture surface already ship in index.html (wood-9). The output contract is DECIDED in
plan-override.schema.md; this script conforms to it exactly.

Source of truth:
  - FEEDBACK-LOOP-SPEC.md   §2 (feedback schema), §4 (the night-agent algorithm), §5 (confirms)
  - plan-override.schema.md (the patch-form output contract; reader floors every block at 5 min)
  - mission-control.schema.json / .example.json (read-only context; camelCase, ISO dates)

Design constraints honored:
  - stdlib only (no pip).
  - additive: writes ONLY plan-override.json. No network, no scheduling, no edits to any
    existing file. Never throws on bad input — fail-soft, exit 0, no write (mirrors the
    reader's "never break the day" ethos).
  - Uses ONLY levers the reader supports: setMinutes / dropModules / addBlocks / order /
    scaleToMinutes, plus top-level schemaVersion / generatedAt / date / dow / focus / pinnedTune.

CLI:
  --feedback PATH          (default: feedback.jsonl next to this script)
  --mission-control PATH   (default: mission-control.json next to this script; optional)
  --out PATH               (default: plan-override.json next to this script)
  --today YYYY-MM-DD       (default: system local date) — the day being STEERED.
                           The feedback join key is today-1 (the last line whose date==today-1).
  --dry-run                print the override JSON to stdout, write nothing.
"""

import argparse
import datetime as _dt
import json
import os
import sys

SCHEMA_VERSION = "1.0"
MIN_FLOOR = 5                 # mirror the reader's MIN_FLOOR
MODULE_FALLBACK_MIN = 10     # baseline when a module has no observed block minutes (spec §4.2)
DEFAULT_TIME = 60            # curriculum days total ~60 min; timeTomorrow default per spec §2
LOW_ENERGY_TRIM = 45        # energy=="low" total when no explicit timeTomorrow (documented)

# Known module ids, used only to keep ordering sensible. The reader ignores unknown modules
# gracefully, so this is advisory, not a gate.
KNOWN_MODULES = ["gym", "vocab", "tunes", "ears", "today"]


# --------------------------------------------------------------------------- helpers

def _script_dir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return os.getcwd()


def _parse_date(s):
    """Parse YYYY-MM-DD into a date; raise ValueError on bad input."""
    return _dt.datetime.strptime(s, "%Y-%m-%d").date()


def _iso_date(d):
    return d.strftime("%Y-%m-%d")


def _now_iso():
    # ISO-8601 with millisecond precision + Z, matching the reader's generatedAt convention.
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _read_feedback_line(path, target_date_str):
    """Return the LAST valid JSON object in `path` whose 'date' == target_date_str.

    Latest line wins (spec §5). Malformed lines are skipped silently. Missing file
    or no match returns None. Never raises.
    """
    if not path or not os.path.exists(path):
        return None
    found = None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except (ValueError, TypeError):
                    continue  # skip malformed line, keep scanning
                if not isinstance(obj, dict):
                    continue
                if obj.get("date") == target_date_str:
                    found = obj  # keep the LAST match
    except OSError:
        return None
    return found


def _read_mission_control(path):
    """Optional read-only context. Returns dict or None; never raises."""
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            obj = json.load(fh)
        return obj if isinstance(obj, dict) else None
    except (OSError, ValueError, TypeError):
        return None


def _module_baseline(fb, module):
    """Sum the module's observed block minutes from the feedback line (spec §4.2 baseline).

    Falls back to MODULE_FALLBACK_MIN when the module has no logged blocks.
    """
    total = 0
    blocks = fb.get("blocks") or []
    if isinstance(blocks, list):
        for b in blocks:
            if isinstance(b, dict) and b.get("module") == module:
                try:
                    total += int(round(float(b.get("min", 0))))
                except (TypeError, ValueError):
                    continue
    return total if total > 0 else MODULE_FALLBACK_MIN


def _forwardable_note(fb, module):
    """Return the most recent non-empty block note for `module`, else None (spec §4.2)."""
    note = None
    blocks = fb.get("blocks") or []
    if isinstance(blocks, list):
        for b in blocks:
            if isinstance(b, dict) and b.get("module") == module:
                n = b.get("note")
                if isinstance(n, str) and n.strip():
                    note = n.strip()  # last logged note wins
    return note


def _inferred_reactions(fb):
    """Infer per-module easy/hard leaning from blocks (spec §2a fallback).

    Returns {module: 'too_easy' | 'too_hard'} only for modules with a clear signal.
    Explicit moduleReactions always win over this (applied by the caller).
      - every logged block in the module advanced -> too_easy
      - a block logged-but-not-advanced            -> too_hard
    """
    by_mod = {}
    blocks = fb.get("blocks") or []
    if isinstance(blocks, list):
        for b in blocks:
            if not isinstance(b, dict):
                continue
            if not b.get("logged"):
                continue
            m = b.get("module")
            if not m:
                continue
            by_mod.setdefault(m, []).append(bool(b.get("advance")))
    inferred = {}
    for m, advs in by_mod.items():
        if not advs:
            continue
        if all(advs):
            inferred[m] = "too_easy"
        elif any(a is False for a in advs):
            inferred[m] = "too_hard"
    return inferred


def _is_neutral(fb, reactions):
    """True when the feedback carries no steering signal at all (spec: neutral -> NO-OP)."""
    # any non-on_point reaction is a signal
    for v in reactions.values():
        if v in ("too_easy", "too_hard"):
            return False
    if fb.get("dropTomorrow"):
        return False
    if fb.get("moreOfThis"):
        return False
    energy = fb.get("energy")
    if energy in ("low", "high"):
        return False
    tt = fb.get("timeTomorrow")
    if tt is not None and tt != DEFAULT_TIME:
        return False
    if fb.get("shakyTunes"):
        return False
    return True


# --------------------------------------------------------------------------- core

def build_override(fb, mc, today):
    """Build the patch-form override dict from a feedback line. Pure; ground every field in fb.

    `mc` (mission-control) is currently read-only context only — no field is fabricated from
    it. It is accepted for forward compatibility and so the agent can run feedback-only.
    Returns the override dict, or None to signal NO-OP (neutral feedback).
    """
    # 1) Resolve reactions: explicit moduleReactions win; inference fills the gaps (§2a).
    reactions = {}
    inferred = _inferred_reactions(fb)
    reactions.update(inferred)
    explicit = fb.get("moduleReactions")
    if isinstance(explicit, dict):
        for m, r in explicit.items():
            if r in ("too_easy", "on_point", "too_hard"):
                reactions[m] = r  # explicit selector wins

    if _is_neutral(fb, reactions):
        return None  # NO-OP — don't write a no-op override

    drop_tomorrow = [m for m in (fb.get("dropTomorrow") or []) if isinstance(m, str)]
    more_of_this = [m for m in (fb.get("moreOfThis") or []) if isinstance(m, str)]

    set_minutes = {}
    add_blocks = []
    drop_modules = list(dict.fromkeys(drop_tomorrow))  # dedupe, preserve order

    # 2) moreOfThis -> addBlocks a promote block (hard promote, §4.4).
    for m in dict.fromkeys(more_of_this):
        if m in drop_modules:
            continue  # a dropped module cannot also be promoted
        base = _module_baseline(fb, m)
        add_blocks.append({
            "module": m,
            "title": _promote_title(m),
            "min": max(MIN_FLOOR, int(round(base))),
            "why": "More of this (flagged yesterday): second pass to consolidate.",
        })

    # 3) Per-module easy/hard handling for modules NOT dropped.
    repaired_modules = set()  # modules that got an addBlocks repair (skip setMinutes for them)
    for m, r in reactions.items():
        if m in drop_modules:
            continue
        base = _module_baseline(fb, m)
        if r == "too_easy":
            # demote — cut minutes ~30%, floor 5 (§4.1). Skip if also promoted via moreOfThis.
            if m in more_of_this:
                continue
            set_minutes[m] = max(MIN_FLOOR, int(round(base * 0.7)))
        elif r == "too_hard":
            note = _forwardable_note(fb, m)
            if note:
                # repeat/extend + carry the note forward as the block's `why` (§4.2).
                add_blocks.append({
                    "module": m,
                    "title": _repair_title(m),
                    "min": max(MIN_FLOOR, int(round(base * 1.25))),
                    "why": "Carried from yesterday: " + note,
                })
                repaired_modules.add(m)
            else:
                # no note to forward -> extend minutes ~25% (§4.2 fallback).
                set_minutes[m] = max(MIN_FLOOR, int(round(base * 1.25)))

    # 4) energy + timeTomorrow scaling (§4.5, §4.8).
    energy = fb.get("energy")
    time_tomorrow = fb.get("timeTomorrow")
    scale_to_minutes = None
    if isinstance(time_tomorrow, (int, float)) and int(time_tomorrow) != DEFAULT_TIME:
        scale_to_minutes = int(round(time_tomorrow))  # reader does the scaling math (§4.5)
    elif energy == "low":
        scale_to_minutes = LOW_ENERGY_TRIM  # trim when low energy + no explicit time
    # energy=="high" -> no trim (documented).

    # 5) order: too_hard + moreOfThis modules first; energy-low forces gym first (§4, §4.8).
    order = _build_order(fb, reactions, more_of_this, drop_modules, energy)

    # 6) shakyTunes[0] -> pinnedTune pass-through (§4.6). Reader validates against TUNES.
    pinned_tune = None
    shaky = fb.get("shakyTunes")
    if isinstance(shaky, list) and shaky and isinstance(shaky[0], str) and shaky[0].strip():
        pinned_tune = shaky[0].strip()

    # 7) Assemble. Only include levers that actually carry a signal (keep the patch compact).
    override = {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": _now_iso(),
        "date": _iso_date(today),
        "dow": today.weekday(),  # 0=Mon, matches spec convention
    }
    focus = fb.get("focus")
    if isinstance(focus, str) and focus.strip():
        override["focus"] = focus.strip() + " (steered)"
    if set_minutes:
        override["setMinutes"] = set_minutes
    if drop_modules:
        override["dropModules"] = drop_modules
    if add_blocks:
        override["addBlocks"] = add_blocks
    if order:
        override["order"] = order
    if scale_to_minutes is not None:
        override["scaleToMinutes"] = scale_to_minutes
    if pinned_tune is not None:
        override["pinnedTune"] = pinned_tune

    return override


def _promote_title(module):
    titles = {
        "gym": "Gym — extra rep",
        "vocab": "Vocabulary — extra rep",
        "tunes": "Tune — extra pass",
        "ears": "Daily Ears — extra rep",
        "today": "Focus block — extra rep",
    }
    return titles.get(module, module + " — extra rep")


def _repair_title(module):
    titles = {
        "gym": "Gym — repair & extend",
        "vocab": "Vocabulary — repair & extend",
        "tunes": "Tune — repair & extend",
        "ears": "Daily Ears — repair & extend",
        "today": "Focus block — repair & extend",
    }
    return titles.get(module, module + " — repair & extend")


def _build_order(fb, reactions, more_of_this, drop_modules, energy):
    """Rank too_hard + moreOfThis modules first, others after; energy-low forces gym first.

    Returns a list of module ids, or [] if there is nothing meaningful to reorder.
    """
    present = []
    blocks = fb.get("blocks") or []
    if isinstance(blocks, list):
        for b in blocks:
            if isinstance(b, dict):
                m = b.get("module")
                if isinstance(m, str) and m not in present:
                    present.append(m)
    # include modules referenced only by reactions / moreOfThis
    for m in list(reactions.keys()) + list(more_of_this):
        if isinstance(m, str) and m not in present:
            present.append(m)
    # remove dropped modules (they won't render)
    present = [m for m in present if m not in drop_modules]
    if not present:
        return []

    priority = set(more_of_this)
    priority.update(m for m, r in reactions.items() if r == "too_hard")

    def rank(m):
        # energy-low: gym warmup first, always
        if energy == "low" and m == "gym":
            return -1
        return 0 if m in priority else 1

    ordered = sorted(present, key=lambda m: (rank(m), present.index(m)))
    # Only emit an order if it actually differs from the observed order (avoid noise).
    if ordered == present:
        return []
    return ordered


# --------------------------------------------------------------------------- io

def _write_override(path, override):
    text = json.dumps(override, indent=2, ensure_ascii=False) + "\n"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Woodshed feedback agent (writer): feedback.jsonl -> plan-override.json")
    sd = _script_dir()
    parser.add_argument("--feedback", default=os.path.join(sd, "feedback.jsonl"),
                        help="path to feedback.jsonl (default: next to this script)")
    parser.add_argument("--mission-control", default=os.path.join(sd, "mission-control.json"),
                        help="path to mission-control.json (optional; read-only context)")
    parser.add_argument("--out", default=os.path.join(sd, "plan-override.json"),
                        help="output path (default: plan-override.json next to this script)")
    parser.add_argument("--today", default=None,
                        help="YYYY-MM-DD day being STEERED (default: system local date). "
                             "Feedback join key is today-1.")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the override JSON to stdout, write nothing")
    args = parser.parse_args(argv)

    # Resolve the steered day. Bad --today -> fail-soft no-op (don't break the day).
    if args.today:
        try:
            today = _parse_date(args.today)
        except ValueError:
            print("woodshed: --today '%s' is not YYYY-MM-DD; no override written" % args.today)
            return 0
    else:
        today = _dt.date.today()

    yesterday = today - _dt.timedelta(days=1)
    yk = _iso_date(yesterday)

    # Read inputs, fail-soft on everything.
    try:
        fb = _read_feedback_line(args.feedback, yk)
    except Exception as e:  # pragma: no cover — defensive; _read_feedback_line is already safe
        print("woodshed: error reading feedback (%s); no override written" % e)
        return 0

    if fb is None:
        print("no feedback for %s; serving static curriculum" % yk)
        return 0

    mc = _read_mission_control(args.mission_control)  # optional; None is fine

    try:
        override = build_override(fb, mc, today)
    except Exception as e:
        # Never throw on bad input — mirror the reader's "never break the day" ethos.
        print("woodshed: failed to build override (%s); no override written" % e)
        return 0

    if override is None:
        print("feedback for %s is neutral (no steering signal); serving static curriculum" % yk)
        return 0

    if args.dry_run:
        print(json.dumps(override, indent=2, ensure_ascii=False))
        return 0

    try:
        _write_override(args.out, override)
    except OSError as e:
        print("woodshed: could not write %s (%s); no override written" % (args.out, e))
        return 0

    print("woodshed: wrote %s steering %s (from feedback dated %s)"
          % (args.out, _iso_date(today), yk))
    return 0


if __name__ == "__main__":
    sys.exit(main())
