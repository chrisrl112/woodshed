/* ============================================================================
 * Woodshed Lite — configuration
 * ----------------------------------------------------------------------------
 * THIS is the hand-maintained surface of Lite (besides the landing copy).
 * It is an ALLOWLIST + a few knobs. It does NOT contain engine code or chart
 * data — only references (by id) to tunes that already live in ../charts/.
 *
 * No-fork contract: to add a tune to Lite, add it to the Woodshed first
 * (charts/), then list its id here. Data has one source. See ../docs/woodshed-lite-spec.md
 * ========================================================================== */

window.WSL_CONFIG = {

  /* ---- WARMUP STATION ----------------------------------------------------
   * One re-engraved public-domain exercise. Clarke Technical Study II is PD
   * (1912) and the most-recognized trumpet warmup. Must be YOUR engraving —
   * never a scanned modern (Carl Fischer) edition. */
  warmup: {
    id: 'clarke-study-2',          // must exist in charts/ (re-engrave via score-to-woodshed)
    label: 'Clarke — Technical Study II',
    defaultBpm: 72,
    bpmMin: 40,
    bpmMax: 160,
    reps: 5,                       // rep check-off target shown in the tracker
  },

  /* ---- JAM STATION -------------------------------------------------------
   * PD lead sheets (melody shown — must be your engraving of a <=1930 tune)
   * + changes-only tunes (chords only — legal for ANY tune).
   * `default` is the tune the hero CTA cues up. Keep it a changes-only tune
   * for the cleanest instant-wow (no melody to read).
   * composer/year/descriptor/feel are display-only metadata (factual
   * attribution, not copyrighted content) — bars/key always come from
   * charts/charts-curated.js, looked up by label at mount time. */
  jam: {
    default: 'blue-monk',          // hero CTA lands here, pre-cued
    defaultBpm: 120,

    // Per tune: `bpm` (starting tempo), `groove` (drummer: swing|bossa|brushes)
    // and `compFeel` (piano feel: evans|garland|jamal) are the session defaults
    // applied when the tune loads. `feel` is the display descriptor in the list.
    tunes: [
      // Changes-only (chords, no melody) — legal for any tune. 'On the Sunny
      // Side of the Street' was dropped: it needs a PD-safe melody engraving
      // (type: 'leadsheet') that doesn't exist anywhere in charts/ yet — see
      // verify_public_safe.py. Re-add it once that engraving exists.
      { id: 'blue-monk', label: 'Blue Monk', type: 'changes',
        composer: 'Thelonious Monk', year: 1954, descriptor: 'B♭ BLUES', feel: 'MEDIUM SWING',
        bpm: 130, groove: 'swing', compFeel: 'garland' },
      { id: 'blue-bossa', label: 'Blue Bossa', type: 'changes',
        composer: 'Kenny Dorham', year: 1963, descriptor: 'C MINOR', feel: 'BOSSA NOVA',
        bpm: 160, groove: 'bossa', compFeel: 'evans' },
      { id: 'solar', label: 'Solar', type: 'changes',
        composer: 'Miles Davis', year: 1954, descriptor: 'C MINOR', feel: 'BRUSHED SWING',
        bpm: 150, groove: 'brushes', compFeel: 'jamal' },
    ],

    // Toggles surfaced in the Jam station UI (all powered by the shared engine):
    feels:  ['evans', 'garland', 'jamal'],   // CompFeel presets shown in the UI (evans default)
    styles: ['swing', 'bossa', 'brushes', 'ballad'],   // Band styles (brushes = soft swing)
    showDrumsToggle: true,
    tempoRange: [60, 240],
  },

  /* ---- FUNNEL ------------------------------------------------------------
   * Hosted embeds only — no backend. Swapping providers is a one-line change. */
  funnel: {
    waitlist: {
      provider: 'mailerlite',
      account: '2481736',
      formId:  '191733298141070717',
    },
    votes: {
      provider: 'canny',           // 'canny' | 'featurebase'
      embedId:  'TODO',
      // Seed these so the board is never blank (see spec §6):
      seeds: [
        'More tunes (which ones?)',
        'Build-your-own session (warmup → tunes → cooldown)',  // the consolidation probe
        'Loop a section (woodshed a hard 4 bars)',
        'More warmup exercises (Clarke/Arban library)',
        'Slow-down trainer (gradual tempo bump)',
        'Save your practice streak / log',
        'Mobile app version',
      ],
    },
    founder: {
      enabled: false,              // STUB until M3 (Phase 2). Don't charge during M0–M2.
      provider: 'stripe',          // 'stripe' | 'lemonsqueezy' | 'gumroad'
      linkUrl:  'TODO',
      pitch:    'First 30 founding members: $3/mo locked for life + name on the wall.',
    },
  },

  /* ---- ANALYTICS ---------------------------------------------------------
   * Events the funnel ladder depends on (spec §6). The mount wires these. */
  analytics: {
    provider: 'plausible',         // 'plausible' | 'ga4'
    domain:   'TODO',              // your deployed domain
    events: ['page_view','demo_play','metronome_start','feel_toggle','tempo_change','waitlist_submit','vote_cast','tiktok_click'],
  },

  /* ---- SOCIALS (footer) -------------------------------------------------- */
  socials: {
    tiktok:    'TODO',
    instagram: 'TODO',
    youtube:   'TODO',
  },
};
