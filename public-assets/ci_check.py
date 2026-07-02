#!/usr/bin/env python3
"""
ci_check.py — wood-68 / milestone M4 (publish gate orchestrator)

The named follow-on CI gate from wood-48's published hub-ingestion contract
("Follow-on CI gate = wood-68"). This is plumbing only: it does NOT re-implement
any validation. It ORCHESTRATES the two existing, already-passing gate scripts
into a single publish gate and gives one combined exit code, so a publish step
(or CI job) can call ONE command and abort the publish if either gate fails.

WHAT IT RUNS (both as subprocesses, via sys.executable — never bare "python3")
  1. build_manifest.py      — validates the published manifest.json against the
                              hub schema v1, asserts it stays IN SYNC with the
                              hub-side canonical manifest (no drift), and checks
                              the data artifacts exist. (hub-ingestion contract)
  2. verify_public_safe.py  — asserts the public bundle ships only exact
                              page-IMAGES, never source books / full documents.
                              (copyright-safe "full book never shipped" guardrail)

PLUS one ADVISORY gate (wood-71) that ALWAYS runs and ALWAYS surfaces its result
but NEVER affects the exit code:
  3. verify_tune_page_coverage.py — every app `page:<N>` tune ref has a covering
                              page-image. Advisory-only today because it is
                              blocked_by wood-70 (Solar page 363 vs 365 = one known
                              gap); per directive D4, detection must run by default
                              and must not gate publish on an unanswered decision.
                              Promote to blocking by moving it into GATES once
                              wood-70 greens. See ADVISORY_GATES below.

EXIT CODES (depend ONLY on the two blocking GATES; advisory never counts)
  0  — BOTH gates passed. Safe to publish.
  1  — EITHER gate failed. Do NOT publish. The failing gate's stdout/stderr is
       surfaced so the cause is human-readable, and the final line names which
       gate(s) failed.

USAGE (runnable from anywhere — paths resolve relative to this script's dir)
    python3 public-assets/ci_check.py
    python3 public-assets/ci_check.py --verbose   # stream child output live

stdlib only (subprocess, sys, os, argparse) — no pip installs, matching the
no-pip philosophy of build_manifest.py / verify_public_safe.py.
"""

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))  # .../public-assets

# The two child gate scripts, in the order we run them. Each tuple is
# (short id used in the summary line, human label, script filename).
GATES = [
    ("build_manifest", "Manifest schema v1 + hub sync (hub-ingestion contract)",
     "build_manifest.py"),
    ("verify_public_safe", "Public-bundle copyright guardrail (full book never shipped)",
     "verify_public_safe.py"),
]

# ---------------------------------------------------------------------------
# ADVISORY gates — RUN ALWAYS, SURFACE ALWAYS, but NEVER affect the exit code.
# ---------------------------------------------------------------------------
# Why advisory (and not in GATES above)? This gate (wood-71) is blocked_by
# wood-70, a Chris-owned decision: the app references Solar at page:363 but the
# manifest/image is printedPage:365, so the coverage verifier reports exactly ONE
# gap (Solar — 24/25 covered) and EXITS 1 today. Per standing directive D4,
# detection must run by default and surface what it finds; gating publish on an
# unanswered decision would be a bug, not a safeguard. So coverage is wired in as
# a THIRD gate that ALWAYS runs and ALWAYS prints its result, but is ADVISORY:
# it does NOT append to `failed` and does NOT change the overall exit code. The
# final PUBLISH GATE verdict depends ONLY on the two blocking GATES above.
#
# TODO(wood-70->blocking): once wood-70 is resolved (Solar page reconciled and the
# verifier exits 0), promote coverage to BLOCKING by deleting it from ADVISORY_GATES
# and appending the same tuple to GATES above. That one move is the entire change.
ADVISORY_GATES = [
    ("tune_page_coverage",
     "Every app page:<N> tune ref has a covering page-image (wood-45)",
     "verify_tune_page_coverage.py"),
]


def run_gate(gate_id, label, script, verbose):
    """Run one child gate script as a subprocess.

    Returns (passed: bool, stdout: str, stderr: str). The child's relative paths
    are resolved from its own __file__, but we still set cwd=HERE so the child
    runs exactly as its docstring documents ("cd public-assets; python3 ...").
    """
    script_path = os.path.join(HERE, script)
    if not os.path.isfile(script_path):
        return (False, "", "gate script not found: {}".format(script_path))

    if verbose:
        # Stream the child's output live; let it inherit our stdout/stderr.
        print("=" * 70)
        print(">>> running gate: {} ({})".format(gate_id, script))
        print("=" * 70)
        proc = subprocess.run(
            [sys.executable, script_path],
            cwd=HERE,
        )
        return (proc.returncode == 0, "", "")

    # Default (concise) mode: capture output, only surface it on failure.
    proc = subprocess.run(
        [sys.executable, script_path],
        cwd=HERE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,  # text mode (py3.6-compatible alias for text=True)
    )
    return (proc.returncode == 0, proc.stdout or "", proc.stderr or "")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Woodshed publish gate (wood-68): run both gate scripts "
            "(build_manifest.py + verify_public_safe.py) and fail the publish "
            "if EITHER fails. Exit 0 = safe to publish, non-zero = abort."
        ),
        epilog=(
            "Enforces the hub-ingestion contract (manifest schema v1 in sync "
            "with the hub canonical copy) and the copyright-safe guardrail "
            "(full source books never shipped)."
        ),
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Stream each child gate's full output live (default: concise "
             "pass/fail per gate, with full output shown only for failures).",
    )
    args = parser.parse_args(argv)

    print("Woodshed publish gate (wood-68) — orchestrating {} gate(s)".format(len(GATES)))
    print("public-assets: {}".format(HERE))
    print("-" * 70)

    failed = []  # list of gate_ids that failed
    for gate_id, label, script in GATES:
        passed, out, err = run_gate(gate_id, label, script, args.verbose)

        if args.verbose:
            # Output already streamed above; just print the verdict line.
            print("[{}] {} — {}".format("PASS" if passed else "FAIL", gate_id, label))
        else:
            print("[{}] {} — {}".format("PASS" if passed else "FAIL", gate_id, label))
            if not passed:
                # Surface the child's output so the failure is human-readable.
                print("    ----- {} output (stdout) -----".format(script))
                for line in (out.rstrip("\n").splitlines() or ["<no stdout>"]):
                    print("    {}".format(line))
                if err.strip():
                    print("    ----- {} output (stderr) -----".format(script))
                    for line in err.rstrip("\n").splitlines():
                        print("    {}".format(line))

        if not passed:
            failed.append(gate_id)

    # ----- ADVISORY pass (wood-71): runs always, surfaces always, NEVER blocks -----
    # Deliberately a SEPARATE loop from the blocking one above: it uses the same
    # run_gate helper and prints a clear [ADVISORY PASS/WARN] line + the gate's
    # output, but it does NOT touch `failed` and does NOT affect the return code.
    # See ADVISORY_GATES note above for why (wood-70). TODO(wood-70->blocking).
    if ADVISORY_GATES:
        print("-" * 70)
        print("ADVISORY gate(s) — informational only, do NOT affect the publish verdict:")
    for gate_id, label, script in ADVISORY_GATES:
        passed, out, err = run_gate(gate_id, label, script, args.verbose)
        verdict = "PASS" if passed else "WARN"
        print("[ADVISORY {}] {} — {}".format(verdict, gate_id, label))
        if args.verbose:
            # Output already streamed live by run_gate; nothing more to surface.
            pass
        else:
            # Surface the advisory gate's output regardless of pass/warn, so its
            # coverage result is always visible (D4: detection surfaces what it finds).
            print("    ----- {} output (stdout) -----".format(script))
            for line in (out.rstrip("\n").splitlines() or ["<no stdout>"]):
                print("    {}".format(line))
            if err.strip():
                print("    ----- {} output (stderr) -----".format(script))
                for line in err.rstrip("\n").splitlines():
                    print("    {}".format(line))
        if not passed:
            print("    NOTE: advisory WARN is EXPECTED today (wood-70: Solar page "
                  "363 vs 365). It does NOT block publish. Promote to blocking only "
                  "after wood-70 greens (move this gate into GATES).")
    # NOTE: ADVISORY_GATES intentionally never append to `failed`.

    print("-" * 70)
    if failed:
        print("PUBLISH GATE: FAIL ({})".format(", ".join(failed)))
        print("  -> Do NOT publish. Fix the gate(s) above and re-run this check.")
        return 1

    print("PUBLISH GATE: PASS")
    print("  -> Both gates passed. Bundle + manifest are safe to publish.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
