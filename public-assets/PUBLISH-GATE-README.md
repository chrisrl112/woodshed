# Publish Gate (`ci_check.py`) — wood-68 / milestone M4

A single **pre-publish / CI gate** for the Woodshed spoke. It fails the publish
when either of two conditions is true, so a bad bundle or a drifted manifest can
never ship to the Compound Interests hub.

This is the named follow-on CI gate from the wood-48 hub-ingestion contract
("Follow-on CI gate = wood-68"). It does **not** re-implement any validation — it
orchestrates the two existing, already-passing gate scripts into one verdict.

## What it runs

`ci_check.py` invokes both gate scripts as subprocesses (using `sys.executable`,
not bare `python3`) and combines their results:

| Gate                  | Script                  | Enforces |
|-----------------------|-------------------------|----------|
| `build_manifest`      | `build_manifest.py`     | Published `manifest.json` validates against the **hub schema v1** and stays **in sync with the hub-side canonical manifest** (no drift); required data artifacts exist. This is the **hub-ingestion contract**. |
| `verify_public_safe`  | `verify_public_safe.py` | Public bundle ships **only exact page-images, never source books** — the copyright-safe **"full book never shipped"** guardrail. |

If either **blocking** child gate exits non-zero, the publish gate fails.

### Third gate: `tune_page_coverage` — **ADVISORY only** (wood-71)

| Gate                  | Script                            | Enforces |
|-----------------------|-----------------------------------|----------|
| `tune_page_coverage`  | `verify_tune_page_coverage.py`    | Every app tune reference (`page:<N>` in `index.html`) has a covering Real Book **page-image** (a manifest entry at `printedPage == N` whose image file exists on disk). Detects coverage gaps. |

This gate **always runs and always surfaces its result**, but is **advisory only**:
it prints `[ADVISORY PASS]` / `[ADVISORY WARN]` plus its full output, and **never
affects `ci_check.py`'s exit code**. The `PUBLISH GATE: PASS/FAIL` verdict depends
**only** on the two blocking gates above.

**Why advisory and not blocking (right now):** the verifier currently reports
**one known gap — Solar (24/25 covered)** — and exits non-zero. That gap is
[**wood-70**](#), a Chris-owned decision: the app references Solar at `page:363`
while the manifest/image is `printedPage:365`. Per standing directive **D4**,
detection must run by default and surface what it finds; **gating publish on an
unanswered decision would be a bug, not a safeguard.** So coverage runs as
detection today, visibly, without blocking publish.

**Promote to blocking once wood-70 is resolved** (Solar reconciled and the
verifier exits 0). The entire change is **one move in `ci_check.py`**: delete the
`tune_page_coverage` tuple from `ADVISORY_GATES` and append the *same tuple* to the
blocking `GATES` list. After that, a coverage gap fails the publish like any other
gate. (See the `TODO(wood-70->blocking)` marker in `ci_check.py`.)

## How to invoke

Runnable from anywhere (paths resolve relative to the script's own directory):

```sh
python3 public-assets/ci_check.py
```

Add `--verbose` (or `-v`) to stream each child gate's full output live. The
default mode prints a concise PASS/FAIL line per gate and only dumps a failing
gate's stdout/stderr.

```sh
python3 public-assets/ci_check.py --verbose
```

stdlib only (`subprocess`, `sys`, `os`, `argparse`) — no pip dependencies,
matching the no-pip philosophy of the existing scripts.

## Exit codes

| Exit | Meaning |
|------|---------|
| `0`  | **Both blocking** gates passed. Safe to publish. Final line: `PUBLISH GATE: PASS`. (An advisory `WARN` does **not** change this — it is informational only.) |
| `1`  | **Either blocking** gate failed. Do **not** publish. Final line names the failing gate(s), e.g. `PUBLISH GATE: FAIL (build_manifest)`. The failing child's output is surfaced so the cause is human-readable. The advisory `tune_page_coverage` gate can **never** produce this exit code. |

## How the gate is wired in (wood-69)

`ci_check.py` is the orchestrator; **wood-69 added the invoking layer** so a
non-zero gate result actually BLOCKS a publish. Three new files at the repo root
(`Projects/Trumpet/`) do the wiring. None of them deploy/publish anything — the
actual deploy stays a **manual** step Chris runs only *after* a green gate.

### 1. `./publish.sh` — the pre-publish runner (use this)

The canonical way to run the gate before publishing. From the repo root:

```sh
./publish.sh            # run the gate
./publish.sh --verbose  # flags are forwarded straight to ci_check.py
```

- Resolves its own directory, so it works from any cwd.
- On **exit 0**: prints `Publish gate passed — safe to publish.` and exits 0.
  Run your manual deploy step *after* this.
- On **non-zero**: prints `PUBLISH BLOCKED — gate failed` and exits 1, so any
  caller (terminal, hook, CI) aborts.
- It runs `python3 public-assets/ci_check.py "$@"` and **propagates the gate's
  exit code**. It does **not** itself deploy, push, or publish anything.

### 2. Opt-in git pre-push hook — block bad pushes

`git-hooks/pre-push` is a **sample** hook that runs `./publish.sh` and blocks a
`git push` (exit 1) when the gate fails. Hooks under `.git/hooks` are **not**
version-controlled, so the sample does nothing until you install it:

```sh
./git-hooks/install.sh   # opt-in; copies the sample into .git/hooks/pre-push
```

`install.sh` is idempotent and backs up any existing `pre-push` hook before
overwriting. To bypass the gate for a one-off push: `git push --no-verify`.
To uninstall: delete `.git/hooks/pre-push`.

> Note: nothing installs the hook automatically — you opt in by running
> `install.sh` yourself.

### 3. Future CI job (documented snippet — not yet a live workflow)

When the Woodshed spoke gets a CI pipeline, add the gate as a required step so a
failing gate fails the build. Example **GitHub Actions** snippet (illustrative —
this repo does **not** yet ship a live workflow file):

```yaml
# .github/workflows/publish-gate.yml  [confirm: not yet created — sample only]
name: publish-gate
on: [push, pull_request]
jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.x' }
      - name: Run Woodshed publish gate
        run: python3 public-assets/ci_check.py
        working-directory: Projects/Trumpet
```

> The gate is stdlib-only, so no `pip install` step is needed. `working-directory`
> assumes the spoke lives at `Projects/Trumpet/` inside the checked-out repo —
> `[confirm: repo layout / which repo hosts the spoke]` and adjust if different.

### Inlining the gate without `publish.sh`

If you ever need to gate inline (e.g. inside another script) without the runner:

```sh
if python3 public-assets/ci_check.py; then
    echo "Publish gate passed — proceeding."
    # ... publish/deploy ...
else
    echo "Publish gate FAILED — aborting publish." >&2
    exit 1
fi
```

> The actual deploy/publish mechanism for the Woodshed spoke is **not** encoded
> here: `[confirm: how the public bundle is actually published — manual upload,
> static host, hub-pull, etc.]`. `publish.sh` is the GATE in front of that step,
> whatever it turns out to be; the deploy itself stays Chris's manual action.

## What this guarantees (and what it doesn't)

- **Guarantees:** the published `manifest.json` is schema-valid and in sync with
  the hub's canonical copy (no drift), and the public bundle contains only the
  permitted page-images — no source books / full documents leak into a deploy.
- **Does not cover:** the runtime serve-time block (refusing to serve source PDFs
  at request time) — that is a separate task (wood-42, EPHEMERAL mode). Passing
  this gate certifies the *shipped bundle's contents* and the *manifest contract*,
  not the live server's request-time behavior.
