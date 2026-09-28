/* TS_QB_SERIAL_SYNC_V3: bounded requests and account-bound durable submissions. */
(function () {
  "use strict";
  if (window.TS_QB_TRANSPORT) return;
  var nativeFetch = window.fetch.bind(window), queue = Promise.resolve(), reads = new Map();
  var failures = 0, retryAt = 0, owner = null, paused = false, replayTimer, replayQueued = false, sequence = 0;
  var prefix = "ts_qb_submission_outbox_v3:", memory = new Map(), tabId = randomId();
  function status(message) {
    if (!message && window.TS_QB_LOCAL_STORAGE_UNAVAILABLE) message = "Browser storage is full. Keep this page open until progress syncs; offline recovery is unavailable for new changes.";
    window.dispatchEvent(new CustomEvent("ts-qb-sync-status", { detail: message }));
  }
  function delay(ms) { return new Promise(function (resolve) { setTimeout(resolve, ms); }); }
  function storageKeys() {
    var keys = []; for (var i = 0; i < localStorage.length; i++) keys.push(localStorage.key(i));
    memory.forEach(function (_, key) { if (keys.indexOf(key) < 0) keys.push(key); }); return keys;
  }
  function getRecord(key) { return memory.has(key) ? memory.get(key) : localStorage.getItem(key); }
  function putRecord(key, value) {
    try { localStorage.setItem(key, value); memory.delete(key); }
    catch (_) {
      memory.set(key, value); window.TS_QB_LOCAL_STORAGE_UNAVAILABLE = true;
      status("This browser cannot save an offline copy. Keep this page open until your progress syncs.");
    }
  }
  function removeRecord(key) { memory.delete(key); localStorage.removeItem(key); }
  function randomId() { return window.crypto && window.crypto.randomUUID ? window.crypto.randomUUID() : Date.now() + "-" + Math.random().toString(36).slice(2); }
  function parse(raw) { try { return JSON.parse(raw); } catch (_) { return null; } }
  function accountChanged() {
    paused = true; reads.clear();
    status("Your sign-in has changed. Your work is retained on this device. Reload this page before continuing.");
    window.dispatchEvent(new CustomEvent("ts-qb-account-changed", { detail: { user_id: owner } }));
  }
  function identify(id) {
    if (!id || typeof id !== "string") return;
    if (owner && owner !== id) { accountChanged(); return false; }
    if (!owner) {
      owner = id;
      window.dispatchEvent(new CustomEvent("ts-qb-account", { detail: { user_id: id } }));
      scheduleReplay(0);
    }
    return true;
  }
  function retryDelay(response) {
    var header = response && response.headers.get("Retry-After"), seconds = Number(header);
    var requested = seconds > 0 ? seconds * 1000 : Math.max(0, Date.parse(header) - Date.now()) || 0;
    return Math.max(Math.min(requested, 120000), Math.min(60000, 2000 * Math.pow(2, Math.min(failures, 5)))) + Math.floor(Math.random() * 750);
  }
  function pathOf(url) {
    try { var parsed = new URL(url, location.href); return parsed.origin === location.origin ? parsed.pathname : ""; }
    catch (_) { return ""; }
  }
  function isProgress(url) { return /^\/api\/qb\/(user-progress|progress\/(save|load))$/.test(pathOf(url)); }
  function scheduleReplay(ms) {
    clearTimeout(replayTimer);
    if (!owner || paused) return;
    replayTimer = setTimeout(replay, ms == null ? Math.max(1800, retryAt - Date.now()) : ms);
  }
  function records() {
    return storageKeys().filter(function (key) { return key && key.indexOf(prefix + owner + ":") === 0; })
      .map(function (key) { var value = parse(getRecord(key)); return value && Object.assign({ key: key }, value); })
      .filter(Boolean).sort(function (a, b) { return a.created - b.created || (a.tab_id === b.tab_id ? (a.sequence || 0) - (b.sequence || 0) : 0) || a.key.localeCompare(b.key); });
  }
  async function locked(fn) {
    if (window.navigator && navigator.locks && owner) return navigator.locks.request("ts-qb-submissions:" + owner, fn);
    return fn();
  }
  async function request(input, init, read) {
    var originalSignal = (init && init.signal) || (typeof input !== "string" && input.signal);
    for (var attempt = 0; attempt < 3; attempt++) {
      if (paused) return Response.json({ ok: false, code: "ACCOUNT_CHANGED" }, { status: 409 });
      if (originalSignal && originalSignal.aborted) throw new DOMException("Request cancelled", "AbortError");
      if (retryAt > Date.now()) await delay(retryAt - Date.now());
      if (originalSignal && originalSignal.aborted) throw new DOMException("Request cancelled", "AbortError");
      var controller = new AbortController(), abort = function () { controller.abort(); };
      if (originalSignal) originalSignal.addEventListener("abort", abort, { once: true });
      var timer = setTimeout(abort, 15000), response, error;
      try {
        response = await nativeFetch(input, Object.assign({}, init, { signal: controller.signal }));
        if (response.status !== 429 && response.status < 500) {
          var payload = await response.clone().json().catch(function () { return null; });
          if (response.status === 409 && payload && payload.code === "ACCOUNT_CHANGED") accountChanged();
          if (response.status === 401 || response.status === 403) {
            paused = true;
            status("Progress syncing is paused. Your work is retained on this device. Please sign in again and reload this page.");
          }
          if (response.ok && payload && payload.ok) {
            if (identify(payload.user_id || (payload.saved && payload.saved.user_id)) === false) {
              return Response.json({ ok: false, code: "ACCOUNT_CHANGED" }, { status: 409 });
            }
            failures = 0; retryAt = 0;
            if (!read) { reads.clear(); status(""); }
          }
          return response;
        }
      } catch (e) { error = e; }
      finally { clearTimeout(timer); if (originalSignal) originalSignal.removeEventListener("abort", abort); }
      if (originalSignal && originalSignal.aborted) throw error || new DOMException("Request cancelled", "AbortError");
      failures++; retryAt = Date.now() + retryDelay(response);
      status("Connection interrupted. Your work is retained on this device; we’ll retry syncing shortly.");
      if (attempt === 2) { if (response) return response; throw error || new Error("Progress service unavailable"); }
    }
  }
  async function sendRecord(record) {
    if (!getRecord(record.key)) return Response.json({ ok: true, already_synced: true });
    var response = await request(record.url, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: record.body }, false);
    var payload = await response.clone().json().catch(function () { return null; });
    if (response.ok && payload && payload.ok === true) removeRecord(record.key);
    else if ([400, 413, 422].indexOf(response.status) >= 0 || (response.status === 409 && payload && payload.extra && /^(TMUA|ESAT)_IDENTITY_VERSION_REQUIRED$/.test(payload.extra.code || ""))) {
      // A malformed record will not recover by retrying. Keep it for support,
      // while allowing later valid answers to leave the queue.
      putRecord(record.key.replace(prefix, "ts_qb_submission_rejected_v3:"), getRecord(record.key));
      removeRecord(record.key);
      status("One progress record needs review and is retained on this device. Please contact support; other answers can still sync.");
    }
    return response;
  }
  function enqueue(fn) { var result = queue.then(fn, fn); queue = result.catch(function () {}); return result; }
  function replay() {
    if (replayQueued || paused || !owner) return;
    replayQueued = true;
    enqueue(function () { return locked(async function () {
      var waiting = records();
      for (var i = 0; i < waiting.length && !paused; i++) {
        try { var response = await sendRecord(waiting[i]); if (!response.ok) break; }
        catch (_) { break; }
      }
    }); }).finally(function () {
      replayQueued = false;
      if (!paused && records().length) scheduleReplay();
    });
  }
  function progressFetch(input, init) {
    var url = typeof input === "string" ? input : input.url;
    if (!isProgress(url)) return nativeFetch(input, init);
    var method = String((init && init.method) || (input && input.method) || "GET").toUpperCase(), read = method === "GET";
    var existing = reads.get(url);
    if (read && existing && (existing.pending || Date.now() - existing.at < 10000 || (document.visibilityState === "hidden" && Date.now() - existing.at < 120000))) {
      return existing.promise.then(function (r) { return r.clone(); });
    }
    var body = !read && init && typeof init.body === "string" ? parse(init.body) : null;
    // Capture an immutable owner and submission now, not when a delayed queue eventually sends it.
    var boundOwner = (body && body.expected_user_id) || owner, record = null;
    if (owner && boundOwner !== owner) {
      accountChanged(); return Promise.resolve(Response.json({ ok: false, code: "ACCOUNT_CHANGED" }, { status: 409 }));
    }
    if (!read && body && !boundOwner) {
      var waitingKey = prefix + "unassigned:" + randomId();
      putRecord(waitingKey, JSON.stringify({ created: Date.now(), url: url, body: JSON.stringify(body) }));
      // Only edits created in this live page may wait for its authenticated read.
      // Unowned records from previous pages stay quarantined for manual recovery.
      return new Promise(function (resolve, reject) {
        function ready() {
          window.removeEventListener("ts-qb-account", ready);
          var saving = progressFetch(input, init);
          removeRecord(waitingKey);
          saving.then(resolve, reject);
        }
        window.addEventListener("ts-qb-account", ready);
      });
    }
    function bindRecord() {
      if (!body || !owner) return;
      if (!boundOwner) boundOwner = owner;
      body.expected_user_id = boundOwner;
      if (pathOf(url) === "/api/qb/progress/save" && !record) {
        record = { key: prefix + boundOwner + ":" + randomId(), created: Date.now(), tab_id: tabId, sequence: ++sequence, url: url, body: JSON.stringify(body) };
        putRecord(record.key, JSON.stringify(record));
      }
    }
    bindRecord();
    var result = enqueue(async function () {
      if (!read) {
        if (!owner || paused || (boundOwner && boundOwner !== owner)) return Response.json({ ok: false, error: "Verify your sign-in and reload before syncing." }, { status: 503 });
        bindRecord();
        if (record) return locked(async function () {
          var waiting = records(), response;
          for (var i = 0; i < waiting.length; i++) {
            response = await sendRecord(waiting[i]);
            if (!response.ok || waiting[i].key === record.key) return response;
          }
          return Response.json({ ok: true, already_synced: true });
        });
        if (body) init = Object.assign({}, init, { body: JSON.stringify(body) });
      }
      return request(input, init, read);
    });
    result.finally(function () { if (record && getRecord(record.key)) scheduleReplay(); }).catch(function () {});
    if (read) {
      var entry = { at: Date.now(), pending: true, promise: result }; reads.set(url, entry);
      result.then(function (r) { entry.pending = false; entry.at = Date.now(); if (!r.ok && reads.get(url) === entry) reads.delete(url); },
        function () { if (reads.get(url) === entry) reads.delete(url); });
      return result.then(function (r) { return r.clone(); });
    }
    return result;
  };
  window.fetch = progressFetch;
  window.TS_QB_TRANSPORT = {
    nextRetryAt: function () { return retryAt; }, account: function () { return owner; }, paused: function () { return paused; },
    pendingUpdates: function (product) {
      var updates = [];
      if (!owner) return updates;
      records().forEach(function (record) {
        var body = parse(record.body);
        if (body && body.expected_user_id === owner && body.product === product && Array.isArray(body.updates)) updates = updates.concat(body.updates);
      });
      return JSON.parse(JSON.stringify(updates));
    }
  };
  window.addEventListener("online", function () { scheduleReplay(500); });
  window.addEventListener("ts-qb-sync-status", function (event) {
    var node = document.getElementById("ts-qb-sync-notice");
    if (!node && document.body) {
      node = document.createElement("div"); node.id = "ts-qb-sync-notice"; node.setAttribute("role", "status");
      node.style.cssText = "position:fixed;bottom:12px;left:12px;right:12px;z-index:99999;padding:12px 16px;background:#fff3cd;color:#513e12;border:1px solid #e7d598;border-radius:8px;font:14px/1.5 Arial,sans-serif";
      document.body.appendChild(node);
    }
    if (node) { node.textContent = event.detail || ""; node.hidden = !event.detail; }
  });
})();
