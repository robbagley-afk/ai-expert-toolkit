// templates/guide.js
// NONCE toolkit-checklist-20261009. Coding Helper output, reviewed by Codex.
(function () {
  'use strict';
  const STORAGE_KEY = 'toolkit-guide-checklist-v1';
  function loadSaved() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return Object.create(null);
      const parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return Object.create(null);
      const clean = Object.create(null);
      for (const key of Object.keys(parsed)) {
        if (typeof parsed[key] === 'boolean') clean[key] = parsed[key];
      }
      return clean;
    } catch (_) { return Object.create(null); }
  }
  function save(map, known) {
    try {
      const out = Object.create(null);
      for (const id of known) {
        if (Object.prototype.hasOwnProperty.call(map, id)) out[id] = map[id];
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(out));
    } catch (_) { /* Storage may be denied or full. */ }
  }
  function updateProgress(checkboxes, progress) {
    if (!progress) return;
    const done = checkboxes.filter(function (cb) { return cb.checked; }).length;
    progress.textContent = done + ' of ' + checkboxes.length + ' complete';
  }
  function init() {
    const checkboxes = Array.from(document.querySelectorAll('input[data-check]')).filter(function (el) {
      const id = el.getAttribute('data-check');
      return typeof id === 'string' && id.length > 0;
    });
    const knownIds = checkboxes.map(function (cb) { return cb.getAttribute('data-check'); });
    const progress = document.querySelector('[data-progress]') || null;
    const saved = loadSaved();
    checkboxes.forEach(function (cb) {
      const id = cb.getAttribute('data-check');
      if (Object.prototype.hasOwnProperty.call(saved, id)) cb.checked = saved[id];
    });
    updateProgress(checkboxes, progress);
    checkboxes.forEach(function (cb) {
      cb.addEventListener('change', function () {
        saved[cb.getAttribute('data-check')] = cb.checked;
        updateProgress(checkboxes, progress);
        save(saved, knownIds);
      });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
}());
