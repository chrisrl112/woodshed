# A4 — L1 Identity Reconciliation Brief

**Board item:** wood-16 · **Date:** 2026-06-14 · **Type:** decision-support (audit only; no source docs were edited)
**One-line answer:** L1 as shipped is a **real Chet Baker transcription**, not a style-of adaptation. The approaches log is right; the A4 brief's blanket "L1–L5 are device-cited adaptations" claim is wrong about L1.

---

## (a) The discrepancy

Two project docs describe L1's identity incompatibly. `A4-VOCAB-APPROACHES.md` (and `TRANSCRIPTION-POSTMORTEM.md`) state that one lick — **Chet Baker, "Let's Get Lost," bars 9–11** — was "approved and locked" and installed as **L1** in `index.html`'s `LICKS` object, as a real human-ear-picked, note-level transcription from the Weimar Jazz Database. `A4-VOCAB-BRIEF.md` instead asserts, in its provenance note (§b), that "*This matches how L1–L5 were already handled (they cite the device, not a specific recording)*" — i.e., it claims L1 is an idiomatic "style-of"/"adapted" line, not a verbatim recording transcription. Both cannot be true of L1.

## (b) Ground truth — what L1 actually is in the shipped app

L1 lives in **`index.html`**, line 556, as the only entry currently in the `const LICKS=[...]` array (L2–L10 are not present in the live array; only L1 ships). Its stored fields are, verbatim:

- **`name`:** `"Chet Baker — Let's Get Lost"`
- **`src`:** `"Chet Baker, 'Let's Get Lost' (Weimar Jazz DB) bars 9-11 + held G"`
- **`lore`:** `"From Chet Baker's solo on 'Let's Get Lost' (Weimar Jazz Database), bars 9-11. A triplet cascade down the Dm7 (E-D-C-A-E), a walk through the G7, then up the 3rd-5th-7th of Cmaj7 resolving to a held G (the 5th). Chosen by ear."`

The section banner above it reads `CURATED VOCABULARY (picked by ear from real solos, Weimar Jazz DB) ... Exact transcribed notes; offsets = semitones from the I root. Built via tools/render_lick.py from chosen solo bars.` So the file itself labels L1 as an exact transcription, not a style-of line.

**Corroboration (three independent artifacts agree):**
1. **The engraved candidate `A4-lick-chet-9-11.png`** shows exactly this shape: a Dm7 triplet cascade (the "3" bracket, E-D-C…), a stepwise G7 descent, then an ascending Cmaj7 3-5-7 figure resolving to a held whole note — matching L1's `beats` (`_tt`/`ttt` triplets `n:[16,14]`,`[12,9,4]` over Dm7; the `[2,4,-3,0]` walk over G7; `[4,7,11]` up Cmaj7; held `[7]`) and the lore note-for-note.
2. **`A4-WJAZZ-CANDIDATES.json`** contains real WJazzD entries for `"perf": "Chet Baker" / "title": "Let's Get Lost"` (melid 72), confirming the source data is a genuine recorded-solo transcription, not an invented line.
3. **The lore explicitly says "Chosen by ear"** — the human-pick step the approaches log credits.

**Conclusion:** L1 is a verbatim (pitch-level, rhythm-quantized-to-grid) transcription of Chet Baker's recorded solo, human-selected. It is **not** a style-of/device-cited adaptation.

## (c) Which doc is right / where each is wrong

| Doc | Verdict | Detail |
|-----|---------|--------|
| **`A4-VOCAB-APPROACHES.md`** | **Correct** | Lines 8 & 18 accurately describe L1 as the locked Chet Baker "Let's Get Lost" bars 9–11 pick installed in `index.html` `LICKS`. No change needed. |
| **`TRANSCRIPTION-POSTMORTEM.md`** | **Correct** (already self-flags) | §6 & the "Discrepancy to note" callout correctly identify L1 as the Chet Baker pick and already carry `[confirm: current identity of L1 in index.html]`. This brief resolves that confirm. |
| **`A4-VOCAB-BRIEF.md`** | **Wrong about L1** | §(b), the parenthetical *"This matches how L1–L5 were already handled (they cite the device, not a specific recording)"* is factually incorrect for L1 (and presumes an L2–L5 that aren't in the live `LICKS` array). The brief's own pack — L11–L21 in `A4-VOCAB-PACK.js` — genuinely *is* style-of/adapted, and that part is fine; only its claim about the **pre-existing** L1 is false. |

**Important secondary finding — a third, conflicting L1 also exists on disk.** `A4-REAL-LICKS.js` defines a *different* `L1` = **"Confirmation (bridge ii-V-I)" — Charlie Parker, Real Book p.87**, in an array (`A4_REAL_LICKS`) whose header says it *"Replaces the synthetic L1–L10 in index.html's LICKS array."* This is an **unmerged proposal file**, not what ships — `index.html` does not import it (no reference to `A4_REAL_LICKS` exists in `index.html`). It is a live source of confusion: anyone reading `A4-REAL-LICKS.js` would conclude L1 is a Parker/Confirmation transcription. Flagged below.

## (d) Recommended canonical identity for L1 — and the exact edits to make docs consistent

> **Recommendation (for Chris — not executed):** Adopt the **shipped** definition as canonical: **L1 = "Chet Baker — Let's Get Lost," Weimar Jazz DB bars 9–11, an ear-picked note-level transcription.** It is what's actually in the app, it is corroborated by the engraving, the audio, and the WJazzD source row, and it is the one result the project explicitly "approved and locked." Make the docs match the app, not the other way around.

If Chris accepts that canonical identity, the minimal one-line edits each doc needs (DO NOT apply without his go-ahead; back up first):

- **`A4-VOCAB-BRIEF.md`, §(b)** — change the parenthetical
  `"This matches how L1–L5 were already handled (they cite the device, not a specific recording)"`
  → `"This matches how L6–L10 were handled (device-cited adaptations); note that L1, the shipped lick, is a genuine ear-picked transcription (Chet Baker, 'Let's Get Lost,' WJazzD bars 9–11), not a style-of line."`
- **`A4-REAL-LICKS.js`** — it is an unmerged alternative whose `L1`/header collide with the shipped `L1`. Recommended (Chris's call): either (i) rename its array IDs and drop the "Replaces … L1–L10" header so it can't be mistaken for the live data, or (ii) clearly mark the file `STATUS: UNMERGED PROPOSAL — not in index.html` at the top. **Defer-with-context:** if the real plan was to swap the WJazzD/Chet approach out for Real-Book transcriptions, that's a *content* decision (which is wrong proves nothing without his intent), not a doc-reconciliation fix — surface it, don't resolve it here.
- **`A4-VOCAB-APPROACHES.md` / `TRANSCRIPTION-POSTMORTEM.md`** — **no edits required**; they are already correct. The postmortem's `[confirm: current identity of L1 in index.html]` can be marked resolved by pointing to this brief.

## (e) Open `[confirm:]` items

- `[confirm: intent of A4-REAL-LICKS.js]` — Is the Parker/Confirmation `A4_REAL_LICKS` set meant to **replace** the shipped Chet L1, or was it an abandoned branch? Its header says "Replaces the synthetic L1–L10," but nothing imports it and the approaches log treats the Chet pick as the locked result. This is a content/direction call for Chris, not resolvable from the files alone.
- `[confirm: status of L2–L10]` — The live `LICKS` array contains **only L1**. The brief and postmortem both reference "L1–L10 already live in index.html," but they are not in the current array. Either they were removed, or "L1–L10" referred to an earlier state. Worth confirming what (if anything) should populate L2–L10.
- No `[confirm]` on L1's musical content itself — the stored notes, the engraved PNG, the lore, and the WJazzD candidate row are mutually consistent; L1's identity as the Chet Baker transcription is **not** ambiguous.

---

### Decision frame for Chris (resolve / defer / skip)
- **Resolve:** Confirm canonical L1 = the shipped Chet Baker transcription, and approve the one-line `A4-VOCAB-BRIEF.md` fix above.
- **Defer-with-context:** The `A4-REAL-LICKS.js` "replaces L1–L10" question (content direction) — flag what you'd want explored before deciding.
- **Skip:** Acceptable to leave the brief's wording as-is for now; the *app* is correct and unaffected. The only live risk is documentation drift, not shipped behavior.
