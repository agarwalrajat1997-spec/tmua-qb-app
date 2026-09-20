/* TS_QB_SERIAL_SYNC_V2: one bounded progress request at a time per tab. */
(function () {
  "use strict";
  if (window.TS_QB_TRANSPORT) return;
  var nativeFetch = window.fetch.bind(window);
  var queue = Promise.resolve();
  var reads = new Map();
  var failures = 0;
  var retryAt = 0;
  function delay(ms) { return new Promise(function (resolve) { setTimeout(resolve, ms); }); }
  function status(message) {
    window.dispatchEvent(new CustomEvent("ts-qb-sync-status", { detail: message }));
  }
  function retryDelay(response) {
    var seconds = Number(response && response.headers.get("Retry-After"));
    return Math.max(seconds > 0 ? Math.min(seconds * 1000, 120000) : 0,
      Math.min(60000, 2000 * Math.pow(2, Math.min(failures, 5)))) + Math.floor(Math.random() * 750);
  }
  function isProgress(url) {
    try {
      var parsed = new URL(url, location.href);
      return parsed.origin === location.origin && /^\/api\/qb\/(user-progress|progress\/(save|load))$/.test(parsed.pathname);
    } catch (_) { return false; }
  }
  window.fetch = function (input, init) {
    var url = typeof input === "string" ? input : input.url;
    if (!isProgress(url)) return nativeFetch(input, init);
    var method = String((init && init.method) || (input && input.method) || "GET").toUpperCase();
    var read = method === "GET";
    var existing = reads.get(url);
    if (read && existing && (existing.pending || document.visibilityState === "hidden" || Date.now() - existing.at < 10000)) {
      return existing.promise.then(function (r) { return r.clone(); });
    }
    var run = async function () {
      for (var attempt = 0; attempt < 3; attempt++) {
        if (retryAt > Date.now()) await delay(retryAt - Date.now());
        var controller = new AbortController();
        var source = init && init.signal;
        var abort = function () { controller.abort(); };
        if (source) {
          if (source.aborted) controller.abort();
          source.addEventListener("abort", abort, { once: true });
        }
        var timer = setTimeout(abort, 15000);
        var response;
        var error;
        try {
          response = await nativeFetch(input, Object.assign({}, init, { signal: controller.signal }));
          if (response.status !== 429 && response.status < 500) {
            failures = 0; retryAt = 0;
            if (response.ok && !read) status("");
            else if (!response.ok) status("Progress could not sync. Your work remains saved on this device. Please sign in again or contact us.");
            return response;
          }
        } catch (e) { error = e; }
        finally {
          clearTimeout(timer);
          if (source) source.removeEventListener("abort", abort);
        }
        if (source && source.aborted) throw error || new Error("Request cancelled");
        failures++;
        retryAt = Date.now() + retryDelay(response);
        status("Connection interrupted. Your work is saved on this device; we’ll retry syncing shortly.");
        if (attempt === 2) {
          if (response) return response;
          throw error || new Error("Progress service unavailable");
        }
      }
    };
    var result = queue.then(run, run);
    queue = result.catch(function () {});
    if (read) {
      var entry = { at: Date.now(), pending: true, promise: result };
      reads.set(url, entry);
      result.then(function (r) { entry.pending = false; entry.at = Date.now(); if (!r.ok && reads.get(url) === entry) reads.delete(url); },
        function () { if (reads.get(url) === entry) reads.delete(url); });
      return result.then(function (r) { return r.clone(); });
    }
    return result;
  };
  window.TS_QB_TRANSPORT = { nextRetryAt: function () { return retryAt; } };
  window.addEventListener("ts-qb-sync-status", function (event) {
    var node = document.getElementById("ts-qb-sync-notice");
    if (!node && document.body) {
      node = document.createElement("div"); node.id = "ts-qb-sync-notice";
      node.setAttribute("role", "status");
      node.style.cssText = "position:fixed;bottom:12px;left:12px;right:12px;z-index:99999;padding:12px 16px;background:#fff3cd;color:#513e12;border:1px solid #e7d598;border-radius:8px;font:14px/1.5 Arial,sans-serif";
      document.body.appendChild(node);
    }
    if (node) { node.textContent = event.detail || ""; node.hidden = !event.detail; }
  });
})();
