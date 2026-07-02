#!/usr/bin/env python3
"""prune_backups.py — retention cleanup for `*.bak-*` backup files.

Nightly agent edits leave behind dated backups (e.g. `index.html.bak-20260101...`,
`PUBLISH-GATE-README.md.bak-...`). They accumulate. This tool keeps the newest N
backups PER base file and prunes the rest.

USAGE
  python3 prune_backups.py                 # dry-run, keep newest 5 per base file
  python3 prune_backups.py --keep 5        # same, explicit
  python3 prune_backups.py --keep 10       # keep newest 10 instead
  python3 prune_backups.py --dir /some/dir # scan a different directory
  python3 prune_backups.py --keep 5 --apply  # ACTUALLY delete the old ones

By DEFAULT this is a DRY-RUN: it prints what WOULD be pruned and deletes nothing.
Only `--apply` performs real deletion (os.remove).

HOW TO ACTUALLY PRUNE (Chris, run this yourself when ready)
  Open a terminal in Projects/Trumpet and run:

      python3 prune_backups.py --keep 5 --apply

  That deletes every `*.bak-*` backup except the 5 most-recent per base file.
  It NEVER touches a live file (only names containing `.bak-` are ever considered).
  Run without `--apply` first to preview exactly what will go.

Stdlib only. No network. Safe by construction: only files matching `*.bak-*` are
ever considered, so live sources like `index.html` or `charts.js` cannot be touched.
"""

import argparse
import glob
import os
import sys
from datetime import datetime

BACKUP_GLOB = "*.bak-*"
MARKER = ".bak-"


def human_bytes(n):
    """Format a byte count compactly."""
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024.0:
            return f"{n:,.1f} {unit}" if unit != "B" else f"{n:,} {unit}"
        n /= 1024.0
    return f"{n:,.1f} TB"


def base_name(filename):
    """Group key: everything before the FIRST `.bak-`.

    'index.html.bak-20260101' -> 'index.html'
    'PUBLISH-GATE-README.md.bak-x' -> 'PUBLISH-GATE-README.md'
    """
    return filename.split(MARKER, 1)[0]


def collect_groups(target_dir):
    """Return {base: [(path, mtime, size), ...]} for all `*.bak-*` files."""
    groups = {}
    pattern = os.path.join(target_dir, BACKUP_GLOB)
    for path in glob.glob(pattern):
        if not os.path.isfile(path):
            continue
        name = os.path.basename(path)
        # SAFETY: hard assert we only ever handle real backup files.
        assert MARKER in name, f"refusing non-backup file: {name!r}"
        try:
            st = os.stat(path)
        except OSError:
            continue
        groups.setdefault(base_name(name), []).append(
            (path, st.st_mtime, st.st_size)
        )
    return groups


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Retention cleanup: keep newest N `*.bak-*` backups per base "
                    "file, prune the rest. DRY-RUN unless --apply is given."
    )
    parser.add_argument(
        "--keep", type=int, default=5, metavar="N",
        help="how many newest backups to keep per base file (default: 5)",
    )
    parser.add_argument(
        "--dir", default=None, metavar="PATH",
        help="directory to scan (default: this script's own directory)",
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="ACTUALLY delete prune candidates (default is dry-run)",
    )
    args = parser.parse_args(argv)

    if args.keep < 0:
        parser.error("--keep must be >= 0")

    target_dir = args.dir or os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.abspath(target_dir)
    if not os.path.isdir(target_dir):
        print(f"error: not a directory: {target_dir}", file=sys.stderr)
        return 1

    mode = "APPLY (deleting)" if args.apply else "DRY-RUN (no deletion)"
    print("=" * 64)
    print(f"prune_backups — {mode}")
    print(f"dir : {target_dir}")
    print(f"keep: newest {args.keep} per base file")
    print("=" * 64)

    groups = collect_groups(target_dir)
    if not groups:
        print("\nNo `*.bak-*` backup files found. Nothing to do.")
        return 0

    total_reclaimable = 0
    total_prune_count = 0
    total_backups = 0

    for base in sorted(groups):
        files = groups[base]
        total_backups += len(files)
        # newest first
        files.sort(key=lambda t: t[1], reverse=True)
        keep = files[: args.keep]
        prune = files[args.keep:]

        print(f"\n[{base}]  ({len(files)} backups -> keep {len(keep)}, "
              f"prune {len(prune)})")

        for path, mtime, size in keep:
            ts = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            print(f"  KEEP   {os.path.basename(path):<48} {ts}  "
                  f"{human_bytes(size)}")

        for path, mtime, size in prune:
            ts = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            verb = "DELETE" if args.apply else "WOULD-PRUNE"
            print(f"  {verb:<6} {os.path.basename(path):<48} {ts}  "
                  f"{human_bytes(size)}")
            total_reclaimable += size
            total_prune_count += 1
            if args.apply:
                try:
                    os.remove(path)
                    print(f"         removed: {path}")
                except OSError as e:
                    print(f"         ERROR removing {path}: {e}",
                          file=sys.stderr)

    print("\n" + "=" * 64)
    print(f"base files     : {len(groups)}")
    print(f"total backups  : {total_backups}")
    if args.apply:
        print(f"deleted        : {total_prune_count}")
        print(f"reclaimed      : {human_bytes(total_reclaimable)}")
    else:
        print(f"would prune    : {total_prune_count}")
        print(f"reclaimable    : {human_bytes(total_reclaimable)}")
        print("\n(DRY-RUN: nothing was deleted. Re-run with --apply to prune.)")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    sys.exit(main())
