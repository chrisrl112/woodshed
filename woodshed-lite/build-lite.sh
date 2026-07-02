#!/bin/sh
# ============================================================================
# build-lite.sh — assemble the Woodshed Lite static deploy bundle
# ----------------------------------------------------------------------------
# Single source of truth: ../index.html (engine) + ../charts/ (data).
# This script EXTRACTS + FILTERS + ASSEMBLES + GATES. It never hand-copies
# engine code. Re-run it after any Woodshed change, then deploy dist/ manually.
#
# Run from anywhere; resolves its own dir and the project root.
#   ./woodshed-lite/build-lite.sh
#
# Exit 0 = dist/ built and passed the copyright gate (safe to deploy).
# Exit 1 = build or gate failed (do NOT deploy).
# ============================================================================
set -eu

DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$DIR/.." && pwd)
DIST="$DIR/dist"

echo "==> Woodshed Lite build"
echo "    project root: $ROOT"
echo "    output:       $DIST"
echo

rm -rf "$DIST"
mkdir -p "$DIST/vendor" "$DIST/assets" "$DIST/assets/drums/trim"

# ---------------------------------------------------------------------------
# STEP 1 — Extract the engine from canonical index.html
# ---------------------------------------------------------------------------
echo "[1/6] extract engine         … running extract-engine.py"
(cd "$ROOT" && python3 "$DIR/extract-engine.py")

# ---------------------------------------------------------------------------
# STEP 2 — Curated chart + warmup data for the allowlisted tunes
# ---------------------------------------------------------------------------
# charts-curated.js is already the hand-maintained PD-safe/changes-only subset
# of charts-ireal.js (see its own header). Ship it as-is; mount.js looks up
# each WSL_CONFIG.jam.tunes[].label in it at runtime and drops anything it
# can't find a match for, so an over-broad bundle here is harmless.
# clarke-warmups-lite.js is Chris's own hand-verified transcription of the two
# Second Study exercises the Warmup station renders (see its header comment).
echo "[2/6] chart + warmup data    … copying charts-curated.js, clarke-warmups-lite.js"
cp "$ROOT/charts/charts-curated.js" "$DIST/"
cp "$ROOT/charts/clarke-warmups-lite.js" "$DIST/"

# ---------------------------------------------------------------------------
# STEP 3 — Copy shared vendor libs + PD assets for the chosen tunes
# ---------------------------------------------------------------------------
echo "[3/6] copy vendor + assets   … copying shared libs"
cp "$ROOT/vendor/abcjs-basic-min.js" "$DIST/vendor/" 2>/dev/null || echo "      (vendor/abcjs missing — skipped)"
# NOTE: copy ONLY PD-safe assets (re-engraved warmups, your PD lead sheets,
# your own drum audio). NEVER copy reference/ PDFs (Real Book etc.).
cp "$DIR/lite.config.js" "$DIST/" 2>/dev/null || true
cp "$DIR/src/copy.js" "$DIST/"
# content.json is SYMLINKED, not copied: edit woodshed-lite/content.json directly
# and a browser refresh picks it up immediately — no rebuild needed.
ln -sf "$DIR/content.json" "$DIST/content.json"

# ---------------------------------------------------------------------------
# STEP 4 — Real drum-loop audio (charts/drums-manifest.js + the recordings it
# points at) so the Jam station's backing band uses actual recorded grooves
# instead of falling back to the synth kit. ~40MB — that's the real cost of
# shipping real drums; acceptable for a demo bundle.
# ---------------------------------------------------------------------------
echo "[4/6] drum-loop audio        … copying drums-manifest.js + assets/drums/trim/*.mp3"
cp "$ROOT/charts/drums-manifest.js" "$DIST/"
cp "$ROOT/assets/drums/trim/"*.mp3 "$DIST/assets/drums/trim/" 2>/dev/null || echo "      (no drum audio found — Jam station will fall back to the synth kit)"

# ---------------------------------------------------------------------------
# STEP 5 — Assemble dist/index.html
# ---------------------------------------------------------------------------
# dist/index.html = the landing shell (src/shell.html) with <script> tags
# injected for lite.config.js + src/mount.js + src/votes.js at
# <!-- MOUNT_PLACEHOLDER -->. Order matters: config (defines WSL_CONFIG) →
# mount → votes (reads WSL_CONFIG, wires the Supabase vote board).
# engine.js, charts-curated.js, clarke-warmups-lite.js and drums-manifest.js
# are loaded by their own <script src> tags already present in shell.html.
echo "[5/6] assemble index.html    … injecting config + mount.js + votes.js into the shell"
python3 - "$DIR/src/shell.html" "$DIR/lite.config.js" "$DIR/src/mount.js" "$DIR/src/votes.js" "$DIST/index.html" <<'PYEOF'
import pathlib, sys
shell, config, mount, votes, out_p = [pathlib.Path(a) for a in sys.argv[1:]]
inject = (
    '<script>\n// lite.config.js\n' + config.read_text() + '\n</script>\n'
    '<script>\n// mount.js\n' + mount.read_text() + '\n</script>\n'
    '<script>\n// votes.js\n' + votes.read_text() + '\n</script>'
)
html = shell.read_text().replace('<!-- MOUNT_PLACEHOLDER -->', inject)
out_p.write_text(html)
PYEOF

# ---------------------------------------------------------------------------
# STEP 6 — Gates
# ---------------------------------------------------------------------------
# TWO gates with different scopes, and only ONE blocks the Lite deploy:
#
#   (a) verify_public_safe.py — THE copyright gate for what Lite actually ships
#       (scans lite.config.js: any lead-sheet melody must be PD, year <= 1930).
#       This is a HARD STOP. Never weaken it.
#
#   (b) ../publish.sh -> public-assets/ci_check.py — the MAIN-APP page-coverage
#       gate (Real Book render coverage). It is unrelated to the Lite bundle's
#       safety, and its pre-existing ~4-gap coverage warning must NOT block a
#       Lite deploy. We run it for visibility but treat it as ADVISORY here.
#       (If it's ever promoted to blocking for the main app, that's a main-app
#        concern; Lite ships on its own copyright gate.)
echo "[6/6] gates                  … Lite copyright gate (hard) + main-app coverage (advisory)"

echo "  (a) verify_public_safe.py (HARD) …"
if ! python3 "$DIR/verify_public_safe.py" "$DIR/lite.config.js"; then
    echo
    echo "BUILD BLOCKED — Lite copyright gate failed. dist/ is NOT safe to deploy." >&2
    exit 1
fi

echo
echo "  (b) ../publish.sh main-app coverage (ADVISORY — does not block Lite) …"
if [ -x "$ROOT/publish.sh" ]; then
    if "$ROOT/publish.sh"; then
        echo "      main-app gate: PASS"
    else
        echo "      main-app gate: WARN (advisory only — unrelated to the Lite bundle; NOT blocking)." >&2
    fi
else
    echo "      (../publish.sh not found/executable — advisory gate skipped)" >&2
fi

echo
echo "Done. dist/ built and passed the Lite copyright gate — safe to deploy."
echo "Deploy:  npx wrangler pages deploy $DIST --project-name woodshed-lite --commit-dirty=true"
