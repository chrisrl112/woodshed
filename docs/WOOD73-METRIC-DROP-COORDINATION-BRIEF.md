# WOOD-73 — Heartbeat Metric Drop: Cross-Project Coordination Brief

*Milestone M4 · Board: wood-73 · Decision applied: wood-47-metric-source (Chris-resolved) · Drafted night-shift-woodshed 2026-06-25 · DOC ONLY — no edits applied*

---

## Decision being applied

**wood-47-metric-source (resolved by Chris):** drop the two unsourced heartbeat metrics
`sessions_total` and `hours_total` from the Woodshed heartbeat manifest; **keep the one honest
metric `streak_days`.** This is option **(b)** from the emitter spec §3 — shrink the manifest to
what it can actually source, rather than fabricating the two missing numbers. On the hub card, the
two dropped metrics render as em-dashes (or simply don't render) — see the hub-side follow-on below.

The emitter side already conforms: `woodshed_heartbeat.py` emits **only** `streak_days` and
deliberately OMITS the other two (verified below). **Only the two manifest files lag the decision.**

---

## The trap (read before touching anything)

`manifest.json` exists in **two** synchronized copies — a spoke copy (woodshed-owned) and a hub
canonical copy (portfolio-hub-owned). `build_manifest.py` sync-checks **every shared top-level key,
`metrics` included**, between them on every run. Dropping the two metrics from **one** copy alone
makes spoke (1 metric) ≠ hub (3 metrics), so `build_manifest.py` FAILS on drift → `ci_check.py`
FAILS → **the M4 publish gate breaks.** The fix is therefore a **lockstep edit of BOTH files in one
change** — and one of them lives in a different project, off-limits to the woodshed agent.

Evidence from `public-assets/build_manifest.py`:

```python
# line 79
SYNC_KEYS = REQUIRED_KEYS + OPTIONAL_KEYS          # REQUIRED_KEYS includes "metrics" (lines 57-61)

# lines 50-52 — the hub canonical it compares against
HUB_CANONICAL_PATH = os.path.join(
    PROJECTS, "Portfolio Hub", "build-prep", "projects", "the-woodshed", "manifest.json"
)

# check_sync(), lines 273-283 — fails on ANY shared field that differs
for k in SYNC_KEYS:
    ...
    if in_pub and published.get(k) != canonical.get(k):
        errors.append("sync: field '{}' differs from hub canonical manifest".format(k))
```

---

## The exact lockstep edit

Both files must end with the **same** single-metric `metrics` array. Edit BOTH, then verify once.

### File 1 — `Projects/Trumpet/public-assets/manifest.json`  *(woodshed-owned)*

BEFORE (lines 56-60):
```json
  "metrics": [
    { "label": "Current streak", "source": "heartbeat", "key": "streak_days" },
    { "label": "Sessions logged", "source": "heartbeat", "key": "sessions_total" },
    { "label": "Total hours", "source": "heartbeat", "key": "hours_total" }
  ],
```

AFTER:
```json
  "metrics": [
    { "label": "Current streak", "source": "heartbeat", "key": "streak_days" }
  ],
```

### File 2 — `Projects/Portfolio Hub/build-prep/projects/the-woodshed/manifest.json`  *(portfolio-hub-owned — NOT the woodshed agent's to edit)*

Currently **identical** to File 1 (same 3-metric block, same lines 56-60). Apply the **same**
BEFORE → AFTER. Both files keep ONLY the `streak_days` metric object.

> ⚠️ The two files must remain byte-identical on the `metrics` key after the edit. Copy the exact
> AFTER block into both; don't hand-retype and risk a whitespace/label drift that `check_sync` will
> reject.

---

## Ownership / coordination

- **The woodshed night agent CANNOT touch File 2.** It lives in the `portfolio-hub` project — a
  cross-project guardrail. This brief stops at documenting the edit; it does not apply it.
- **Both edits must land together** in one logical change. Two ways to do that:
  1. **Single human edit** — Chris edits both files in one sitting, then runs the verify command.
  2. **Paired run** — a portfolio-hub agent edits File 2 in the same change a woodshed agent edits
     File 1, coordinated so neither is committed/verified alone.
- Applying File 1 alone (or File 2 alone) is the failure mode the whole brief exists to prevent — it
  red-flags the publish gate.

---

## Verification after apply (one gate)

From `Projects/Trumpet/`:

```bash
python3 public-assets/build_manifest.py   # must print PASS (schema-valid + in sync with hub canonical)
python3 public-assets/ci_check.py         # must exit 0
```

If `build_manifest.py` reports a `sync:` error or `ci_check.py` exits non-zero, the two manifests are
out of sync — re-check that File 1 and File 2 carry the identical single-metric block.

---

## Hub-side follow-on (don't lose this)

The **card rendering** — showing "—" for `sessions_total` / `hours_total`, or simply not rendering
them once dropped — is a **portfolio-hub hub-side concern**, NOT in the woodshed manifest's scope.
Once the metric is dropped from the manifest, the hub card naturally has nothing to render for those
two keys; confirm the hub card degrades cleanly (em-dash or omission, never a fabricated 0 or blank
box). Flag this as the **portfolio-hub follow-on** so it doesn't fall through the cross-project crack.

---

## Status

- **wood-73 APPLY: OPEN** — pending the lockstep cross-project edit of both manifests (File 1 +
  File 2), landed together and verified by the one command above.
- **Emitter side: ALREADY CONFORMS** — `woodshed_heartbeat.py` emits only `streak_days`; no emitter
  change needed.
- **This brief: complete.** No files were edited; the only file created is this brief.
