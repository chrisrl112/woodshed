#!/bin/sh
# publish.sh — wood-69 / milestone M4 (the hub publish pipeline)
#
# PRE-PUBLISH RUNNER for the Woodshed spoke. This is the GATE that runs BEFORE
# any manual publish/deploy. It invokes the existing publish-gate orchestrator
# (public-assets/ci_check.py) and propagates its exit code so that any caller
# (a human at the terminal, a git pre-push hook, or a future CI job) aborts the
# publish when the gate fails.
#
# WHAT THIS DOES vs. WHAT IT DOES NOT DO
#   DOES:     run the gate, print a clear verdict, exit 0 (pass) or 1 (blocked).
#   DOES NOT: deploy, publish, push, upload, or touch any remote. The actual
#             deploy stays Chris's MANUAL step. This script only certifies the
#             bundle/manifest are safe to publish; it never publishes anything.
#
# USAGE (runnable from anywhere — resolves its own dir):
#     ./publish.sh            # concise gate run
#     ./publish.sh --verbose  # forward flags straight to ci_check.py
#
# EXIT CODES
#   0  gate passed — safe to publish (then do your manual deploy)
#   1  gate failed — PUBLISH BLOCKED; do NOT deploy
#
# POSIX sh, stdlib python3 only. No pip, no network.

set -eu
# Emulate `pipefail` behavior where available (bash/zsh); harmless under dash.
( set -o pipefail ) 2>/dev/null && set -o pipefail || true

# Resolve this script's own directory so paths work from any cwd.
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

GATE="public-assets/ci_check.py"

if [ ! -f "$GATE" ]; then
    echo "PUBLISH BLOCKED — gate script not found: $SCRIPT_DIR/$GATE" >&2
    exit 1
fi

echo "==> Running Woodshed publish gate (wood-69) before publish..."
echo "    gate: $SCRIPT_DIR/$GATE"
echo

# Run the gate. We deliberately do NOT use `set -e` to abort here, because we
# want to print a tailored BLOCKED message on a non-zero exit before exiting.
set +e
python3 "$GATE" "$@"
GATE_RC=$?
set -e

echo
if [ "$GATE_RC" -ne 0 ]; then
    echo "PUBLISH BLOCKED — gate failed (ci_check.py exit $GATE_RC)." >&2
    echo "  -> Do NOT publish/deploy. Fix the gate failure(s) above and re-run." >&2
    exit 1
fi

echo "Publish gate passed — safe to publish."
echo "  -> The gate certifies the bundle + manifest only. Run your manual"
echo "     deploy step now; this script does NOT publish anything itself."
exit 0
