// Woodshed Lite — copy loader.
// Fetches content.json and drops each value into the element whose
// data-copy="section.key" matches. Edit content.json, refresh the page — no
// build step, no LLM round-trip needed. Runs independently of mount.js (no
// ordering dependency): it only touches static marketing copy, never the
// tune list/chart/etc. that mount.js owns.
(function () {
  'use strict';

  function get(obj, path) {
    return path.split('.').reduce((o, k) => (o && o[k] !== undefined ? o[k] : undefined), obj);
  }

  function applyCopy(content) {
    document.querySelectorAll('[data-copy]').forEach(el => {
      const val = get(content, el.dataset.copy);
      if (val === undefined) {
        console.warn('[woodshed-lite] content.json has no entry for', el.dataset.copy);
        return;
      }
      el.innerHTML = val;
    });
  }

  fetch('content.json', { cache: 'no-store' })
    .then(r => r.json())
    .then(applyCopy)
    .catch(e => console.warn('[woodshed-lite] content.json failed to load — showing the built-in fallback copy.', e));
})();
