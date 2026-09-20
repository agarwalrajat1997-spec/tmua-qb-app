/* TS_QB_COMPACT_PROGRESS_V2: persist changed answers, never duplicate full histories. */
(function () {
  "use strict";
  function object(x) { return !!x && typeof x === "object" && !Array.isArray(x); }
  function parse(raw) { try { return JSON.parse(raw); } catch (_) { return null; } }
  function compact(value) {
    if (!object(value)) return {};
    var state = Object.assign({}, value);
    if (object(state.answers)) {
      state.answers = {};
      Object.keys(value.answers).forEach(function (key) {
        if (["__proto__", "constructor", "prototype"].indexOf(key) >= 0 || !object(value.answers[key])) return;
        state.answers[key] = Object.assign({}, value.answers[key]);
        delete state.answers[key].solution_html;
      });
    }
    return state;
  }
  function equal(a, b) { return JSON.stringify(a) === JSON.stringify(b); }
  function merge(base, patch) {
    return Object.assign({}, base, patch, { answers: Object.assign({}, base.answers || {}, patch.answers || {}) });
  }
  function delta(base, state) {
    var patch = {};
    Object.keys(state).forEach(function (key) {
      if (["__proto__", "constructor", "prototype"].indexOf(key) >= 0) return;
      if (key !== "answers") { if (!equal(base[key], state[key])) patch[key] = state[key]; return; }
      Object.keys(state.answers || {}).forEach(function (qid) {
        if (!equal((base.answers || {})[qid], state.answers[qid])) {
          if (!patch.answers) patch.answers = {};
          patch.answers[qid] = state.answers[qid];
        }
      });
    });
    return patch;
  }
  function legacyHash(str) {
    var h = 0;
    for (var i = 0; i < str.length; i++) { h = ((h << 5) - h) + str.charCodeAt(i); h |= 0; }
    return String(h) + ":" + str.length;
  }
  function start(product, key) {
    var originalSet = Storage.prototype.setItem;
    var ackKey = key + "__compact_ack_v2";
    var pendingKey = key + "__pending_delta_v2";
    var localRaw = localStorage.getItem(key) || "";
    var observed = compact(parse(localRaw));
    var ack = parse(localStorage.getItem(ackKey));
    var pending = mergePatch(ack ? delta(ack, observed) : {}, parse(localStorage.getItem(pendingKey)) || {});
    var inFlightPatch = {};
    var initial = observed;
    var loaded = false;
    var busy = false;
    var timer;
    var failures = 0;
    var lastPull = 0;
    function read() { return compact(parse(localStorage.getItem(key))); }
    function dirty() { return Object.keys(pending).length > 0; }
    function persistAck() { originalSet.call(localStorage, ackKey, JSON.stringify(ack || {})); }
    function persistPending() { originalSet.call(localStorage, pendingKey, JSON.stringify(mergePatch(inFlightPatch, pending))); }
    function capture() {
      var now = read();
      pending = mergePatch(pending, delta(observed, now));
      observed = now;
      persistPending();
    }
    function mergePatch(a, b) {
      var result = Object.assign({}, a, b);
      if (a.answers || b.answers) result.answers = Object.assign({}, a.answers || {}, b.answers || {});
      return result;
    }
    function schedule(ms) {
      clearTimeout(timer);
      timer = setTimeout(sync, ms == null ? 1800 : ms);
    }
    function apply(state) {
      // Keep an already-downloaded solution cache on this device when its answer is unchanged.
      var rich = parse(localStorage.getItem(key)) || {};
      Object.keys(state.answers || {}).forEach(function (qid) {
        var cached = (rich.answers || {})[qid];
        if (cached && equal(compact({ answers: { a: cached } }).answers.a, state.answers[qid]) && cached.solution_html) {
          state.answers[qid] = Object.assign({}, state.answers[qid], { solution_html: cached.solution_html });
        }
      });
      originalSet.call(localStorage, key, JSON.stringify(state));
      observed = compact(state);
      window.dispatchEvent(new CustomEvent("ts-qb-state-restored", { detail: { product: product, state: state } }));
    }
    async function sync() {
      if (busy) return;
      capture();
      if (loaded && !dirty()) return;
      busy = true;
      try {
        if (!loaded) {
          var response = await fetch("/api/qb/user-progress?product=" + encodeURIComponent(product) + "&key=app_state&format=compact-v2", { credentials: "include", cache: "no-store" });
          var payload = await response.json();
          if (!response.ok || !payload.ok) throw new Error("Progress load unavailable");
          var remote = compact(payload.data && (payload.data.parsed || parse(payload.data.raw)));
          capture();
          if (!ack) {
            // Bootstrap only missing answers. A stale browser must not overwrite cloud progress.
            var missing = {};
            Object.keys(initial.answers || {}).forEach(function (qid) {
              if (!(remote.answers || {})[qid]) missing[qid] = initial.answers[qid];
            });
            var legacyUnsent = localRaw && legacyHash(localRaw) !== localStorage.getItem(key + "__last_push_hash");
            var sameServer = payload.updated_at && payload.updated_at === localStorage.getItem(key + "__server_updated_at");
            var bootstrap = !payload.data ? initial : legacyUnsent && sameServer ? delta(remote, initial)
              : Object.keys(missing).length ? { answers: missing } : {};
            pending = mergePatch(bootstrap, pending);
          }
          ack = remote;
          loaded = true;
          lastPull = Date.now();
          apply(merge(remote, pending));
          // The acknowledgement remains the cloud state, so unsent changes survive reloads.
          persistAck();
          persistPending();
        }
        capture();
        if (dirty()) {
          var sending = pending;
          inFlightPatch = sending;
          pending = {};
          try {
            var result = await fetch("/api/qb/user-progress", {
              method: "POST", credentials: "include", headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ product: product, key: "app_state", version: 2, patch: sending })
            });
            var saved = await result.json();
            if (!result.ok || !saved.ok) throw new Error("Progress save unavailable");
            ack = merge(ack, sending);
            persistAck();
            inFlightPatch = {};
            persistPending();
          } catch (error) {
            pending = mergePatch(sending, pending);
            inFlightPatch = {};
            persistPending();
            throw error;
          }
        }
        failures = 0;
      } catch (error) {
        failures++;
        console.warn("Progress retained locally; sync will retry", error);
      } finally {
        busy = false;
        if (!loaded || dirty()) schedule(failures ? Math.min(120000, 5000 * Math.pow(2, Math.min(failures, 5))) : 1800);
      }
    }
    Storage.prototype.setItem = function (storageKey, value) {
      var result = originalSet.apply(this, arguments);
      if (this === localStorage && storageKey === key) { capture(); schedule(); }
      return result;
    };
    window.addEventListener("online", function () { schedule(500); });
    window.addEventListener("storage", function (event) { if (event.key === key) { capture(); schedule(); } });
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "visible") {
        if (!busy && Date.now() - lastPull > 120000) loaded = false;
        schedule(500);
      }
    });
    // Event-driven saves only; no full-history polling or automatic reloads.
    schedule(0);
    return { sync: sync };
  }
  window.TS_QB_COMPACT = { start: start, compact: compact, delta: delta, merge: merge };
})();
