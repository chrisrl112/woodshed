#!/bin/sh
# git-hooks/install.sh — wood-69 / milestone M4 (the hub publish pipeline)
#
# OPT-IN INSTALLER for the sample pre-push hook (git-hooks/pre-push). YOU run
# this; nothing runs it for you. It copies the sample hook into
# .git/hooks/pre-push so that `git push` will run the publish gate and block a
# push when the gate fails.
#
# It is idempotent and SAFE:
#   - backs up any existing .git/hooks/pre-push to pre-push.bak-<timestamp>
#     before overwriting,
#   - re-running it just refreshes the installed copy,
#   - uninstall by deleting .git/hooks/pre-push (and restoring a .bak if you
#     want your old hook back).
#
# USAGE:
#     ./git-hooks/install.sh
#
# POSIX sh. No network. Touches only your local .git/hooks directory.

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SOURCE_HOOK="$SCRIPT_DIR/pre-push"

# Locate the repo's .git/hooks directory.
if REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null); then
    :
else
    echo "install.sh: not inside a git repository (git rev-parse failed)." >&2
    echo "  -> Run this from within the Woodshed git repo." >&2
    exit 1
fi

# Honor a custom hooksPath if the user has configured one; else default.
HOOKS_PATH=$(git config --get core.hooksPath 2>/dev/null || true)
if [ -n "$HOOKS_PATH" ]; then
    case "$HOOKS_PATH" in
        /*) HOOKS_DIR="$HOOKS_PATH" ;;
        *)  HOOKS_DIR="$REPO_ROOT/$HOOKS_PATH" ;;
    esac
else
    HOOKS_DIR="$REPO_ROOT/.git/hooks"
fi

if [ ! -f "$SOURCE_HOOK" ]; then
    echo "install.sh: source hook not found at $SOURCE_HOOK" >&2
    exit 1
fi

mkdir -p "$HOOKS_DIR"
TARGET="$HOOKS_DIR/pre-push"

# Back up any existing hook (but don't clobber a backup if our installed copy is
# already identical to the source — keeps re-runs quiet/idempotent).
if [ -e "$TARGET" ] || [ -L "$TARGET" ]; then
    if cmp -s "$SOURCE_HOOK" "$TARGET" 2>/dev/null; then
        echo "install.sh: pre-push already up to date at $TARGET — nothing to do."
        exit 0
    fi
    STAMP=$(date +%Y%m%d-%H%M%S)
    BACKUP="$TARGET.bak-$STAMP"
    cp -p "$TARGET" "$BACKUP"
    echo "install.sh: backed up existing hook -> $BACKUP"
fi

cp "$SOURCE_HOOK" "$TARGET"
chmod +x "$TARGET"
echo "install.sh: installed publish-gate pre-push hook -> $TARGET"
echo "  -> 'git push' will now run the publish gate and block on failure."
echo "  -> Bypass a single push with: git push --no-verify"
echo "  -> Uninstall by deleting: $TARGET"
