/* ============================================================================
 * Woodshed Lite — live vote board (Supabase, M0)
 * ----------------------------------------------------------------------------
 * Backs the #wsl-votes-slot board with real tallies from Supabase. Design notes:
 *   - SINGLE-SELECT: a browser has one live vote. Clicking a different option
 *     MOVES the vote (the cast_vote RPC upserts). We mirror that optimistically.
 *   - Public-safe by construction: only SUPABASE_URL + anon key ship here; the
 *     tables are RLS-locked and reached solely through two security-definer RPCs
 *     (get_vote_tallies, cast_vote). See supabase/migrations/0001_voting.sql.
 *   - Graceful: if the backend/keys are missing or unreachable, we leave the
 *     static fallback rows (names via copy.js, seed counts in shell.html) exactly
 *     as-is so the board never looks broken.
 *   - It updates the EXISTING .vote rows in place (keyed by data-option-id); it
 *     does not fight copy.js over labels — copy.js owns names/meta, we own counts.
 * ========================================================================== */
(function () {
  'use strict';

  var CFG = (window.WSL_CONFIG && window.WSL_CONFIG.funnel && window.WSL_CONFIG.funnel.votes) || {};
  var URL = CFG.supabaseUrl, KEY = CFG.supabaseAnonKey;
  var WRITE_IN = CFG.writeInOptionId || 'other';
  var LS_VOTER = 'woodshed_voter';   // per-browser identity (UUID)
  var LS_VOTED = 'woodshed_voted';   // the option_id this browser currently backs

  var slot = document.getElementById('wsl-votes-slot');
  if (!slot) return;

  // Not configured yet → keep the static fallback board, say why (quietly).
  if (!URL || !KEY || URL === 'TODO' || KEY === 'TODO') {
    console.warn('[woodshed-lite] votes: Supabase not configured (funnel.votes.supabaseUrl/anonKey) — showing fallback board.');
    return;
  }

  // ---- small helpers -------------------------------------------------------
  function voterHash() {
    var v = null;
    try { v = localStorage.getItem(LS_VOTER); } catch (e) {}
    if (!v) {
      v = (window.crypto && crypto.randomUUID) ? crypto.randomUUID()
        : 'v-' + Math.random().toString(36).slice(2) + Date.now().toString(36);
      try { localStorage.setItem(LS_VOTER, v); } catch (e) {}
    }
    return v;
  }
  function getVoted() { try { return localStorage.getItem(LS_VOTED); } catch (e) { return null; } }
  function setVoted(id) { try { id ? localStorage.setItem(LS_VOTED, id) : localStorage.removeItem(LS_VOTED); } catch (e) {} }
  function track(option) {
    try { if (typeof window.plausible === 'function') window.plausible('vote_cast', { props: { option: option } }); } catch (e) {}
  }
  function rowFor(id) { return slot.querySelector('.vote[data-option-id="' + (window.CSS && CSS.escape ? CSS.escape(id) : id) + '"]'); }

  // Load supabase-js (UMD) on demand — same async-safe spirit as the soundfont
  // loader in shell.html: a slow/blocked CDN never blocks first paint.
  function loadSb() {
    return new Promise(function (resolve, reject) {
      if (window.supabase && window.supabase.createClient) return resolve(window.supabase);
      var s = document.createElement('script');
      s.async = true;
      s.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.110.0/dist/umd/supabase.min.js';
      s.onload = function () {
        (window.supabase && window.supabase.createClient) ? resolve(window.supabase)
          : reject(new Error('supabase-js loaded but createClient missing'));
      };
      s.onerror = function () { reject(new Error('failed to load supabase-js')); };
      document.head.appendChild(s);
    });
  }

  var sb = null;          // supabase client
  var lastTallies = null; // last authoritative tallies (array of {option_id,label,meta,sort,count})

  // ---- rendering -----------------------------------------------------------
  // Update counts + bar widths in place, re-sort rows desc, mark lead + voted.
  function render(tallies) {
    if (!Array.isArray(tallies) || !tallies.length) return;
    lastTallies = tallies;
    var voted = getVoted();
    var max = tallies.reduce(function (m, t) { return Math.max(m, Number(t.count) || 0); }, 0);

    tallies.forEach(function (t) {
      var row = rowFor(t.option_id);
      if (!row) return;
      var n = row.querySelector('.up .n');
      var bar = row.querySelector('.vbar i');
      if (n) n.textContent = String(t.count);
      if (bar) bar.style.width = (max > 0 ? Math.round((Number(t.count) || 0) / max * 100) : 0) + '%';
      row.classList.toggle('voted', voted === t.option_id);
    });

    // Sort rows by count desc (stable on ties via sort field), re-append, and
    // keep the header first + the write-in form last.
    var container = slot.querySelector('.votes');
    if (!container) return;
    var byId = {};
    tallies.forEach(function (t) { byId[t.option_id] = t; });
    var rows = [].slice.call(container.querySelectorAll('.vote'));
    rows.sort(function (a, b) {
      var ta = byId[a.dataset.optionId] || {}, tb = byId[b.dataset.optionId] || {};
      return (Number(tb.count) || 0) - (Number(ta.count) || 0)
          || (Number(ta.sort) || 0) - (Number(tb.sort) || 0);
    });
    var form = container.querySelector('.vote-writein');
    rows.forEach(function (row, i) {
      row.classList.toggle('lead', i === 0);
      container.appendChild(row);
    });
    if (form) container.appendChild(form); // form stays at the bottom
  }

  // Optimistic single-select move: prev pick -1, new pick +1, repaint, then the
  // server response reconciles to the truth.
  function optimisticMove(newId) {
    if (!lastTallies) return;
    var prev = getVoted();
    if (prev === newId) return;
    var clone = lastTallies.map(function (t) {
      var c = Number(t.count) || 0;
      if (t.option_id === newId) c += 1;
      if (prev && t.option_id === prev) c = Math.max(0, c - 1);
      return { option_id: t.option_id, label: t.label, meta: t.meta, sort: t.sort, count: c };
    });
    setVoted(newId);
    render(clone);
  }

  // ---- casting -------------------------------------------------------------
  var inFlight = false;
  function cast(optionId, note) {
    if (inFlight) return;
    inFlight = true;
    optimisticMove(optionId);
    track(optionId);
    sb.rpc('cast_vote', { p_option_id: optionId, p_voter_hash: voterHash(), p_note: note || null })
      .then(function (res) {
        if (res.error) throw res.error;
        setVoted(optionId);
        if (res.data) render(res.data);
      })
      .catch(function (err) {
        console.warn('[woodshed-lite] cast_vote failed — keeping last state.', err && err.message ? err.message : err);
        // refetch to undo a bad optimistic move
        refresh();
      })
      .then(function () { inFlight = false; });
  }

  function refresh() {
    return sb.rpc('get_vote_tallies').then(function (res) {
      if (res.error) throw res.error;
      render(res.data);
    });
  }

  // ---- wiring --------------------------------------------------------------
  function wire() {
    // Each option row. The write-in ('other') reveals its text box instead of
    // casting immediately; every other row casts on click (move-vote).
    var form = slot.querySelector('.vote-writein');
    [].slice.call(slot.querySelectorAll('.vote')).forEach(function (row) {
      row.addEventListener('click', function () {
        var id = row.dataset.optionId;
        if (!id) return;
        if (id === WRITE_IN && form) {
          var show = form.hasAttribute('hidden');
          if (show) { form.removeAttribute('hidden'); var inp = form.querySelector('input'); if (inp) inp.focus(); }
          else { form.setAttribute('hidden', ''); }
          return;
        }
        if (form) form.setAttribute('hidden', '');
        cast(id, null);
      });
    });
    if (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var inp = form.querySelector('input');
        var note = inp ? inp.value.trim() : '';
        cast(WRITE_IN, note || null);
        if (inp) inp.value = '';
        form.setAttribute('hidden', '');
      });
    }
  }

  // ---- boot ----------------------------------------------------------------
  loadSb()
    .then(function (lib) {
      sb = lib.createClient(URL, KEY, { auth: { persistSession: false } });
      wire();
      return refresh();
    })
    .catch(function (err) {
      // Any failure → the static fallback board stays. Never throw into the page.
      console.warn('[woodshed-lite] votes offline — showing fallback board.', err && err.message ? err.message : err);
    });
})();
