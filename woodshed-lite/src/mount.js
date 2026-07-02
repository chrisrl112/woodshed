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

  // A bar with N chords splits its 4 beats N-ways (matches the engine's own
  // comping convention for dense bars — see compBar's "wood-24" split). Render
  // each chord as its own sub-cell with its own slash count ("G // F- //"),
  // not one merged label sitting above a single unrelated 4-slash row.
  function renderBarHTML(bar, idx, semis) {
    const num = `<span class="num">${idx + 1}</span>`;
    if (bar.length === 1) {
      const { root, sup } = splitChordForCard(bar[0], semis);
      return `<div class="bar" data-bar="${idx}">${num}<span class="chord">${root}${sup ? `<sup>${sup}</sup>` : ''}</span><span class="slash">/ / / /</span></div>`;
    }
    const beatsEach = Math.max(1, Math.round(4 / bar.length));
    const slashMini = Array(beatsEach).fill('/').join(' ');
    const cells = bar.map(sym => {
      const { root, sup } = splitChordForCard(sym, semis);
      return `<div class="bar-split-cell"><span class="chord">${root}${sup ? `<sup>${sup}</sup>` : ''}</span><span class="slash-mini">${slashMini}</span></div>`;
    }).join('');
    return `<div class="bar bar-split" data-bar="${idx}">${num}<div class="bar-split-row">${cells}</div></div>`;
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

  // ── Warmup Station: real engraving (Clarke Second Study Ex. 27–28) ────────
  // Strip ABCJS's own T: title line — it renders in ABCJS's default title font,
  // which clashes with the brand type system. The branded "Ex. 27 · G major"
  // labels in shell.html (data-copy="warmup.clarke_ex27_label" etc.) replace it.
  const clarkeLine1 = document.querySelector('#clarke-line-1');
  const clarkeLine2 = document.querySelector('#clarke-line-2');
  if (clarkeLine1 && window.CLARKE_WARMUPS) {
    const ex27 = window.CLARKE_WARMUPS.find(w => w.id === 'clarke-2-ex27');
    const ex28 = window.CLARKE_WARMUPS.find(w => w.id === 'clarke-2-ex28');
    const stripTitle = abc => abc.replace(/^T:.*\n/m, '');
    if (ex27) renderABC(clarkeLine1, stripTitle(ex27.abc), 1.1, { responsive: 'resize' });
    if (ex28) renderABC(clarkeLine2, stripTitle(ex28.abc), 1.1, { responsive: 'resize' });
  }

  // ── Warmup Station (Clarke metronome) ──────────────────────────────────────
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

  if (warmupBpmInput) {
    const cfg = CFG.warmup;
    warmupBpmInput.min   = cfg.bpmMin;
    warmupBpmInput.max   = cfg.bpmMax;
    warmupBpmInput.value = cfg.defaultBpm;
    warmupBpmDisplay.textContent = cfg.defaultBpm;
    if (warmupTempoWord) warmupTempoWord.textContent = tempoMarking(cfg.defaultBpm);

    bindSlider(warmupBpmInput, warmupBpmFill, warmupBpmKnob, bpm => {
      warmupBpmDisplay.textContent = bpm;
      if (warmupTempoWord) warmupTempoWord.textContent = tempoMarking(bpm);
      if (Metro.playing) Metro.setBpm(bpm);
    });

    function setWarmupStatus(playing) {
      warmupStatusDots.forEach((d, i) => d.classList.toggle('on', playing ? i === 1 : i === 0));
    }
    setWarmupStatus(false);

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

  // ── Reps tracker (manual check-off — click a dot to mark reps complete up
  //    to that point; click the current boundary again to undo). Illustrative
  //    only — no persistence yet; "Log it" just confirms the moment. ────────
  const repsDotsEl  = document.querySelector('#warmup-reps-dots');
  const repsCountEl = document.querySelector('#warmup-reps-count');
  const warmupLogBtn = document.querySelector('#warmup-log-btn');
  const repsTotal   = CFG.warmup.reps;
  let repsCompleted = 0;

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
    repsCountEl.textContent = `${repsCompleted} / ${repsTotal}`;
    if (warmupLogBtn) warmupLogBtn.disabled = repsCompleted < repsTotal;
  }

  if (repsDotsEl) {
    repsDotsEl.addEventListener('click', e => {
      const idx = Number(e.target.dataset.idx);
      if (Number.isNaN(idx)) return;
      repsCompleted = (repsCompleted === idx + 1) ? idx : idx + 1;
      renderReps();
    });
    renderReps();
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

  // Initial load — prefer CFG.jam.default, fall back to the first resolved tune.
  if (jamTunes.length) {
    const startIdx = Math.max(0, jamTunes.findIndex(t => t.id === CFG.jam.default));
    loadTune(startIdx);
  } else {
    console.warn('[woodshed-lite] no jam tunes have chart data — Jam station has nothing to play.');
  }
})();
