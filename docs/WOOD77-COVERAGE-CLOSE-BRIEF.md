# wood-77 — Tune→Page-Image Coverage: Close-Out Brief

**Milestone:** M2  ·  **Date:** 2026-06-29  ·  **Owner:** Chris  ·  **Status:** 13 of 17 gaps closed; 4 residual (all by-design page:0), each with a recommendation below.

The Tune Vault rebuild grew the app's tune set but left `render_pages.py` / `page-manifest.json` behind, so the coverage verifier failed with 17 gaps. This run rendered every gap tune whose Real Book page was **visually verified against the actual PDF**, regenerated the manifest, and re-greened the safe-to-ship check. No guessing — the 4 remaining gaps are documented for your call.

---

## A. What I closed (13 tunes rendered — every page eyeballed in the real PDF)

Each printed page below was opened in `Real Book.pdf` (PDF page = printed − 1) and the title + composer were confirmed on the page before rendering. Zero mismatches.

| Tune | App id | Printed pg | Confirmed on page |
|------|--------|-----------:|-------------------|
| All Blues | allblues | 18 | "ALL BLUES — Miles Davis" |
| All of Me | allofme | 20 | "ALL OF ME — Simons/Marks" |
| Black Nile | blacknile | 48 | "BLACK NILE — Wayne Shorter" |
| Blue Monk | bluemonk | 52 | "BLUE MONK — Thelonious Monk" |
| Blues for Alice | bfalice | 55 | "BLUES FOR ALICE — Charlie Parker" |
| Cotton Tail | cottontail | 90 | "COTTON TAIL — Duke Ellington" |
| Daahoud | daahoud | 96 | "DAAHOUD — Clifford Brown" |
| Donna Lee | donnalee | 123 | "DONNA LEE — Charlie Parker" |
| Freddie Freeloader | freddie | 151 | "FREDDIE FREELOADER — Miles Davis" |
| The Girl from Ipanema | ipanema | 158 | "THE GIRL FROM IPANEMA — Jobim" |
| Joy Spring | joyspring | 229 | "JOY SPRING — Clifford Brown" |
| Lady Bird | ladybird | 235 | "LADY BIRD — Tadd Dameron" |
| So What | sowhat | 364 | "SO WHAT — Miles Davis" |

(Blues for Alice and Lady Bird, flagged "previously verified," were independently re-verified here and are correct.)

---

## B. Residual gaps — your call (4) — `[confirm:Chris]`

All four are `page:0` in the app **on purpose** — they aren't in your Real Book, so there's no RB page to render. No action is *required* to ship safely; these are product decisions, not bugs.

1. **Sandu** (`sandu`, page:0) — `[confirm:Chris]`
   App already points it at a dedicated lead-sheet image (`img:'sandu-lead-sheet.png'`, which exists at the app root) and notes "not in your Real Book." 
   **Recommendation:** leave as-is — it already has a real image source, just not via the Real Book manifest. Optionally bring `sandu-lead-sheet.png` under the manifest so the verifier counts it as covered. No RB render is possible or appropriate.

2. **Watermelon Man** (`watermelon`, page:0) — `[confirm:Chris]`
   ADD-12 batch; app explicitly says "Not in your Real Book; changes are the iReal grid." Plays from changes. 
   **Recommendation:** keep page:0 (intentional). If you want a visual, source a public-domain / iReal lead-sheet image; do **not** force a Real Book page.

3. **Summertime** (`summertime`, page:0) — `[confirm:Chris]`
   Same ADD-12 batch; "not in your Real Book — changes are the iReal grid, concert A minor." 
   **Recommendation:** keep page:0 (intentional), or attach an iReal image like Watermelon Man if you want a chart.

4. **"Autumn Leaves" page:0 flag** (`autumnlv`) — `[confirm:Chris]` *(verifier label artifact, not a real gap)*
   This is your requested **F-minor concert** version, deliberately page:0, and it already carries `page2:{page:39}` pointing at the book's concert-E-minor print. Autumn Leaves **is** covered at p.39 (rendered, in manifest). The verifier's heuristic just labels this page:0 entry "Autumn Leaves." 
   **Recommendation:** no action — this is working as designed. If you want the verifier to stop flagging it, the cleanest fix is a tiny verifier allow-list for intentional page:0 tunes (separate task — verifier is out of scope for wood-77's guardrails).

**Net:** none of the four needs a Real Book render. Decision is purely "leave page:0 as-is" vs. "attach a non-RB lead-sheet image" per tune.

---

## C. Verifier before / after

| Check | Before | After |
|-------|-------:|------:|
| `verify_tune_page_coverage.py` MISSING (gaps) | **17** | **4** (all page:0, above) |
| COVERED | 12 | **25** |
| Real Book images on disk | 25 | **38** (+13) |
| `verify_public_safe.py` | (n/a) | **PASS** — no PDF leak, manifest↔pages 2-way match |

No source PDF was copied into `public-assets/` (verified). The source Real Book PDF stays a read-only input.

---

## D. Root-cause note for wood-77's owner (recommended follow-up)

`render_pages.py`'s hardcoded `TUNES` table had **drifted** from the app's actual tune set — that drift is exactly what produced the 17 gaps. I appended the 13 verified tunes, but the generator is still a *manually-maintained mirror* of `index.html`, so it will drift again on the next Vault change.

**Recommendation (spin-off task):** make the app's tune list the single source of truth — have `render_pages.py` parse the `page:<N>` references straight out of `index.html` (its own docstring already claims it does this) instead of a parallel hardcoded table. That closes this class of gap permanently. I did **not** do this here — it's a generator redesign beyond this task's render-the-gaps scope.

---

## Files changed
- `public-assets/render_pages.py` — appended 13 verified tune rows to `TUNES`; added an idempotent skip-if-exists guard to `render()` (deterministic, output-identical; needed so a full regenerate of a 73 MB PDF completes the manifest write).
- `public-assets/page-manifest.json` — regenerated (40 → 53 entries).
- `public-assets/pages/` — 13 new `realbook-pNN-*.png` images.
- `WOOD77-COVERAGE-CLOSE-BRIEF.md` — this brief.

Backups `*.bak-20260629` left untouched.
