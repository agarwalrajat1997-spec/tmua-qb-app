(function (global) {
  "use strict";
  var legacyPrefix = "TMUA-\u004a\u005a-";
  function identity(value) { return value.split(legacyPrefix).join("TMUA-TS-"); }
  function normalize(value) {
    if (typeof value === "string") return identity(value);
    if (Array.isArray(value)) return value.map(normalize);
    if (!value || typeof value !== "object") return value;
    return Object.fromEntries(Object.entries(value).filter(function (entry) {
      var key = entry[0], canonical = identity(key);
      return canonical === key || !Object.prototype.hasOwnProperty.call(value, canonical);
    }).map(function (entry) { return [identity(entry[0]), normalize(entry[1])]; }));
  }
  global.TSQuestionIdentities = { normalize: normalize };
  // Preserve account-qualified storage keys and queued submissions in place.
  // Authentication storage and unrelated application data are never touched.
  try {
    var storage = global.localStorage;
    var keys = [];
    for (var i = 0; i < storage.length; i++) keys.push(storage.key(i));
    keys.forEach(function (key) {
      if (!key || !/^ts_(?:esat|tmua|qb)_/i.test(key)) return;
      var raw = storage.getItem(key);
      if (!raw || raw.indexOf(legacyPrefix) === -1) return;
      try { storage.setItem(key, JSON.stringify(normalize(JSON.parse(raw)))); }
      catch (_) { /* Retain malformed or unavailable storage without deleting it. */ }
    });
  } catch (_) { /* Server-side compatibility also accepts older saved identities. */ }
})(window);
