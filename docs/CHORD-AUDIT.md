# Woodshed Chord Audit — band changes vs the Real Book
*Updated 2026-06-15 (corrected). Policy: the band should match the printed Real Book chart.*

## ⚠️ Correction to the first-pass audit
A first automated pass concluded "all 22 tunes are in the wrong key." **That conclusion was wrong** — it
compared the book's printed key directly against the app's `keyPc` without accounting for the edition.

**`Real Book.pdf` is the B♭ (trumpet) edition: every chart is written a whole step ABOVE concert pitch.**
Verified directly: Take the "A" Train (concert C) is printed in **D**; Straight No Chaser is printed in
**C** (= concert B♭). So the correct relationship is:

> **concert key (app `keyPc`) = book's written key − 2 semitones (a whole step down).**

Re-checked against that rule, the app's keys are essentially **correct**, by design (band plays concert;
the embedded page is the B♭ chart the player reads). No mass re-key is needed.

## Key verdicts (corrected)
- **21 of 22 tunes: KEY CORRECT** — app `keyPc` = written − 2. Examples: A Train (book D → concert C ✓),
  Blue Bossa (book Dm → Cm ✓), Misty (book F → E♭ ✓), Oleo (book C → B♭ ✓), Confirmation (book G → F ✓),
  Recorda Me (book Bm → Am ✓), Bessie's Blues (book F → E♭ ✓ — the "E♭ blues" title is correct).
- **Straight No Chaser (`blues`): GENUINE error — FIXED.** App had it in concert F; book prints written C
  = concert **B♭**. Corrected to `keyPc:10`, bars `B♭7/E♭7/B♭7/B♭7/E♭7/E♭7/B♭7/B♭7/F7/E♭7/B♭7/F7`, and the
  added jazz-blues ii-Vs removed to match the book's plain blues. (Title/hook updated.)
- **Autumn Leaves (`autumn`): RECHECK.** First pass read the page as F♯m; the app expects concert Gm →
  written **Am** (per the app's own note). Likely a misread of the key signature, but needs a 30-second
  visual recheck to confirm the app's Gm is right.

## Genuine to-dos (small, not a 22-tune re-key)
1. **`autumn`** — visually recheck the printed key (expect Am written / Gm concert).
2. **`solar` page reference** — first pass reports `page:365` lands on So What's overflow; Solar prints on
   **p.363**. Verify and fix the page number (display bug, not a chord bug).
3. **Changes-level audit (the real remaining value).** Separate from keys: does the band's *harmonization*
   match the book's *printed changes* (ignoring key)? Straight No Chaser proved the app sometimes adds
   ii-Vs / diminished chords the book doesn't print. This needs a careful per-tune pass comparing the
   progression in Roman numerals (key-independent) — the first pass could not do this reliably because it
   was distracted by the (non-)key issue. This is the worthwhile next sweep.

## Media caveat
The `vids[]` / `soloId` play-alongs are real recordings in their own keys; they were never guaranteed to
match the band. Only relevant where we actually change a key — i.e., Straight No Chaser (now concert B♭,
while the famous recordings are in F). Flag per-tune only when a key actually changes.

---

## Changes-level audit (2026-06-18 night-shift) — key-independent

**Method note.** Rendered each tune's actual Real Book page with `pdftoppm -r 150–280` (pdfPage =
printedPage − 1; book is the B♭/trumpet edition, written a whole step above concert) and read the
printed changes directly off the image. Compared the book's printed harmony, transposed **down a whole
step to concert**, against the app's CONCERT `bars[]`. Diffed for genuine ADD / DROP / SUBSTITUTE of
chords; ignored cosmetic extension/voicing differences (C7 vs C13, 7♭5 vs 7♯11, ♭9 vs ♯9, maj7 vs 6).
Where the engraving's melody crosses barlines and exact bar-alignment is ambiguous, marked `[confirm]`
rather than asserting. **No app code was edited — `bars[]` suggestions below are proposals only.**
All 24 tunes were read at the page; 24 audited (none left unread).

| Tune | id | printed p. | pdfPage | verdict | divergence (Roman-numeral, concert, 1 line) | suggested `bars[]` fix |
|------|----|-----------|---------|---------|---------------------------------------------|------------------------|
| Straight No Chaser | blues | 386 | 385 | ✓ | Plain B♭ blues; matches book after prior fix (verified vs p.386). | — |
| Autumn Leaves | autumn | 39 | 38 | **DIVERGES (KEY)** | Book prints concert **G major / E minor** (written A maj / F♯ minor, 3 sharps). App is concert **B♭ / G minor**. App ≠ book key, and the app's "written A minor" note is wrong. | see Fix #1 |
| Blue Bossa | bossa | 50 | 49 | **DIVERGES (minor)** | Book bar 4 = **♭VII7 (B♭7)**; app holds **iv (Fm7)**. App = the universal jam version; book prints KD's B♭7. | bar4 `['Bb7']` |
| Take the "A" Train | atrain | 398 | 397 | ✓ minor | Bridge: book holds V (G7) 2 bars; app splits to ii-V (Dm7 G7). Cosmetic. | — |
| All The Things You Are | attya | 22 | 21 | **DIVERGES (minor)** | Bar 16 (into bridge): book **V7/vi = E7♯5**; app **C7♯5** (wrong target). Also app adds ii's in bars 6 & 30 (cosmetic). | bar16 `['E7#5']` |
| Four | four | 149 | 148 | ✓ | Falling-minor-ii-V staircase matches book exactly. | — |
| Beautiful Love | beautiful | 40 | 39 | ✓ minor | App bar 14 has an extra G7♯11 not clearly in book; structure otherwise matches. | — |
| Solar | solar | **363** | 362 | ✓ (page# wrong) | Changes match book exactly. **`page:365` is wrong — Solar prints on p.363** (365 lands in So What overflow). | see Fix #2 (display only) |
| There Will Never Be Another You | twnbay | 407 | 406 | ✓ minor | Core E♭ changes match; final tag bars differ cosmetically from book's E7-A-7-D7 tag. | — |
| Oleo (Rhythm Changes) | oleo | 309 | 308 | ✓ minor | Book A bar 3 = I (B♭6); app = ii (Dm7). Book bar 6 = ♯iv-7→iv-6 (E-7 E♭-6); app = IV6→iv6 (E♭6 E♭m6). Both common rhythm-changes variants; bridge matches. | optional: bar3 `['Bb6','G7']` |
| Song for My Father | father | 373 | 372 | ✓ | Fm7–E♭7–D♭7–C7 downhill matches book (A and B). | — |
| Footprints | footprints | 144 | 143 | ✓ minor / [confirm] | Bars 9–12 slippery: book chord 3 = **iiø (E-7♭5)**, app = **dominant (E7♯9)**. The famously-ambiguous Miles bar; app documents the choice. | (leave; Chris's call) |
| Cherokee | cherokee | 77 | 76 | **DIVERGES (major)** | **Bridge starts on the wrong key.** Book bridge = ii-V-I down by whole steps **B→A→G→F** (concert). App does only **A→G→F** (missing the opening **B major** ii-V-I) — contradicts the app's own hook text. | see Fix #3 |
| Confirmation | confirmation | 87 | 86 | **[confirm]** | A-section bar 4: book appears to print **ii-V to ♭VII (Cm7 F7)**; app has **V7 (G7)**. Bar-alignment ambiguous in dense engraving; bridge matches. | confirm bar 4 → likely `['Cm7','F7']` |
| Misty | misty | 277 | 276 | ✓ minor | A/bridge match exactly; app adds an A♭7 backdoor in the final bars not in book. | — |
| Stella by Starlight | stella | 382 | 381 | ✓ | Reads bar-for-bar against book (only Ab7 vs Ab7♯11 extension diff). | — |
| There Is No Greater Love | tingl | 406 | 405 | **DIVERGES (minor)** | A-section bar 5: book = **V7/ii (C7 secondary dom)** → Cm7 F7; app = **ii (Cm7)**, dropping the C7. | bar5 `['C7']`, bar6 `['Cm7','F7']` |
| A Night in Tunisia | tunisia | 302 | 301 | **DIVERGES** | Bridge: (a) bar 17 book **♭vø (A♭m7♭5)**, app **Aø (Am7♭5)**; (b) bar 23 book **iv-6 (Fm6, minor)**, app **IV (Fmaj7, major)** — app turned a minor ii-V-i into a major one. A-section matches. | see Fix #4 |
| Ornithology | ornithology | 317 | 316 | **[confirm]** | Bars 13–16: book prints a **ii-V chain Bm7 E7 / Am7 D7** (concert); app has **Gmaj7 / Am7 D7** repeated. Form alignment ambiguous. | confirm bars 13–16 |
| Have You Met Miss Jones? | missjones | 172 | 171 | ✓ | Including the major-thirds bridge (B♭→G♭→D→G♭) — matches book. | — |
| Out of Nowhere | nowhere | 318 | 317 | ✓ minor / [confirm] | Signature B♭m7-E♭7 "from nowhere" (bar 3) + altered-dom shock present; some passing-chord diffs in dense bars 11-12/26. | confirm bars 11-12 |
| My Funny Valentine | valentine | 287 | 286 | ✓ minor | Descending minor-line A matches; 36-bar extended bridge/tag has minor passing-chord diffs (book Cm/B♭m7/A7 descent vs app simplification). | — |
| Recorda Me | recordame | 337 | 336 | ✓ | Matches book incl. the extended ii-V chain riding down to F major before E7 home (the app's prior correction is confirmed correct). | — |
| Bessie's Blues | bessies | 42 | 41 | **DIVERGES (minor)** | Book is a **plain E♭ blues** (I7 IV7 I7 I7 / IV7 IV7 I7 I7 / V7 IV7 I7 / V7). App **adds a turnaround** in bars 11-12 (E♭7 C7 / Fm7 B♭7) the book doesn't print — same pattern as Straight No Chaser. | bars 11-12 → `['Eb7'],['Bb7']` (plain) |

### Fix list for Chris (prioritized)

**P1 — real harmonic/key errors, worth fixing**

1. **Autumn Leaves (autumn) — KEY MISMATCH (decide first).**
   *What's wrong:* The app plays concert **B♭ major / G minor**; Real Book p.39 prints concert **G major /
   E minor** (written A major / F♯ minor, 3 sharps). The app's story/hook text claims the book is "written
   A minor" — that is factually wrong for this page. So app and book are in *different keys* (a minor third
   apart), and the player reading the embedded page will be in E minor while the band plays G minor.
   *Decision needed:* (a) re-key the band to match the book (concert E minor), OR (b) keep concert G minor
   (the most common *jam* key for Autumn Leaves) and fix the misleading text + swap the embedded page to a
   Gm/Am chart. This is a genuine player-facing conflict, not cosmetic.
   *If (a) — match book — corrected concert bars[] (E minor / G major):*
   ```
   bars:[['Am7'],['D7'],['Gmaj7'],['Cmaj7'],['F#m7b5'],['B7b9'],['Em6'],['Em6'],
         ['Am7'],['D7'],['Gmaj7'],['Cmaj7'],['F#m7b5'],['B7b9'],['Em6'],['Em6'],
         ['F#m7b5'],['B7b9'],['Em6'],['Em6'],['Am7'],['D7'],['Gmaj7'],['Cmaj7'],
         ['F#m7b5'],['B7b9'],['Em7','Eb7'],['Dm7','Db7'],['Cmaj7'],['B7b9'],['Em6'],['Em6']]
   ```
   and set `keyPc:4, minor:true`. *Confidence: high on the book read; the (a)/(b) choice is Chris's.*

2. **Cherokee (cherokee) — bridge is missing its first key center.**
   *What's wrong:* The bridge should descend by whole steps **B→A→G→F** (concert), four ii-V-I's, 4 bars
   each (the book prints exactly this on p.77). The app's bridge does only **A→G→F** plus a turnaround —
   it omits the opening **B major** ii-V-I and is shifted down a step. This even contradicts the app's own
   hook ("B to A to G to F").
   *Corrected concert bridge (replace the 16 bridge bars, the 3rd line of cherokee's `bars`):*
   ```
   ['Dbm7'],['Gb7'],['Bmaj7'],['Bmaj7'],['Bm7'],['E7'],['Amaj7'],['Amaj7'],
   ['Am7'],['D7'],['Gmaj7'],['Gmaj7'],['Gm7'],['C7'],['Fmaj7'],['Fmaj7'],
   ```
   *Confidence: high.*

3. **A Night in Tunisia (tunisia) — bridge quality/chord errors.**
   *What's wrong:* Book bridge (concert) is two descending minor ii-V-i's: **A♭ø D7 Gm6 / Gø C7 Fm6**, into
   Eø A7. The app has (a) **Am7♭5** where book has **A♭m7♭5** (bar 17), and (b) resolves the 2nd cell to
   **Fmaj7 (major)** where the book prints **Fm6 (minor, bar 23)**.
   *Corrected concert bridge (8 bars):*
   ```
   ['Abm7b5'],['D7b9'],['Gm6','D7b9'],['Gm6'],['Gm7b5'],['C7b9'],['Fm6'],['Em7b5','A7b9'],
   ```
   *Confidence: high read; note bar-17 A♭ø is the book's printed chord even though Aø is more "textbook."*

4. **All The Things You Are (attya) — bar 16 wrong dominant.**
   *What's wrong:* Bar 16 (the dominant pushing into the bridge's Am7) should be **E7♯5 (V7/vi)**; the app
   has **C7♯5**, which doesn't lead to Am7. *Fix:* bar 16 → `['E7#5']`. *Confidence: medium-high.*

5. **Bessie's Blues (bessies) — added turnaround the book doesn't print.**
   *What's wrong:* Book p.42 is a plain E♭ blues; the app adds **E♭7 C7 / Fm7 B♭7** in bars 11-12.
   Same issue already fixed on Straight No Chaser. *Fix:* bars 11-12 → `['Eb7'],['Bb7']` (or keep the
   added turnaround if Chris wants the jazz-blues flavor — a deliberate-divergence call). *Confidence: high.*

**P2 — minor divergences / display**

6. **Solar (solar) — page number only.** `page:365` is wrong; Solar prints on **p.363**. Set `page:363`.
   Changes themselves are correct. Display-only. *Confidence: high.*

7. **Blue Bossa (bossa) — book bar 4 = B♭7, app = Fm7.** The app's Fm7 is the near-universal jam version;
   the book prints B♭7. Match-the-book → bar 4 `['Bb7']`. Low priority (most players expect the app's
   version). *Confidence: high read; policy call.*

8. **There Is No Greater Love (tingl) — A bar 5 drops a secondary dominant.** Book bar 5 = C7 (V7/ii) →
   Cm7 F7; app collapses to Cm7. Optional fix: bar5 `['C7']`, bar6 `['Cm7','F7']`. *Confidence: high read.*

**[confirm] — RESOLVED 2026-06-23 (wood-26 sweep). Closer page reads below; see "§ [confirm] resolution".**

9. **Confirmation (confirmation)** — ✅ RESOLVED → **CONFIRMED divergence.** Book p.87 prints the **Cm7–F7 ii-V into B♭** the app omits. Fix: bar 3 → `['Dm7','G7']`, bar 4 → `['Cm7','F7']` (mirror at bars 11-12 & 27-28). Confidence: high.
10. **Ornithology (ornithology)** — ✅ RESOLVED → **CONFIRMED divergence.** Book p.317 bars 13–16 (written C#m7 F#7 Bm7 E7) = concert **Bm7 E7 Am7 D7**, a descending ii-V home to G; app repeats Gmaj7/Am7 D7. Fix: bars 13–16 → `['Bm7'],['E7'],['Am7'],['D7']`. Confidence: high.
11. **Out of Nowhere (nowhere)** — ✅ RESOLVED → **NO CHANGE.** App's bars 11-12 passing chords (Bm7-B♭dim7 / Am7-D7) are legit — the book prints that exact chromatic turnaround (written C#m7-Cdim7-Bm7-E7) in its closing bars. Cosmetic placement. Confidence: med-high.
12. **Footprints (footprints)** — ✅ RESOLVED → **APP IS BOOK-EXACT.** Book p.144 bars 9-10 (written G#m7♭5 G7♯11 / F#7♭5♯9 B7♭5♯9) = concert F#m7♭5 F7♯11 / E7♯9 A7♯9; bars 11-12 = Cm7. Book prints the **dominant**, not iiø — app's E7♯9 is correct. No fix. Confidence: high.

### What Chris should review/decide FIRST
1. **Autumn Leaves key** (Fix #1) — it's the only player-facing key conflict and needs a *decision*
   (re-key to E minor to match the book, vs keep G-minor jam key and fix the text/embedded page).
2. **Cherokee bridge** (Fix #2) — clear, mechanical, high-confidence fix; restores B→A→G→F.
3. Then the rest of P1 (Tunisia bridge, ATTYA bar 16, Bessie's turnaround) as a batch, and the trivial
   **Solar page:363** display fix.

---

## § [confirm] resolution (2026-06-23 night-shift sweep — wood-26)

**Method.** Re-rendered each tune's actual Real Book page at 250 dpi (`pdftoppm`, pdfPage = printed − 1;
B♭/trumpet edition, written a whole step above concert) and read the printed chords bar-by-bar off the
image, transposed down a whole step to concert, against the app's current `bars[]` in `index.html`.
All four prior `[confirm]` items are now resolved with a definite verdict. **No `index.html` code was
edited** — these fold into the wood-25 / wood-23 apply pass. 📍 Sources: `Real Book.pdf` pp.87, 317, 318,
144 (rendered crops archived under the sweep's report).

### 9. Confirmation (`confirmation`, p.87) — CONFIRMED divergence → FIX
- **Book read (written G major):** `G6 | F#m7♭5 | B7 | Em ‖ D-7 | G7 | C7 | B-7  E7` (A section, 8 bars).
- **Concert (−2):** `F6 | Em7♭5 | A7 | Dm ‖ Cm7 | F7 | B♭7 | Am7  D7`.
- **App now:** `F6 | Em7♭5 A7♭9 | Dm7 | G7 | B♭7 | Am7 D7 | Gm7 | C7`.
- **Finding:** the book contains the **Cm7→F7 ii-V into B♭** (a clean ii-V-I). The app has **no Cm7 or F7
  anywhere in the A section** — it goes `Dm7 | G7 | B♭7`, where `G7→B♭7` is non-functional. This is the
  standard Confirmation A section; the app's bar-4 `G7` is a genuine harmonic error, not a voicing nit.
- **Book-exact fix (app's compressed 8-bar grid):** bar 3 → `['Dm7','G7']`, bar 4 → `['Cm7','F7']`.
  The same A section recurs at bars 9-16 and 25-32, so apply the identical fix at **bars 3-4, 11-12, 27-28**.
  Bridge (bars 17-24) and bars 5-8 (`B♭7 | Am7 D7 | Gm7 | C7`) are fine — leave them.
- **Confidence:** high.

### 10. Ornithology (`ornithology`, p.317) — CONFIRMED divergence → FIX
- **Form note:** the book engraves Ornithology as a 16-bar form with **1st/2nd endings** (played twice =
  32). The app writes it out flat as 32 bars (`AB 32`). The A1 and the home-run climb read cleanly anyway.
- **Book read, bars 13-16 (written):** `C#m7 | F#7 | Bm7 | E7` → **concert `Bm7 | E7 | Am7 | D7`** —
  a descending ii-V chain (ii-V of A, then ii-V of G) walking home to G.
- **App now, bars 13-16:** `Gmaj7 | Am7 D7 | Gmaj7 | Am7 D7` — repeats the tonic/turnaround and **drops the
  Bm7-E7 ii-V**.
- **Book-exact fix (app grid):** bars 13-16 → `['Bm7'],['E7'],['Am7'],['D7']`.
- **Confidence:** high. **Caveat for wood-23:** the book's *2nd ending* adds a chromatic turnaround
  (written `C#m7 C°7 / B-7 B♭7` → concert `Bm7 B♭dim7 / Am7 A♭7`) that the app's flat 32-bar layout does
  not mirror. That's a separate form-structure question, not part of this `[confirm]`.

### 11. Out of Nowhere (`nowhere`, p.318) — RESOLVED → NO CHANGE
- **Book read (written A major):** bars 1-8 `Amaj7 | Amaj7 | C-7 | F7 | Amaj7 | Amaj7 | C#m7 | F#7` →
  concert `Gmaj7 | Gmaj7 | B♭m7 | E♭7 | Gmaj7 | Gmaj7 | Bm7 | E7` — **matches the app exactly**, including
  the signature `B♭m7-E♭7` "from nowhere" (bar 3) and `Bm7-E7` (bar 7).
- **bars 11-12 question:** the app's passing chords `Bm7 B♭dim7 / Am7 D7` are **legitimate book vocabulary** —
  the book itself prints exactly that chromatic descent (written `C#m7 C°7 / B-7 E7` → concert
  `Bm7 B♭dim7 / Am7 D7`) in its closing turnaround. The app relocates it as a passing reharm; harmonically
  sound, not an error.
- **Verdict:** ✓, no fix. The book's literal 1st-ending bars are simpler (`Am7 | Bm7♭5 E7 | Am7`); both
  are valid. Bar-26 alignment vs the book's repeat form is intrinsically fuzzy and acceptable as-is.
- **Confidence:** medium-high.

### 12. Footprints (`footprints`, p.144) — RESOLVED → APP IS BOOK-EXACT
- **Book read (written D minor, the slippery bars 9-10):** `G#m7♭5 | G7♯11 | F#7♭5(♯9) | B7♭5(♯9)`
  → **concert `F#m7♭5 | F7♯11 | E7♯9 | A7♯9`**; bars 11-12 = `D-7` → concert **`Cm7`**.
- **App now, bars 9-12:** `['F#m7b5','F7#11'] | ['E7#9','A7#9'] | ['Cm7'] | ['Cm7']` — **identical** to the
  book once transposed.
- **Finding:** the prior doubt ("book chord 3 = iiø `Em7♭5` vs app dominant `E7♯9`") resolves **in favor of
  the app** — the book prints a **dominant** (`F#7♭5♯9` written = concert `E7♭5♯9 ≈ E7♯9`), not a iiø. The
  app's story note ("F♯ø→F7♯11→E7♯9→A7♯9 … Verified p.144") is correct.
- **Verdict:** ✓ book-exact, no fix.
- **Confidence:** high.

### Net for wood-25 / wood-23 apply
- **2 real fixes to apply:** Confirmation (bars 3-4, 11-12, 27-28 → `Dm7 G7` / `Cm7 F7`) and Ornithology
  (bars 13-16 → `Bm7 / E7 / Am7 / D7`). Both high-confidence, book-exact, mechanical.
- **2 cleared as correct/cosmetic:** Out of Nowhere (no change) and Footprints (already book-exact) — drop
  their `[confirm]` flags. No remaining `[confirm]` items in this audit.
