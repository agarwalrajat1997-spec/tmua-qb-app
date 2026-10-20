(function () {
  'use strict';

  /*
   * Parent contract:
   *   src="/{tmua|esat}-mini-test/index.html?embed=1&parentOrigin=<encoded origin>"
   *   child -> parent: { type: 'ts-mini-test-size', height, phase }
   *   parent -> child: { type: 'ts-mini-test-fullscreen', fullscreen: boolean }
   *
   * The parent must check event.source === iframe.contentWindow and the exact
   * apps origin before accepting size messages. No answers, scores or personal
   * details cross this bridge. Neither test functions nor storage are changed.
   */
  var params = new URLSearchParams(window.location.search);
  if (params.get('embed') !== '1' || window.parent === window) return;

  var allowedOrigins = new Set([
    'https://www.thrivingscholars.com',
    'https://thrivingscholars.com',
    'https://thriving-scholars-migration.raj1291241.chatgpt.site'
  ]);
  var localHosts = new Set(['localhost', '127.0.0.1', '[::1]']);
  var parentOrigin = params.get('parentOrigin');
  var parsedParent;
  try {
    parsedParent = new URL(parentOrigin);
  } catch (_) {
    return;
  }
  // Reject URLs with paths, credentials, hashes or deceptive host suffixes.
  if (!parentOrigin || parsedParent.origin !== parentOrigin) return;
  var localDevelopment = localHosts.has(window.location.hostname)
    && localHosts.has(parsedParent.hostname)
    && (parsedParent.protocol === 'http:' || parsedParent.protocol === 'https:');
  if (!allowedOrigins.has(parentOrigin) && !localDevelopment) return;
  // When supplied by the browser, the referrer must agree with the declared
  // parent. A no-referrer policy is supported; targetOrigin still stays exact.
  if (document.referrer) {
    try {
      if (new URL(document.referrer).origin !== parentOrigin) return;
    } catch (_) {
      return;
    }
  }

  var root = document.documentElement;
  var phases = ['landing', 'exam', 'transition', 'results'];
  var framePending = false;
  var lastHeight = null;
  var lastPhase = null;
  var isFullscreen = false;

  function currentPhase() {
    for (var index = 0; index < phases.length; index += 1) {
      var node = document.getElementById(phases[index]);
      if (node && !node.hidden) return phases[index];
    }
    return 'landing';
  }

  function publishSize() {
    framePending = false;
    var phase = currentPhase();
    var active = document.getElementById(phase);
    if (!active) return;
    // Measuring the active content rather than root.scrollHeight allows the
    // iframe to shrink after expanded results, avoiding a height feedback loop.
    var bottom = active.getBoundingClientRect().bottom + window.scrollY;
    var margin = parseFloat(window.getComputedStyle(active).marginBottom) || 0;
    var naturalHeight = isFullscreen ? window.innerHeight : bottom + margin + 2;
    if (!Number.isFinite(naturalHeight)) return;
    var height = Math.max(320, Math.min(30000, Math.ceil(naturalHeight)));
    if (lastPhase === phase && lastHeight !== null && Math.abs(height - lastHeight) <= 1) return;
    lastHeight = height;
    lastPhase = phase;
    window.parent.postMessage({
      type: 'ts-mini-test-size',
      height: height,
      phase: phase
    }, parentOrigin);
  }

  function scheduleSize() {
    if (framePending) return;
    framePending = true;
    window.requestAnimationFrame(publishSize);
  }

  function start() {
    root.classList.add('ts-mini-embedded');
    if (typeof ResizeObserver === 'function') {
      var resizeObserver = new ResizeObserver(scheduleSize);
      ['brandbar'].concat(phases).forEach(function (id) {
        var element = document.getElementById(id);
        if (element) resizeObserver.observe(element);
      });
    }
    if (typeof MutationObserver === 'function') {
      var mutationObserver = new MutationObserver(scheduleSize);
      mutationObserver.observe(document.body, {
        subtree: true,
        childList: true,
        characterData: true,
        attributes: true,
        attributeFilter: ['hidden', 'open', 'class', 'style', 'data-scheme']
      });
    }
    window.addEventListener('resize', scheduleSize);
    window.addEventListener('load', scheduleSize);
    window.addEventListener('pageshow', scheduleSize);
    document.addEventListener('toggle', scheduleSize, true);
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(scheduleSize).catch(function () {});
    }
    scheduleSize();
  }

  window.addEventListener('message', function (event) {
    if (event.source !== window.parent || event.origin !== parentOrigin) return;
    var data = event.data;
    if (!data || data.type !== 'ts-mini-test-fullscreen' || typeof data.fullscreen !== 'boolean') return;
    isFullscreen = data.fullscreen;
    root.classList.toggle('ts-mini-fullscreen', isFullscreen);
    scheduleSize();
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else {
    start();
  }
})();
