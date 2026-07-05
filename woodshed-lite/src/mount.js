// Woodshed Lite — station mounting
// Runs after engine.js + charts-curated.js + clarke-warmups-lite.js + drums-manifest.js.
// Depends on globals from engine.js (Band, Metro, DrumLoop, pretty, transposeSym,
// renderABC — chordChartHTML is NOT used here, this design renders its own chart-card
// markup, see renderBarHTML below), window.USER_CHARTS (charts-curated.js),
// window.CLARKE_WARMUPS (clarke-warmups-lite.js), window.WSL_CONFIG (lite.config.js).
// S and saveState() are defined as global stubs in shell.html <head>.
(function () {
  'use strict';

  const CFG = window.WSL_CONFIG;

  // Set by initMobileConsole(); lets the carousel re-seed the mobile tempo too.
  let mcSyncBpm = () => {};

  // ── iOS/Safari WebAudio unlock ─────────────────────────────────────────────
  // On iOS Safari (and to a lesser degree Android Chrome) an AudioContext stays
  // muted until it is BOTH resumed AND has actually started a buffer inside a
  // real user gesture. AC.get() only calls resume() — so the metronome/band
  // could stay silent for the whole session even though every later call looks
  // fine. Fix: on the very FIRST pointer/touch/key anywhere on the page (the
  // hero button, a scroll-tap, whatever comes before Play), resume the context
  // AND play one silent sample. After that the context is "running" and every
  // later sound — even one that starts after an await (drum decode) — plays.
  // Capture-phase + once, so it never interferes with the app's own handlers.
  (function installAudioUnlock() {
    if (typeof AC === 'undefined') return;
    // Declare a media ("playback") audio session up front so iOS doesn't mute
    // our Web Audio in silent mode (see AC.get() in the engine for the why).
    try { if (navigator.audioSession) navigator.audioSession.type = 'playback'; } catch (e) {}
    const EVENTS = ['pointerdown', 'touchend', 'mousedown', 'keydown'];
    let done = false;
    function unlock() {
      if (done) return;
      try {
        const ctx = AC.get();                 // creates the context + resume(), synchronously in the gesture
        if (ctx.state === 'suspended') ctx.resume();
        const buf = ctx.createBuffer(1, 1, 22050);   // 1-sample silent buffer
        const src = ctx.createBufferSource();
        src.buffer = buf; src.connect(ctx.destination); src.start(0);
        if (ctx.state === 'running') done = true;
      } catch (e) { /* try again on the next gesture */ }
      if (done) EVENTS.forEach(ev => document.removeEventListener(ev, unlock, true));
    }
    EVENTS.forEach(ev => document.addEventListener(ev, unlock, true));
  })();

  // ── helpers ──────────────────────────────────────────────────────────────

  // Resolve a config tune {id, label, type, composer, year, descriptor, feel}
  // into one carrying real bars/key from charts/ (single source of truth —
  // see lite.config.js's no-fork contract). Tunes with no chart data are
  // dropped rather than faked.
  function resolveTune(t) {
    const charted = (window.USER_CHARTS || []).find(
      c => (c.title || '').toLowerCase() === t.label.toLowerCase()
    );
    if (!charted || !charted.bars) return null;
    return Object.assign({}, t, {
      bars: charted.bars,
      key:  charted.key || '',
      bpm:  t.bpm || CFG.jam.defaultBpm,
      // groove / compFeel ride along from the config tune (Object.assign spread)
      groove:   t.groove   || 'swing',
      compFeel: t.compFeel || (CFG.jam.feels && CFG.jam.feels[0]) || 'evans',
    });
  }

  // "Bb7" -> {root:"B♭", sup:"7"} using the engine's own chord-symbol prettifier.
  // `semis` transposes the symbol first (0 = concert pitch, as written in charts/).
  function splitChordForCard(sym, semis) {
    const t = semis ? transposeSym(sym, semis) : sym;
    const p = pretty(t);
    const m = p.match(/^([A-G][♭♯]?)(.*)$/);
    return m ? { root: m[1], sup: m[2] } : { root: p, sup: '' };
  }

  // Every bar — single- or multi-chord — renders the same two-row structure so
  // the chord label can never collide with the slash marks (the old single-chord
  // path absolutely-positioned the slashes bottom-right, which overlapped the
  // chord text on narrow bars). Row 1: one left-justified chord cell per chord
  // (flex:1 each — a 2-chord bar just adds a second cell, e.g. "G  F-"). Row 2:
  // a full-width strip of slash marks per chord, each matching its share of the
  // measure ("/ / / /" for one chord; "/ /" + "/ /" for two). Font autofits via
  // clamp() + a .bar-multi modifier so dense bars shrink instead of overflowing.
  function renderBarHTML(bar, idx, semis) {
    const num = `<span class="num">${idx + 1}</span>`;
    const n = bar.length;
    const beatsEach = Math.max(1, Math.round(4 / n));
    const slashStrip = Array(beatsEach).fill('/').join(' ');
    const chordCells = bar.map(sym => {
      const { root, sup } = splitChordForCard(sym, semis);
      return `<span class="chord">${root}${sup ? `<sup>${sup}</sup>` : ''}</span>`;
    }).join('');
    const slashCells = bar.map(() => `<span class="slash-cell">${slashStrip}</span>`).join('');
    return `<div class="bar${n > 1 ? ' bar-multi' : ''}" data-bar="${idx}">${num}<div class="bar-chords">${chordCells}</div><div class="bar-slashes">${slashCells}</div></div>`;
  }

  // "Bb (concert)" -> "B♭"; "Dm (concert)" -> "D MINOR". `semis` transposes the
  // tonic first (0 = concert, as read off charts/ — e.g. 2 for Bb instruments).
  function transposeKeyLabel(rawKey, semis) {
    const stripped = (rawKey || '').replace(/\s*\(concert\)/i, '').trim();
    const minor = /m$/.test(stripped);
    const root = minor ? stripped.slice(0, -1) : stripped;
    const shifted = semis ? transposeSym(root, semis) : root;
    return pretty(shifted) + (minor ? ' MINOR' : '');
  }

  // Standard Italian tempo markings by BPM range.
  function tempoMarking(bpm) {
    if (bpm < 60)  return 'Largo';
    if (bpm < 66)  return 'Larghetto';
    if (bpm < 76)  return 'Adagio';
    if (bpm < 108) return 'Andante';
    if (bpm < 120) return 'Moderato';
    if (bpm < 168) return 'Allegro';
    if (bpm < 200) return 'Vivace';
    return 'Presto';
  }

  // Overlay a real <input type=range> on a decorative .slider (.fill/.knob).
  // Returns a sync() you can call to re-paint the fill/knob from input.value.
  function bindSlider(input, fillEl, knobEl, onChange) {
    function sync() {
      const min = Number(input.min), max = Number(input.max), val = Number(input.value);
      const pct = max > min ? ((val - min) / (max - min)) * 100 : 0;
      fillEl.style.width = pct + '%';
      knobEl.style.left = pct + '%';
    }
    input.addEventListener('input', () => { sync(); onChange(Number(input.value)); });
    sync();
    return sync;
  }

  // ── Warmup Station: 3-exercise carousel ───────────────────────────────────
  // Clarke (branded ABCJS engraving) + two public-domain Arban studies (cropped
  // engraving images). ◀ ▶ swap the active slide and re-seed the metronome
  // default/range + reps. Config: CFG.warmups[] (see lite.config.js). ABCJS's
  // own T: title line is stripped from the Clarke ABC so the branded HTML
  // labels in shell.html carry the naming.
  const WARMUPS = (CFG.warmups && CFG.warmups.length) ? CFG.warmups : [];

  const clarkeHost = document.querySelector('#clarke-lines');
  let clarkeRendered = false;
  function renderClarke() {
    if (clarkeRendered || !clarkeHost || !window.CLARKE_WARMUPS) return;
    const stripTitle = abc => abc.replace(/^T:.*\n/m, '');
    // The ABC has a hard newline before the final whole-note bar, which ABCJS
    // treats as a forced system break. Collapse the music body onto one source
    // line (layout only, notes untouched) so each exercise renders as ONE line —
    // its 4 melodic bars + the tonic whole-note resolution — matching Chris's
    // "each a full line ending in a whole note".
    const oneSystem = abc => {
      const lines = abc.split('\n');
      const k = lines.findIndex(l => /^K:/.test(l));
      if (k < 0) return abc;
      const body = lines.slice(k + 1).join(' ').replace(/\s+/g, ' ').trim();
      return lines.slice(0, k + 1).join('\n') + '\n' + body + '\n';
    };
    // Render every Clarke Second Study exercise (Ex. 27–32) as one full line so
    // the stacked lines fill the screen. staffwidth:800 forces a single system
    // that responsive:'resize' scales to the container width.
    const list = window.CLARKE_WARMUPS;
    clarkeHost.innerHTML = '';
    list.forEach((ex, i) => {
      const lab = document.createElement('div');
      lab.className = 'clarke-ex-lab';
      lab.textContent = ex.id.replace(/^.*ex/i, 'Ex. ') + ' · ' + (ex.keyLabel || ex.key);
      clarkeHost.appendChild(lab);
      const line = document.createElement('div');
      line.className = 'clarke-line';
      clarkeHost.appendChild(line);
      renderABC(line, oneSystem(stripTitle(ex.abc)), 1.1,
        { responsive: 'resize', measuresPerLine: 8, staffwidth: 800, paddingtop: 2, paddingbottom: 4 });
      if (i < list.length - 1) {
        const dv = document.createElement('div'); dv.className = 'divline'; clarkeHost.appendChild(dv);
      }
    });
    clarkeRendered = true;
  }

  // ── Warmup metronome elements ─────────────────────────────────────────────
  const warmupBpmInput   = document.querySelector('#warmup-bpm');
  const warmupBpmDisplay = document.querySelector('#warmup-bpm-display');
  const warmupBpmFill    = document.querySelector('#warmup-bpm-fill');
  const warmupBpmKnob    = document.querySelector('#warmup-bpm-knob');
  const warmupTempoWord  = document.querySelector('#warmup-tempo-word');
  const warmupPlay       = document.querySelector('#warmup-play');
  const warmupPlayIcon   = document.querySelector('#warmup-play-icon');
  const warmupPlayLabel  = document.querySelector('#warmup-play-label');
  const warmupStatusDots = document.querySelectorAll('#warmup-status-dots i');
  const warmupSubdivSeg  = document.querySelector('#warmup-subdiv-seg');

  // Overlay the real range input on the decorative slider; keep the returned
  // sync() so the carousel can repaint the fill/knob after a BPM re-seed.
  let syncWarmupSlider = () => {};
  if (warmupBpmInput) {
    syncWarmupSlider = bindSlider(warmupBpmInput, warmupBpmFill, warmupBpmKnob, bpm => {
      warmupBpmDisplay.textContent = bpm;
      if (warmupTempoWord) warmupTempoWord.textContent = tempoMarking(bpm);
      if (Metro.playing) Metro.setBpm(bpm);
    });
  }

  // ── Reps tracker (manual check-off — click a dot to mark reps complete up to
  //    that point; click the current boundary again to undo). Illustrative only
  //    — no persistence. repsTotal re-seeds per exercise (generic across all
  //    three unless a warmups[] entry sets a different `reps`). ──────────────
  const repsDotsEl   = document.querySelector('#warmup-reps-dots');
  const repsCountEl   = document.querySelector('#warmup-reps-count');
  const warmupLogBtn  = document.querySelector('#warmup-log-btn');
  let repsTotal      = (WARMUPS[0] && WARMUPS[0].reps) || 5;
  let repsCompleted  = 0;

  function renderReps() {
    if (!repsDotsEl) return;
    repsDotsEl.innerHTML = '';
    for (let i = 0; i < repsTotal; i++) {
      const dot = document.createElement('i');
      if (i < repsCompleted) dot.className = 'done';
      else if (i === repsCompleted) dot.className = 'cur';
      dot.dataset.idx = i;
      repsDotsEl.appendChild(dot);
    }
    if (repsCountEl) repsCountEl.textContent = `${repsCompleted} / ${repsTotal}`;
    if (warmupLogBtn) warmupLogBtn.disabled = repsCompleted < repsTotal;
  }

  // ── Carousel state + render ───────────────────────────────────────────────
  const exTitle     = document.querySelector('#warmup-ex-title');
  const exBadge     = document.querySelector('#warmup-ex-badge');
  const exCount     = document.querySelector('#warmup-ex-count');
  const exMarking   = document.querySelector('#clarke-tempo-marking');
  const exStaffMeta = document.querySelector('#warmup .staff-meta');
  const abcSlide    = document.querySelector('#warmup-abc-slide');
  const imgSlide    = document.querySelector('#warmup-image-slide');
  const warmupImg   = document.querySelector('#warmup-image');
  const exPrev      = document.querySelector('#warmup-ex-prev');
  const exNext      = document.querySelector('#warmup-ex-next');
  let activeWarmup  = 0;

  function renderWarmup(idx) {
    if (!WARMUPS.length) return;
    const n = WARMUPS.length;
    activeWarmup = ((idx % n) + n) % n;
    const w = WARMUPS[activeWarmup];

    if (exTitle)   exTitle.textContent   = w.label   || '';
    if (exBadge)   exBadge.textContent   = w.badge   || '';
    if (exMarking) exMarking.textContent = w.marking || '';
    if (exCount)   exCount.textContent   = `${activeWarmup + 1} / ${n}`;

    const isImg = w.type === 'image';
    if (abcSlide) abcSlide.hidden = isImg;
    if (imgSlide) imgSlide.hidden = !isImg;
    // The Arban crops carry their own clef/metre; drop the HTML clef+ts glyphs
    // (cut-time C) on image slides so they don't sit above a common-time crop.
    if (exStaffMeta) exStaffMeta.classList.toggle('no-glyph', isImg);

    if (isImg) {
      if (warmupImg) { warmupImg.src = w.src || ''; warmupImg.alt = w.label || ''; }
    } else {
      renderClarke();
    }

    // Re-seed the metronome default + range for this exercise.
    if (warmupBpmInput) {
      if (w.bpmMin != null) warmupBpmInput.min = w.bpmMin;
      if (w.bpmMax != null) warmupBpmInput.max = w.bpmMax;
      const bpm = w.defaultBpm != null ? w.defaultBpm : Number(warmupBpmInput.value);
      warmupBpmInput.value = bpm;
      if (warmupBpmDisplay) warmupBpmDisplay.textContent = bpm;
      if (warmupTempoWord)  warmupTempoWord.textContent = tempoMarking(bpm);
      syncWarmupSlider();
      mcSyncBpm(bpm, w.bpmMin, w.bpmMax);   // keep the mobile console's tempo in sync
      if (Metro.playing) Metro.setBpm(bpm);
    }

    // Fresh rep count for the new exercise.
    repsTotal = w.reps || repsTotal;
    repsCompleted = 0;
    renderReps();
  }

  if (exPrev) exPrev.addEventListener('click', () => renderWarmup(activeWarmup - 1));
  if (exNext) exNext.addEventListener('click', () => renderWarmup(activeWarmup + 1));

  // ── Metronome status + play/stop ──────────────────────────────────────────
  function setWarmupStatus(playing) {
    warmupStatusDots.forEach((d, i) => d.classList.toggle('on', playing ? i === 1 : i === 0));
  }
  setWarmupStatus(false);

  if (warmupPlay && warmupBpmInput) {
    warmupPlay.onclick = () => {
      if (Metro.playing) {
        Metro.stop();
        warmupPlay.removeAttribute('data-state');
        warmupPlayIcon.textContent  = '▶';
        warmupPlayLabel.textContent = 'Start Metronome';
        setWarmupStatus(false);
      } else {
        Metro.setBpm(Number(warmupBpmInput.value));
        Metro.start();
        // Kick off the 5-minute practice block on first metronome start — like
        // starting the clock at the top of a real session.
        if (window.__wslStartPracticeTimer) window.__wslStartPracticeTimer();
        warmupPlay.dataset.state    = 'playing';
        warmupPlayIcon.textContent  = '■';
        warmupPlayLabel.textContent = 'Stop';
        setWarmupStatus(true);
      }
    };
  }

  // Click subdivision: quarter / eighth / beats-2-&-4-only (real engine features —
  // Metro.subdiv and Metro.mode24, see engine.js's Metro._schedule()).
  if (warmupSubdivSeg) {
    warmupSubdivSeg.addEventListener('click', e => {
      const btn = e.target.closest('button[data-subdiv]');
      if (!btn) return;
      warmupSubdivSeg.querySelectorAll('button').forEach(b => b.classList.toggle('on', b === btn));
      if (btn.dataset.subdiv === '24') {
        Metro.mode24 = true;
      } else {
        Metro.mode24 = false;
        Metro.subdiv = Number(btn.dataset.subdiv);
      }
    });
  }

  if (repsDotsEl) {
    repsDotsEl.addEventListener('click', e => {
      const idx = Number(e.target.dataset.idx);
      if (Number.isNaN(idx)) return;
      repsCompleted = (repsCompleted === idx + 1) ? idx : idx + 1;
      renderReps();
    });
  }

  if (warmupLogBtn) {
    const original = warmupLogBtn.innerHTML;
    warmupLogBtn.addEventListener('click', () => {
      if (warmupLogBtn.disabled) return;
      warmupLogBtn.innerHTML = '<span class="tri">✓</span> Logged in the Woodshed';
      warmupLogBtn.dataset.state = 'playing';
      setTimeout(() => {
        warmupLogBtn.innerHTML = original;
        warmupLogBtn.removeAttribute('data-state');
      }, 1800);
    });
  }

  // Initial carousel paint (also seeds the metronome + reps for exercise 1).
  renderWarmup(0);

  // ── Practice-block timer (5-minute countdown) ──────────────────────────────
  // A branded session clock above the Clarke study. Starts on its own button or
  // automatically when the warmup metronome first starts. No persistence — it's
  // a live practice aid, reset each visit.
  (function initPracticeTimer() {
    const clockEl   = document.querySelector('#ptimer-clock');
    const toggleEl  = document.querySelector('#ptimer-toggle');
    const resetEl   = document.querySelector('#ptimer-reset');
    const fillEl    = document.querySelector('#ptimer-fill');
    const timerCard = document.querySelector('#practice-timer');
    if (!clockEl || !toggleEl) return;

    const TOTAL = 5 * 60; // seconds
    let remaining = TOTAL;
    let ticking = null;

    const fmt = s => Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
    function paint() {
      clockEl.textContent = fmt(remaining);
      if (fillEl) fillEl.style.width = (remaining / TOTAL * 100) + '%';
    }
    function label(run) {
      toggleEl.textContent = run ? 'Pause' : (remaining < TOTAL ? 'Resume' : 'Start');
    }
    function stopTick() { if (ticking) { clearInterval(ticking); ticking = null; } }
    function tick() {
      remaining = Math.max(0, remaining - 1);
      paint();
      if (remaining === 0) {
        stopTick();
        if (timerCard) timerCard.classList.add('done');
        clockEl.textContent = 'Done';
        label(false);
        if (typeof toast === 'function') toast('⏱ Practice block done — nice work');
      }
    }
    function start() {
      if (ticking || remaining === 0) return;
      if (timerCard) timerCard.classList.remove('done');
      ticking = setInterval(tick, 1000);
      label(true);
    }
    function pause() { stopTick(); label(false); }
    function reset() {
      stopTick();
      remaining = TOTAL;
      if (timerCard) timerCard.classList.remove('done');
      paint();
      label(false);
    }

    toggleEl.addEventListener('click', () => (ticking ? pause() : start()));
    if (resetEl) resetEl.addEventListener('click', reset);
    paint();
    label(false);

    // Let the warmup metronome auto-start the block on first press.
    window.__wslStartPracticeTimer = start;
  })();

  // ── Jam Station ────────────────────────────────────────────────────────────
  const jamTuneListEl   = document.querySelector('#jam-tune-list');
  const jamTuneNameEl   = document.querySelector('#jam-tune-name');
  const jamTuneByEl     = document.querySelector('#jam-tune-by');
  const jamKeyEl        = document.querySelector('#jam-key');
  const jamChartEl      = document.querySelector('#jam-chart');
  const jamPlay         = document.querySelector('#jam-play');
  const jamBpmInput     = document.querySelector('#jam-bpm');
  const jamBpmDisplay   = document.querySelector('#jam-bpm-display');
  const jamBpmFill      = document.querySelector('#jam-bpm-fill');
  const jamBpmKnob      = document.querySelector('#jam-bpm-knob');
  const jamFeelSeg      = document.querySelector('#jam-feel-seg');
  const jamDrummerSeg   = document.querySelector('#jam-drummer-seg');
  const jamTransposeSeg = document.querySelector('#jam-transpose-seg');

  // Resolve the allowlist down to tunes that actually have chart data.
  const jamTunes = [];
  CFG.jam.tunes.forEach(t => {
    const resolved = resolveTune(t);
    if (resolved) jamTunes.push(resolved);
    else console.warn('[woodshed-lite] no chart data for:', t.label);
  });

  let currentTune       = null;
  let currentTuneIdx    = -1;
  let currentFeel       = CFG.jam.feels[0] || 'evans';
  let currentGroove     = 'swing';
  let currentTranspose  = 0;  // semitones from concert pitch (0=C, 2=Bb, 9=Eb)
  let currentPlayingBar = -1; // -1 = not playing; kept so a transpose click mid-play can restore the highlight
  let bandPlaying       = false;

  // A Drummer groove nudges Feel to a sensible pairing (still overridable —
  // clicking Feel afterward wins, same "auto but overridable" pattern the
  // main Woodshed app uses for CompFeel.auto()/choices).
  const GROOVE_DEFAULT_FEEL = { swing: 'garland', bossa: 'evans', brushes: 'jamal' };

  function setFeel(feel) {
    currentFeel = feel;
    if (jamFeelSeg) {
      jamFeelSeg.querySelectorAll('button').forEach(b => b.classList.toggle('on', b.dataset.feel === feel));
    }
  }

  // Set the drummer groove + reflect it in the segmented control WITHOUT
  // touching Feel (loadTune sets Feel explicitly per tune; the drummer-click
  // handler adds the auto-Feel nudge on top of this).
  function setGroove(groove) {
    currentGroove = groove;
    if (jamDrummerSeg) {
      jamDrummerSeg.querySelectorAll('button').forEach(b => b.classList.toggle('on', b.dataset.groove === groove));
    }
  }

  function renderTuneList() {
    if (!jamTuneListEl) return;
    jamTuneListEl.innerHTML = jamTunes.map((t, i) => `
      <button class="tune${i === currentTuneIdx ? ' active' : ''}${i === currentTuneIdx && bandPlaying ? ' playing' : ''}" data-idx="${i}">
        <span class="idx">${String(i + 1).padStart(2, '0')}</span>
        <span class="tn"><span class="name">${t.label}</span><span class="meta">${t.descriptor} · ${t.bars.length} BARS · ${t.feel}</span></span>
        <span class="eq"><span></span><span></span><span></span><span></span></span>
      </button>
    `).join('');
  }

  function updateKeyBadge() {
    if (jamKeyEl && currentTune) {
      jamKeyEl.textContent = `KEY OF ${transposeKeyLabel(currentTune.key, currentTranspose)} · ♩=${jamBpmInput.value}`;
    }
  }

  function renderChart() {
    if (jamChartEl && currentTune) {
      jamChartEl.innerHTML = currentTune.bars.map((bar, i) => renderBarHTML(bar, i, currentTranspose)).join('');
    }
  }

  const syncJamSlider = jamBpmInput
    ? bindSlider(jamBpmInput, jamBpmFill, jamBpmKnob, bpm => {
        jamBpmDisplay.innerHTML = `${bpm} <small>BPM</small>`;
        updateKeyBadge();
      })
    : () => {};

  function loadTune(idx) {
    if (bandPlaying) stopBand();
    currentTuneIdx = idx;
    currentTune = jamTunes[idx];
    if (jamTuneNameEl) jamTuneNameEl.textContent = currentTune.label;
    if (jamTuneByEl) jamTuneByEl.textContent = `${currentTune.composer} · ${currentTune.year}`;
    if (jamBpmInput) {
      jamBpmInput.min   = CFG.jam.tempoRange[0];
      jamBpmInput.max   = CFG.jam.tempoRange[1];
      jamBpmInput.value = currentTune.bpm;
      jamBpmDisplay.innerHTML = `${currentTune.bpm} <small>BPM</small>`;
      syncJamSlider();
    }
    // Apply this tune's session defaults (drummer groove + comping feel).
    setGroove(currentTune.groove || 'swing');
    setFeel(currentTune.compFeel || currentFeel);
    updateKeyBadge();
    renderChart();
    renderTuneList();
  }

  function stopBand() {
    Band.stop();
    bandPlaying = false;
    currentPlayingBar = -1;
    if (jamPlay) {
      jamPlay.removeAttribute('data-state');
      jamPlay.textContent = '▶';
    }
    document.querySelectorAll('#jam-chart .bar').forEach(el => el.classList.remove('play'));
    renderTuneList();
  }

  if (jamTuneListEl) {
    jamTuneListEl.addEventListener('click', e => {
      const btn = e.target.closest('.tune');
      if (btn) loadTune(Number(btn.dataset.idx));
    });
  }

  if (jamTransposeSeg) {
    jamTransposeSeg.addEventListener('click', e => {
      const btn = e.target.closest('button[data-transpose]');
      if (!btn) return;
      currentTranspose = Number(btn.dataset.transpose);
      jamTransposeSeg.querySelectorAll('button').forEach(b => b.classList.toggle('on', b === btn));
      updateKeyBadge();
      renderChart();
      if (bandPlaying && currentPlayingBar >= 0) {
        // renderChart() just rebuilt the bar elements — restore the playhead highlight
        document.querySelectorAll('#jam-chart .bar').forEach((el, i) =>
          el.classList.toggle('play', i === currentPlayingBar));
      }
    });
  }

  if (jamDrummerSeg) {
    jamDrummerSeg.addEventListener('click', e => {
      const btn = e.target.closest('button[data-groove]');
      if (!btn) return;
      setGroove(btn.dataset.groove);
      setFeel(GROOVE_DEFAULT_FEEL[currentGroove] || 'evans');
    });
  }

  if (jamFeelSeg) {
    jamFeelSeg.addEventListener('click', e => {
      const btn = e.target.closest('button[data-feel]');
      if (btn) setFeel(btn.dataset.feel);
    });
  }

  if (jamPlay) {
    jamPlay.onclick = async () => {
      if (bandPlaying) { stopBand(); return; }
      if (!currentTune) return;

      const bpm = Number(jamBpmInput.value);

      // The engine's Band has no 'brushes' style — "Brushes" is a soft-swing
      // feel whose signature is the recorded brush loop, so the synth bass/comp
      // ride on the 'swing' style while we force the brush drum recording.
      const bandStyle = (currentGroove === 'brushes') ? 'swing' : currentGroove;

      // Pick the drum recording: for Brushes, force the nearest brushed track so
      // it's audibly distinct from ride-cymbal swing; otherwise let DrumLoop
      // auto-pick the best match for the (style, bpm) and fall back to synth.
      if (typeof DrumLoop !== 'undefined') {
        if (currentGroove === 'brushes') {
          const brush = (window.DRUM_TRACKS || [])
            .filter(t => /^brushes/i.test(t.id))
            .sort((a, b) => Math.abs(a.bpm - bpm) - Math.abs(b.bpm - bpm))[0];
          DrumLoop.setChoice(currentTune.id, brush ? brush.id : 'auto');
        } else {
          DrumLoop.setChoice(currentTune.id, 'auto');
        }
      }

      bandPlaying = true;
      jamPlay.dataset.state = 'playing';
      jamPlay.textContent = '■';
      renderTuneList();

      // Arm the real recorded drum loop for this groove/tempo (falls back to
      // the synth kit automatically if drums-manifest.js / the audio didn't
      // load — see DrumLoop.prep/whenReady in engine.js).
      if (typeof DrumLoop !== 'undefined') {
        DrumLoop.prep(currentTune.id, bandStyle, bpm);
        await DrumLoop.whenReady(DrumLoop.resolve(currentTune.id, bandStyle, bpm));
      }
      if (!bandPlaying) return; // stopped while we were awaiting the drum/sample load

      Band.play(currentTune.bars, {
        bpm,
        choruses:  2,
        style:     bandStyle,
        countIn:   true,
        compFeel:  currentFeel,
        onBar: bar => {
          currentPlayingBar = bar;
          document.querySelectorAll('#jam-chart .bar').forEach((el, i) =>
            el.classList.toggle('play', i === bar));
        },
        onDone: stopBand,
      });
    };
  }

  // Mobile: the gear reveals the band-config drawer (transpose / drummer / feel)
  // so the chord chart owns the screen. Toggles .cfg-open on the chart card; the
  // ≤760px CSS shows/hides the drawer. On desktop the gear is hidden and the
  // controls are always inline.
  const jamGear = document.querySelector('#jam-gear');
  const jamChartcard = document.querySelector('.chartcard');
  if (jamGear && jamChartcard) {
    jamGear.addEventListener('click', () => {
      const open = jamChartcard.classList.toggle('cfg-open');
      jamGear.setAttribute('aria-expanded', String(open));
    });
  }

  // Initial load — prefer CFG.jam.default, fall back to the first resolved tune.
  if (jamTunes.length) {
    const startIdx = Math.max(0, jamTunes.findIndex(t => t.id === CFG.jam.default));
    loadTune(startIdx);
  } else {
    console.warn('[woodshed-lite] no jam tunes have chart data — Jam station has nothing to play.');
  }

  // ── Mobile practice console (≤760px) ───────────────────────────────────────
  // A compact top bar that replaces the three stacked warmup panels on phones:
  // a countdown timer (tap to start/stop), a "72 BPM" chip (tap to start/stop
  // the metronome — same Metro engine as desktop), and a gear that reveals
  // tempo + click + a Streaks toggle. Streaks (off by default) reveals a reps
  // counter. Shares warmupBpmInput as the tempo source of truth so the exercise
  // carousel re-seeds it too (see mcSyncBpm above).
  (function initMobileConsole() {
    const $ = id => document.getElementById(id);
    const timerBtn = $('mc-timer-toggle');
    if (!timerBtn) return;               // console markup absent — nothing to wire
    const tico = $('mc-tico'), timeEl = $('mc-time');
    const bpmBtn = $('mc-bpm-toggle'), bpmIco = $('mc-bpm-ico'), bpmVal = $('mc-bpm-val');
    const gear = $('mc-gear'), config = $('mc-config');
    const range = $('mc-bpm-range'), rangeVal = $('mc-bpm-range-val'), subdivSeg = $('mc-subdiv-seg');
    const streakToggle = $('mc-streak-toggle'), streak = $('mc-streak');
    const repsCountEl = $('mc-reps-count'), repsDotsEl = $('mc-reps-dots'), logBtn = $('mc-log');

    // — practice-block countdown (independent 5-minute timer) —
    const TOTAL = 5 * 60;
    let remaining = TOTAL, ticking = null;
    const fmt = s => Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
    const paintTimer = () => { timeEl.textContent = fmt(remaining); };
    function stopTimer() {
      clearInterval(ticking); ticking = null;
      timerBtn.classList.remove('on'); tico.textContent = '▶';
      if (remaining <= 0) { remaining = TOTAL; paintTimer(); }
    }
    function startTimer() {
      if (ticking) return;
      timerBtn.classList.add('on'); tico.textContent = '■';
      ticking = setInterval(() => { remaining = Math.max(0, remaining - 1); paintTimer(); if (remaining === 0) stopTimer(); }, 1000);
    }
    timerBtn.onclick = () => (ticking ? stopTimer() : startTimer());

    // — metronome (shares Metro + warmupBpmInput with desktop) —
    const curBpm = () => Number(warmupBpmInput ? warmupBpmInput.value : range.value) || 72;
    function paintBpm() {
      const b = curBpm();
      bpmVal.textContent = b;
      if (range) range.value = b;
      if (rangeVal) rangeVal.textContent = b;
    }
    function metroOn()  { Metro.setBpm(curBpm()); Metro.start(); bpmBtn.classList.add('on'); bpmIco.textContent = '■'; }
    function metroOff() { Metro.stop(); bpmBtn.classList.remove('on'); bpmIco.textContent = '▶'; }
    bpmBtn.onclick = () => (Metro.playing ? metroOff() : metroOn());

    // — gear reveals the config drawer —
    gear.onclick = () => {
      config.hidden = !config.hidden;
      gear.setAttribute('aria-expanded', String(!config.hidden));
    };

    // — tempo slider (writes through to the shared source of truth) —
    if (range) range.addEventListener('input', () => {
      const b = Number(range.value);
      if (warmupBpmInput) warmupBpmInput.value = b;
      if (warmupBpmDisplay) warmupBpmDisplay.textContent = b;
      bpmVal.textContent = b;
      if (rangeVal) rangeVal.textContent = b;
      syncWarmupSlider();
      if (Metro.playing) Metro.setBpm(b);
    });

    // — click subdivision (same Metro flags as the desktop seg) —
    if (subdivSeg) subdivSeg.addEventListener('click', e => {
      const btn = e.target.closest('button[data-subdiv]');
      if (!btn) return;
      subdivSeg.querySelectorAll('button').forEach(b => b.classList.toggle('on', b === btn));
      if (btn.dataset.subdiv === '24') { Metro.mode24 = true; }
      else { Metro.mode24 = false; Metro.subdiv = Number(btn.dataset.subdiv); }
    });

    // — streaks toggle reveals the reps counter —
    let repsTotal = 5, repsDone = 0;
    function renderReps() {
      repsDotsEl.innerHTML = '';
      for (let i = 0; i < repsTotal; i++) {
        const d = document.createElement('i');
        if (i < repsDone) d.className = 'done';
        else if (i === repsDone) d.className = 'cur';
        d.dataset.idx = i;
        repsDotsEl.appendChild(d);
      }
      repsCountEl.textContent = repsDone + ' / ' + repsTotal;
      if (logBtn) logBtn.disabled = repsDone < repsTotal;
    }
    streakToggle.addEventListener('click', () => {
      const turningOn = streak.hidden;
      streak.hidden = !turningOn;
      streakToggle.setAttribute('aria-checked', String(turningOn));
      streakToggle.textContent = turningOn ? 'On' : 'Off';
      if (turningOn) renderReps();
    });
    repsDotsEl.addEventListener('click', e => {
      const idx = Number(e.target.dataset.idx);
      if (Number.isNaN(idx)) return;
      repsDone = (repsDone === idx + 1) ? idx : idx + 1;
      renderReps();
    });

    // — sync hook the exercise carousel calls when it re-seeds the tempo —
    mcSyncBpm = (bpm, min, max) => {
      if (range) { if (min != null) range.min = min; if (max != null) range.max = max; }
      if (bpm != null) { bpmVal.textContent = bpm; if (range) range.value = bpm; if (rangeVal) rangeVal.textContent = bpm; }
    };

    paintTimer();
    paintBpm();
  })();
})();
