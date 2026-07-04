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
   * A 3-exercise carousel (◀ ▶ arrows switch; the metronome default tempo +
   * range re-seed per exercise). All three are public domain. Entry shape
   * mirrors jam.tunes (config-driven, no fork):
   *   id        - stable id (carousel state / analytics)
   *   type      - 'abc'   → branded ABCJS engraving (Clarke, from
   *                         clarke-warmups-lite.js — MUST be your own engraving)
   *               'image' → a cropped PD engraving PNG in assets/warmups/
   *   label     - panel title
   *   badge     - panel sup badge (PD attribution)
   *   marking   - the staff-meta study line under the title
   *   src       - image path (type:'image' only; relative to the deploy root)
   *   defaultBpm / bpmMin / bpmMax - metronome seed when this exercise is active
   *   reps      - rep check-off target shown in the tracker
   * Clarke Technical Study is PD (1912); the two Arban studies are from the
   * 1893 Carl Fischer Arban (public domain). Clarke must stay YOUR engraving. */
  warmups: [
    {
      id: 'clarke-study-2', type: 'abc',
      label: 'Clarke · Second Study, Ex. 27–28',
      badge: 'PUBLIC DOMAIN · RE-ENGRAVED',
      marking: 'half=80–120 · Play legato at first, then very lightly single tongue',
      defaultBpm: 72, bpmMin: 40, bpmMax: 160, reps: 5,
    },
    {
      id: 'arban-slur-8', type: 'image',
      label: 'Arban · Studies on the Slur, No. 8',
      badge: 'PUBLIC DOMAIN · 1893',
      src: 'assets/warmups/arban-slur-08.png',
      marking: 'Slur throughout · full, even air — lip slurs climbing to the top of the staff',
      defaultBpm: 66, bpmMin: 40, bpmMax: 120, reps: 5,
    },
    {
      id: 'arban-first-3', type: 'image',
      label: 'Arban · First Studies, No. 3',
      badge: 'PUBLIC DOMAIN · 1893',
      src: 'assets/warmups/arban-first-studies-03.png',
      marking: 'Light single tongue · keep the interval leaps clean and connected',
      defaultBpm: 80, bpmMin: 40, bpmMax: 140, reps: 5,
    },
  ],

  /* ---- JAM STATION -------------------------------------------------------
   * PD lead sheets (melody shown — must be your engraving of a <=1930 tune)
   * + changes-only tunes (chords only — legal for ANY tune).
   * `default` is the tune the hero CTA cues up. Keep it a changes-only tune
   * for the cleanest instant-wow (no melody to read).
   * composer/year/descriptor/feel are display-only metadata (factual
   * attribution, not copyrighted content) — bars/key always come from
   * charts/charts-curated.js, looked up by label at mount time. */
  jam: {
    default: 'autumnlv',           // hero CTA lands here, pre-cued
    defaultBpm: 120,

    // Per tune: `bpm` (starting tempo), `groove` (drummer: swing|bossa|brushes)
    // and `compFeel` (piano feel: evans|garland|jamal) are the session defaults
    // applied when the tune loads. `feel` is the display descriptor in the list.
    tunes: [
      // Changes-only (chords, no melody) — legal for any tune. 'On the Sunny
      // Side of the Street' was dropped: it needs a PD-safe melody engraving
      // (type: 'leadsheet') that doesn't exist anywhere in charts/ yet — see
      // verify_public_safe.py. Re-add it once that engraving exists.
      { id: 'autumnlv', label: 'Autumn Leaves', type: 'changes',
        composer: 'Kosma / Mercer', year: 1945, descriptor: 'F MINOR', feel: 'MEDIUM SWING',
        bpm: 160, groove: 'swing', compFeel: 'garland' },
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
      provider: 'supabase',        // real backend — see woodshed-lite/supabase/migrations/0001_voting.sql
      // PUBLIC-SAFE keys only. The anon key is designed to ship in the browser
      // and is protected by RLS (tables are locked; only the two RPCs are
      // exec-grantable to anon). NEVER put the service_role key or DB password
      // here — those live in .env / .dev.vars, which .gitignore excludes.
      supabaseUrl:     'https://doavobhtmetfmugpjgrt.supabase.co',  // Project URL           (Project Settings → API)
      supabaseAnonKey: 'sb_publishable_bzn1Lmjxalxac0J9AAOtgA_0v-QoLya',  // publishable/anon key  (Project Settings → API)
      model: 'single-select',      // one vote per browser total; casting again MOVES the vote
      // Option ids MUST match vote_options.id in the migration + the
      // data-option-id attributes in shell.html. Order here is the fallback
      // display order used only when the backend is unreachable.
      options: ['full_warmup', 'byo_session', 'track_progress', 'other'],
      writeInOptionId: 'other',    // this option reveals a free-text box (stored as votes.note)
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
