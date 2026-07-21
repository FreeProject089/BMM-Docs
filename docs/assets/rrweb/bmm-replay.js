/*
 * bmm-replay.js — inline player for BMM .bmmreplay session recordings.
 *
 * Embed in any page with:
 *   <div class="bmm-replay" data-src="../assets/replays/NAME.bmmreplay"
 *        data-title="What this shows"></div>
 *
 * A .bmmreplay is JSON: { bmmReplay, app, durationMs, events: [...], ... } where
 * `events` is a standard rrweb event array. We lazy-load the (often large) file
 * only when the reader clicks Play, then drive rrweb's Replayer with a minimal
 * control bar and auto-scale the recording to the container width.
 *
 * Depends on window.rrweb (rrweb.min.js) + rrweb.min.css, loaded from mkdocs.yml.
 */
(function () {
  'use strict';

  function fmt(ms) {
    const s = Math.max(0, Math.round(ms / 1000));
    const m = Math.floor(s / 60);
    return m + ':' + String(s % 60).padStart(2, '0');
  }

  function fit(host, wrapper, recW, recH) {
    // rrweb renders at the recording's native size; scale it to fit the host box.
    if (!recW) return;
    const byW = host.clientWidth / recW;
    const byH = recH && host.clientHeight ? host.clientHeight / recH : Infinity;
    const scale = Math.min(byW, byH);
    wrapper.style.transform = 'scale(' + scale + ')';
    wrapper.style.transformOrigin = 'top left';
  }

  function mount(el) {
    const src = el.getAttribute('data-src');
    if (!src) return;
    const title = el.getAttribute('data-title') || '';

    el.classList.add('bmm-replay-ready');
    el.innerHTML =
      '<div class="bmm-replay-poster">' +
        '<button type="button" class="bmm-replay-play" aria-label="Play recording">' +
          '<svg viewBox="0 0 24 24" width="26" height="26" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>' +
        '</button>' +
        (title ? '<div class="bmm-replay-title">' + title + '</div>' : '') +
        '<div class="bmm-replay-hint">Interactive session recording — click to play</div>' +
      '</div>';

    const poster = el.querySelector('.bmm-replay-poster');
    poster.querySelector('.bmm-replay-play').addEventListener('click', function () {
      if (!window.rrweb || !window.rrweb.Replayer) {
        poster.innerHTML = '<div class="bmm-replay-error">Replay engine not loaded.</div>';
        return;
      }
      poster.innerHTML = '<div class="bmm-replay-loading"><span class="bmm-replay-spin"></span>Loading recording…</div>';

      fetch(src).then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      }).then(function (data) {
        const events = Array.isArray(data) ? data : (data && data.events);
        if (!events || events.length < 2) throw new Error('no events');
        play(el, events, (data && data.regions) || []);
      }).catch(function (err) {
        poster.innerHTML = '<div class="bmm-replay-error">Could not load this recording (' +
          String(err.message || err) + ').</div>';
      });
    });
  }

  var ICON = {
    pause: '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M6 5h4v14H6zm8 0h4v14h-4z"/></svg>',
    play:  '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>',
    restart: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2v6h6"/><path d="M3.5 8a9 9 0 1 0 2.6-4.5L3 8"/></svg>',
    fs:    '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3M3 16v3a2 2 0 0 0 2 2h3m13-5v3a2 2 0 0 1-2 2h-3"/></svg>'
  };

  function play(el, events, regions) {
    el.innerHTML =
      '<div class="bmm-replay-stage"><div class="bmm-replay-mount"></div></div>' +
      '<div class="bmm-replay-bar">' +
        '<button type="button" class="bmm-replay-toggle" aria-label="Pause">' + ICON.pause + '</button>' +
        '<button type="button" class="bmm-replay-restart" aria-label="Restart">' + ICON.restart + '</button>' +
        '<input type="range" class="bmm-replay-seek" min="0" max="1000" value="0" aria-label="Seek">' +
        '<span class="bmm-replay-time">0:00</span>' +
        '<button type="button" class="bmm-replay-speed" aria-label="Playback speed">1&times;</button>' +
        '<button type="button" class="bmm-replay-fs" aria-label="Fullscreen">' + ICON.fs + '</button>' +
      '</div>';

    const stage = el.querySelector('.bmm-replay-stage');
    const mountEl = el.querySelector('.bmm-replay-mount');
    const toggle = el.querySelector('.bmm-replay-toggle');
    const restart = el.querySelector('.bmm-replay-restart');
    const speedBtn = el.querySelector('.bmm-replay-speed');
    const fsBtn = el.querySelector('.bmm-replay-fs');
    const seek = el.querySelector('.bmm-replay-seek');
    const timeEl = el.querySelector('.bmm-replay-time');

    const replayer = new window.rrweb.Replayer(events, {
      root: mountEl,
      speed: 1,
      skipInactive: true,   // fast-forward idle gaps — nicer for a doc demo
      showWarning: false,
      mouseTail: { strokeStyle: '#3b82f6', lineWidth: 3 }
    });

    const meta = replayer.getMetaData();
    const total = meta.totalTime || 1;
    timeEl.textContent = fmt(0) + ' / ' + fmt(total);

    // Native recording size → scale the rrweb wrapper to fit.
    const metaEvt = events.find(function (e) { return e.type === 4 && e.data && e.data.width; });
    const recW = metaEvt ? metaEvt.data.width : 0;
    const recH = metaEvt ? metaEvt.data.height : 0;
    const wrapper = mountEl.querySelector('.replayer-wrapper');

    // A recording made with the Replay Studio can carry a `regions` timeline — the moving
    // capture FRAME. When present we crop the viewport to the active region (scale it to fill
    // the stage width, translate to the region origin) and follow it over time; a CSS
    // transition glides the frame moves. No regions → the whole recording, exactly as before.
    const regs = (Array.isArray(regions) ? regions : [])
      .filter(function (r) { return r && r.rect && r.rect.w; })
      .sort(function (a, b) { return a.t - b.t; });
    const hasRegions = regs.length > 0;
    if (recW && recH && !hasRegions) stage.style.aspectRatio = recW + ' / ' + recH;
    if (hasRegions && wrapper) wrapper.style.transition = 'transform .35s ease';

    function activeIdx(t) { var i = -1; for (var k = 0; k < regs.length; k++) { if (regs[k].t <= t) i = k; else break; } return i; }
    function rectAt(t) { var i = activeIdx(t); return i >= 0 ? regs[i].rect : { x: 0, y: 0, w: recW, h: recH }; }
    function applyFit(t) {
      if (!wrapper) return;
      var rect = rectAt(t);
      if (!rect.w) return;
      var s = stage.clientWidth / rect.w;
      if (document.fullscreenElement === stage && rect.h) s = Math.min(s, stage.clientHeight / rect.h);
      wrapper.style.transformOrigin = 'top left';
      wrapper.style.transform = 'translate(' + (-rect.x * s) + 'px,' + (-rect.y * s) + 'px) scale(' + s + ')';
      if (hasRegions) stage.style.height = (rect.h * s) + 'px';
    }
    function refit() { applyFit(replayer.getCurrentTime()); }
    refit();
    window.addEventListener('resize', refit);
    // Refit on ANY container size change (sidebar toggle, font-zoom, reflow) — not just
    // window resizes — so the recording always fills the box without jumps.
    if (window.ResizeObserver) { var ro = new ResizeObserver(refit); ro.observe(stage); }

    replayer.play();
    let playing = true;
    function setPlaying(p) {
      playing = p;
      toggle.innerHTML = p ? ICON.pause : ICON.play;
      toggle.setAttribute('aria-label', p ? 'Pause' : 'Play');
    }

    toggle.addEventListener('click', function () {
      if (playing) replayer.pause();
      else replayer.play(replayer.getCurrentTime());
      setPlaying(!playing);
    });

    restart.addEventListener('click', function () {
      replayer.play(0);
      setPlaying(true);
    });

    // Speed cycle: 1 → 2 → 4 → 1
    const SPEEDS = [1, 2, 4];
    let si = 0;
    speedBtn.addEventListener('click', function () {
      si = (si + 1) % SPEEDS.length;
      const sp = SPEEDS[si];
      replayer.setConfig({ speed: sp });
      speedBtn.innerHTML = sp + '&times;';
    });

    // Fullscreen the stage; refit to the new size on enter/exit.
    fsBtn.addEventListener('click', function () {
      if (document.fullscreenElement) { document.exitFullscreen && document.exitFullscreen(); }
      else if (stage.requestFullscreen) { stage.requestFullscreen(); }
    });
    document.addEventListener('fullscreenchange', function () {
      // In fullscreen the stage fills the screen; recompute scale after layout settles.
      setTimeout(refit, 60);
    });

    let seeking = false;
    const wasPlaying = { v: false };
    seek.addEventListener('input', function () {
      // Live scrub: show the target time as you drag (rrweb only actually seeks on release,
      // which keeps dragging smooth instead of thrashing the Replayer on every pixel).
      if (!seeking) { wasPlaying.v = playing; }
      seeking = true;
      const t = (seek.value / 1000) * total;
      timeEl.textContent = fmt(t) + ' / ' + fmt(total);
    });
    seek.addEventListener('change', function () {
      const t = (seek.value / 1000) * total;
      // Resume from the new point if it was playing before the scrub; otherwise stay paused.
      if (wasPlaying.v) { replayer.play(t); setPlaying(true); }
      else { replayer.pause(t); setPlaying(false); }
      seeking = false;
    });

    var lastIdx = -2;
    (function tick() {
      if (!el.isConnected) return; // page changed
      const t = replayer.getCurrentTime();
      if (!seeking) {
        seek.value = String(Math.min(1000, Math.round((t / total) * 1000)));
        timeEl.textContent = fmt(t) + ' / ' + fmt(total);
      }
      // Follow the capture frame: re-fit only when the active region changes, so the CSS
      // transition animates the move (and we don't recompute layout every frame).
      if (hasRegions) { var i = activeIdx(t); if (i !== lastIdx) { lastIdx = i; applyFit(t); } }
      requestAnimationFrame(tick);
    })();

    replayer.on('finish', function () { setPlaying(false); });
  }

  function init() {
    document.querySelectorAll('.bmm-replay:not(.bmm-replay-ready)').forEach(mount);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  // MkDocs Material instant-loading swaps content without a full reload.
  if (window.document$ && typeof window.document$.subscribe === 'function') {
    window.document$.subscribe(init);
  }
})();
