# Engraver Battle Test — Clarke Second Study (Exercise 27)

**Date:** Jun 29, 2026 · **Source:** `Technical Studies.pdf` p.8 (printed), Second Study, ex. 27 · **Engine:** `omr-engine/omr.py`

## TL;DR

The engine **is not broken.** On a clean engraved score it's near-perfect; on *your* Clarke scan it makes systematic, diagnosable errors. The bottleneck is **input quality**, not the algorithm. "Perfect" is a property of the *workflow* (clean source + verify-and-diff loop), not of any reader — no OMR, commercial included, is perfect on a faded photocopy. Don't try to make OMR magic. Make the input clean and keep a human-verified loop.

## The evidence (same engine, two inputs)

**Clean engraving (engine's own test score):** flawless.
```
16 notes: C4 D4 E4 F4 G4 A4 B4 C5  C5 B4 A4 G4 F4 E4 D4 C4   (all quarter notes) ✓
```

**Your Clarke photocopy (ex. 27), best settings (`--thr 180 --deskew`):**
```
K:C  M:4/4 L:1/16
E,2 F,2 G,2 E,2 F,2 G,2 A,2 F,2 | G,2 A,2 B,2 z2 G,2 E,2 F,2 G,2 | ...
```
Right idea, wrong in four specific ways (below).

## Failure modes — named and ranked

### THE HEADLINE BUG (found via Chris's ground-truth read): staff baseline off by one line → every pitch a third low

Chris transcribed ex. 27 directly from the book: `G A B G A B C A | B C D B G A B G | A B C A F♯ G A F♯ | G B A G A C B A | G`.
My output (and the OMR engine's) read **a diatonic third too low** — `E F♯ G…` where truth is `G A B…`.

**Root cause:** the staff-line detector locked onto the **wrong 5 lines** — it placed the bottom line (E4) one staff-position (~25px) too low. Every pitch is read by counting steps off that baseline, so a baseline off by one line shifts the *entire* line down a third. Not an octave, not a key issue — a **staff-anchor off-by-one.**

**The trap that fooled me:** the OMR engine and my independent pixel-centroid method made the *same* anchoring error, so they agreed — and I read that agreement as confirmation. Then I "verified" by counting ledger lines **against the same bad baseline**, which of course confirmed the wrong answer. Two automated methods plus a self-check can be **collectively wrong** when they share the same flawed assumption. The only thing that caught it was a human (Chris) reading the actual notes off the page.

| # | Error | What happened | Root cause | Fix |
|---|---|---|---|---|
| 1 | **Pitch a third low** (the big one) | `E F♯ G…` vs true `G A B…` | Staff baseline mis-located by one line | **Anchor pitch to the CLEF glyph**, not raw line-peak detection (see below) |
| 2 | **Key signature dropped** | `K:C`, no F♯ | Key-sig lost on the cropped single staff | Pipe detected key through to crops |
| 3 | **Spurious rests** | Phantom `z2` in beam gaps | Gap→rest threshold too loose | Tighten threshold |
| 4 | **No meter inference** | Defaulted 4/4 ÷16; it's cut-time eighths | Engine doesn't read the time signature | Read ¢/C, or set in-app |

**The single highest-value engine fix:** anchor the vertical pitch scale to the **treble-clef glyph** (the clef's curl unambiguously fixes the G4 line), then *validate* the detected 5-line staff against it — if they disagree, trust the clef. That one change prevents the entire third-error class on degraded scans. Right now the engine trusts horizontal-line peak detection, which on this scan was corrupted by the slur arc, thick beams, and a faint top line — yielding a 5-line group shifted one position down.

**What the engine got right:** rhythm (continuous even eighths), note ordering, and melodic *contour* (interval shape). What it got wrong was the absolute vertical anchor — which, unfixed, makes every note wrong.

**Meta-lesson for the product:** this is exactly why "automated reader → human verify" beats "trust the reader." But note the verify step only works if the human checks against the **source**, not against a re-render of the machine's own (possibly mis-anchored) output. The render-and-diff must diff against the original page.

## Why this scan is near-worst-case

This isn't a clean engraving — it's a heavy, faded photocopy with handwritten annotations ("BIG BREATH CHEST UP"), noteheads smeared into ledger lines in the low register, and a long slur arc over the whole line. That combination defeats algorithmic OMR **and** careful human reading (I had low confidence calling exact pitches at full zoom — which is itself the finding: garbage in, garbage out). The engine's gates are validated on clean engraved renders and the Real-Book regime, not faded low-register etudes.

Also notable: the default threshold returned **0 systems** — the engine only saw the staff at all with `--thr 180 --deskew`. On a bad scan, even "is there music here" is fragile.

## What to do about it — the recommendation

**1. Fix the input, not just the reader (biggest lever).**
For the PD warmups (Clarke/Arban) you actually need, don't OCR a bad photocopy. These are *finite, fixed, published* exercises — you don't need OMR to "discover" Clarke 2, it's a known quantity. Options, best first:
- **Enter/verify once from the canonical edition, own a perfect asset forever.** One careful pass per exercise → a clean ABC library you never have to re-read. For a demo you need *one* exercise, perfect — this is the fastest route to that.
- **Re-source a cleaner scan** (IMSLP has cleaner Clarke/Arban plates than this photocopied edition) before any OMR.

**2. Treat OMR as a first-draft accelerator, never an autonomous engraver.**
Your `score-to-woodshed` skill already encodes the right method: draft → render → **diff against source** → fix. OMR produces the draft; the render-and-diff loop catches exactly errors #1–#4 in one or two passes. "Perfect" comes from the loop, not the reader. This is also how every pro uses commercial OMR (Audiveris/PhotoScore/SmartScore) — first draft + correction.

**3. If you want to invest in the engine itself, the ranked backlog:**
- **(a) Octave/clef anchor robustness** — anchor pitch to the detected clef glyph and sanity-check against the ledger-line span. Single biggest accuracy win on real scans.
- **(b) Key-sig pass-through on crops** — carry the detected signature into single-staff reads so F♯ isn't dropped.
- **(c) Spurious-rest suppression** — tighten the gap→rest threshold.
- **(d) Scan pre-processing** — normalize contrast + despeckle + deskew + higher DPI before reading; refuse/flag when staff confidence is low instead of emitting a bad read.
- **(e) Time-sig read** (or just set meter/tempo in the Woodshed UI — for playback the measure grid matters more than notated rhythm).

**4. Product decision for the demo (do this now):**
You need ONE clean Clarke exercise in the warmup station — not a general OMR pipeline. Hand-verify exercise 27 once (crop-read-verify loop), render it in the Woodshed, ship it. Reserve the OMR build for the *later* feature where users import their own arbitrary charts — and even then, ship it as **draft + verify**, not "magic."

## Exercise 28 — the failure reproduced (feasibility confirmed)

Ran the same process on ex. 28. Confirmed by reading: **3 flats (E♭ major)**, cut time, eighth notes beamed in 4s, low register, sequential Clarke wave. **But the absolute pitch could not be pinned** — the staff baseline is ambiguous to ±1 line on this scan, exactly as on 27, so the whole line floats by a third depending on which 5 horizontal lines you call "the staff." Two exercises, same root failure, both methods. This is a *reproducible* limitation, not a one-off.

**Bottom line on feasibility (autonomous reading of THIS source):** **Not reliable.** The contour/rhythm/key are recoverable; the absolute pitch is not, because staff-baseline detection fails on a faded photocopy with interfering slurs and beams. A draft is achievable; a *correct* result requires a human to anchor the pitch — or a clean source.

**What WOULD make it feasible:**
1. **Clean source** (IMSLP plates / a sharp scan) — removes the baseline ambiguity at the root. Most of the error here is the photocopy, not the concept.
2. **Clef-anchored pitch** in the engine (anchor to the treble-clef glyph, validate staff lines against it) — the specific code fix.
3. **Human-in-the-loop verify** against the *original page* — the workflow that actually shipped a correct ex. 27 (Chris read it; I rendered and diffed).

For the product: the realistic feature is **"clean source → draft → human verifies in seconds,"** not "point it at any photocopy and trust it." The Clarke/Arban warmups you need are finite and fixed — keying them once from a clean edition (as you did for 27) is faster and 100% correct, versus engineering an OMR pipeline to fight bad scans.

## Honest expectation-setting

A "tool that makes this easy and perfect" for *arbitrary* sheet music doesn't exist — not from this engine, not from commercial OMR. What's achievable and genuinely valuable: **clean source → automated first draft → fast verify-and-diff → confirmed-correct ABC.** That's "easy," reliably correct, and a real feature. Aiming for "perfect autonomous reading of any scan" is the one version of this that will keep disappointing you.

## Next step (pick one)
- **A —** I produce a clean, verified ABC of Clarke ex. 27 right now (crop-read-verify) and drop it into the Woodshed warmup station. *(Fastest path to a working demo asset.)*
- **B —** I prototype fix (a) — octave/clef-anchor — on `omr.py` and re-test on ex. 27 to see how much accuracy it recovers. *(Invests in the engine.)*
- **C —** I pull a cleaner Clarke source (IMSLP) and re-run the engine to quantify how much of the error was just scan quality. *(Proves the input hypothesis.)*
