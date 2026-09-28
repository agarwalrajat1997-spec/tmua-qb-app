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
  function start(product, key) {
    var originalSet = Storage.prototype.setItem, originalGet = Storage.prototype.getItem;
    var owner = null, scope = null, ack = {}, pending = {}, inFlightPatch = {}, observed = {};
    var viewRaw = JSON.stringify({ answers: {}, filters: {} });
    observed = compact(parse(viewRaw));
    var loaded = false, busy = false, stopped = false, failures = 0, lastPull = 0, timer;
    var tabId = window.crypto && window.crypto.randomUUID ? window.crypto.randomUUID() : Date.now() + "-" + Math.random().toString(36).slice(2);
    var pendingKey = null, journalWritten = false;
    var memory = new Map();
    function get(k) { return memory.has(k) ? memory.get(k) : originalGet.call(localStorage, k); }
    function put(k, value) {
      try { originalSet.call(localStorage, k, value); memory.delete(k); }
      catch (_) {
        memory.set(k, value); window.TS_QB_LOCAL_STORAGE_UNAVAILABLE = true;
        window.dispatchEvent(new CustomEvent("ts-qb-sync-status", { detail: "Browser storage is full. Keep this page open until progress syncs; offline recovery is unavailable for new changes." }));
      }
    }
    function remove(k) { memory.delete(k); localStorage.removeItem(k); }
    // Old releases did not record an owner. Retain their complete data for recovery,
    // but never assign another student's browser history to the next signed-in user.
    if (get(key) && !get(key + "__unassigned_legacy_v3")) {
      put(key + "__unassigned_legacy_v3", JSON.stringify({ raw_key: key, ack_key: key + "__compact_ack_v2", pending_key: key + "__pending_delta_v2" }));
    }
    function mergePatch(a, b) {
      var result = Object.assign({}, a, b);
      if (a.answers || b.answers) result.answers = Object.assign({}, a.answers || {}, b.answers || {});
      return result;
    }
    function dirty() { return Object.keys(pending).length > 0; }
    function persistPending() {
      var patch = mergePatch(inFlightPatch, pending);
      if (!pendingKey) {
        // Fresh edits made while identity is unavailable are retained, but are not
        // replayed by a later unrelated sign-in without verified ownership.
        if (Object.keys(patch).length) put(key + "__unassigned_tab_v3:" + tabId, JSON.stringify(patch));
        return;
      }
      if (Object.keys(patch).length) {
        var old = parse(get(pendingKey));
        if (!old || !equal(old.patch, patch)) put(pendingKey, JSON.stringify({ at: Date.now(), patch: patch }));
        journalWritten = true;
      } else { remove(pendingKey); journalWritten = false; }
    }
    function journal() {
      var rows = [];
      if (!scope) return rows;
      var names = [];
      for (var i = 0; i < localStorage.length; i++) names.push(localStorage.key(i));
      memory.forEach(function (_, name) { if (names.indexOf(name) < 0) names.push(name); });
      for (var j = 0; j < names.length; j++) {
        var name = names[j];
        if (name && name.indexOf(scope + "pending:") === 0) {
          var raw = get(name), row = parse(raw);
          if (row && object(row.patch)) rows.push({ key: name, raw: raw, at: row.at || 0, patch: row.patch });
        }
      }
      return rows.sort(function (a, b) { return a.at - b.at || a.key.localeCompare(b.key); });
    }
    function capture() {
      // Another tab may have acknowledged this journal under the shared lock.
      if (pendingKey && journalWritten && !get(pendingKey) && !Object.keys(inFlightPatch).length) pending = {};
      var now = compact(parse(viewRaw));
      pending = mergePatch(pending, delta(observed, now));
      observed = now;
      persistPending();
    }
    function bind(id) {
      if (!id || typeof id !== "string") throw new Error("Progress account could not be verified");
      if (owner && owner !== id) { stopped = true; throw new Error("Signed-in account changed; reload this page"); }
      if (owner) return;
      owner = id; scope = key + "__account_v3:" + owner + ":"; pendingKey = scope + "pending:" + tabId;
      ack = parse(get(scope + "ack")) || {};
      // Only the durable journal proves an unsent change. A cached full state
      // may be stale after another tab/device saved and must not become a delta.
      persistPending();
      remove(key + "__unassigned_tab_v3:" + tabId);
    }
    function schedule(ms) {
      clearTimeout(timer);
      if (!stopped) timer = setTimeout(sync, ms == null ? 1800 : ms);
    }
    function apply(state, publish) {
      var rich = parse(viewRaw) || {};
      Object.keys(state.answers || {}).forEach(function (qid) {
        var cached = (rich.answers || {})[qid];
        if (cached && equal(compact({ answers: { a: cached } }).answers.a, state.answers[qid]) && cached.solution_html) {
          state.answers[qid] = Object.assign({}, state.answers[qid], { solution_html: cached.solution_html });
        }
      });
      viewRaw = JSON.stringify(state); observed = compact(state);
      if (scope && publish !== false) put(scope + "state", JSON.stringify(compact(state)));
      window.dispatchEvent(new CustomEvent("ts-qb-state-restored", { detail: { product: product, state: state } }));
    }
    async function work() {
      if (!loaded) {
        var response = await fetch("/api/qb/user-progress?product=" + encodeURIComponent(product) + "&key=app_state&format=compact-v2", { credentials: "include", cache: "no-store" });
        var payload = await response.json();
        if (!response.ok || !payload.ok) {
          if (response.status === 401 || response.status === 403 || response.status === 409) stopped = true;
          throw new Error("Progress load unavailable");
        }
        capture(); bind(payload.user_id);
        var remote = compact(payload.data && (payload.data.parsed || parse(payload.data.raw)));
        journal().forEach(function (row) { pending = mergePatch(pending, row.patch); });
        ack = remote; loaded = true; lastPull = Date.now();
        apply(merge(remote, pending));
        put(scope + "ack", JSON.stringify(ack)); persistPending();
      }
      capture();
      var snapshots = journal(), sending = {};
      snapshots.forEach(function (row) { sending = mergePatch(sending, row.patch); });
      if (!Object.keys(sending).length) return;
      inFlightPatch = sending; pending = {}; persistPending();
      // Acknowledge exactly the records used to build this POST. Another tab
      // may append a journal meanwhile; a second full scan would delete unsent work.
      snapshots = snapshots.filter(function (row) { return row.key !== pendingKey; });
      var ownRaw = get(pendingKey);
      if (ownRaw) snapshots.push({ key: pendingKey, raw: ownRaw });
      try {
        var result = await fetch("/api/qb/user-progress", {
          method: "POST", credentials: "include", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ product: product, key: "app_state", version: 2, expected_user_id: owner, patch: sending })
        });
        var saved = await result.json();
        if (!result.ok || !saved.ok) {
          if (result.status === 409 || result.status === 401 || result.status === 403) stopped = true;
          throw new Error("Progress save unavailable");
        }
        ack = merge(ack, sending); put(scope + "ack", JSON.stringify(ack));
        snapshots.forEach(function (row) { if (get(row.key) === row.raw) remove(row.key); });
        inFlightPatch = {}; persistPending();
      } catch (error) {
        pending = mergePatch(sending, pending); inFlightPatch = {}; persistPending(); throw error;
      }
    }
    async function sync() {
      if (busy || stopped) return;
      capture();
      if (loaded && !dirty() && !journal().length) return;
      busy = true;
      try {
        if (window.navigator && navigator.locks) await navigator.locks.request("ts-qb-compact:" + product, work);
        else await work();
        failures = 0;
      } catch (error) { failures++; console.warn("Progress retained locally; sync will retry", error); }
      finally {
        busy = false;
        if (!loaded || dirty() || journal().length) schedule(failures ? Math.min(120000, 5000 * Math.pow(2, Math.min(failures, 5))) : 1800);
      }
    }
    // The existing UI keeps its legacy key, but each tab reads/writes an isolated
    // account view; no global student history is exposed during authentication.
    Storage.prototype.getItem = function (storageKey) {
      return this === localStorage && storageKey === key ? viewRaw : originalGet.apply(this, arguments);
    };
    Storage.prototype.setItem = function (storageKey, value) {
      if (this === localStorage && storageKey === key) {
        var before = observed;
        viewRaw = String(value); capture();
        if (scope) {
          var combined = merge(compact(parse(get(scope + "state"))), delta(before, observed));
          // Preserve another tab's answers without recursively re-rendering the
          // question while the current UI is still processing its check event.
          put(scope + "state", JSON.stringify(combined));
        }
        schedule(); return;
      }
      return originalSet.apply(this, arguments);
    };
    window.addEventListener("online", function () { schedule(500); });
    window.addEventListener("ts-qb-account-changed", function () { stopped = true; clearTimeout(timer); });
    window.addEventListener("storage", function (event) {
      if (scope && event.key && event.key.indexOf(scope) === 0 && !busy) {
        var combined = compact(parse(get(scope + "state")));
        apply(merge(combined, pending), false); schedule();
      }
    });
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "visible") {
        if (!busy && Date.now() - lastPull > 120000) loaded = false;
        schedule(500);
      }
    });
    schedule(0);
    return { sync: sync, pendingAnswers: function () {
      var changes = {};
      journal().forEach(function (row) { changes = mergePatch(changes, row.patch); });
      changes = mergePatch(changes, mergePatch(inFlightPatch, pending));
      return JSON.parse(JSON.stringify(changes.answers || {}));
    } };
  }
  window.TS_QB_COMPACT = { start: start, compact: compact, delta: delta, merge: merge };
})();
