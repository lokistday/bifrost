/* Stable lesson IDs, shared by the homepage and every course. No account required. */
(() => {
  'use strict';
  const KEY = 'bifrost_progress_v2';
  const LEGACY = 'whl_progress_v1';
  const validIds = new Set(Object.values(window.BifrostCourses).flatMap(c => c.modules.flatMap(m => m.lessons.map(l => l.id))));
  // Only equivalent topics migrate. Expanded/reworked lessons start unchecked.
  const migration = {
    foundation: ['foundation.paths', null, 'foundation.c-memory', 'foundation.permissions', 'foundation.network', 'foundation.http', 'foundation.git'],
    web: ['web.flow', 'web.sessions', 'web.authorization', 'web.sql-injection', 'web.output', 'web.authorization', 'web.regression'],
    pwn: ['pwn.build', 'pwn.lifetime', 'pwn.bounds', 'pwn.debugger', 'pwn.errors', 'pwn.mitigations', null],
    rev: ['rev.binary', 'rev.assembly', null, 'rev.static', 'rev.dynamic', null, 'rev.report'],
    forensic: ['forensic.logs', 'forensic.integrity', 'forensic.timeline', 'forensic.report'],
    network: [null, 'network.pcap', null],
    crypto: ['crypto.representation', 'crypto.modular', 'crypto.classical', 'crypto.hash', 'misc.automation', 'misc.triage', 'misc.writeup']
  };
  let available = true;
  let readable = true;
  const empty = () => ({ version: 2, completed: {}, lastLesson: null, legacyImported: false, legacy: {} });
  function clean(value) {
    if (!value || value.version !== 2 || !value.completed || typeof value.completed !== 'object' || Array.isArray(value.completed)) throw new Error('진도 파일 형식이 올바르지 않습니다.');
    const state = empty();
    for (const id of validIds) if (value.completed[id] === true) state.completed[id] = true;
    if (validIds.has(value.lastLesson)) state.lastLesson = value.lastLesson;
    state.legacyImported = value.legacyImported === true;
    const legacy = value.legacy;
    for (const [key, map] of Object.entries(migration)) {
      if (legacy && Array.isArray(legacy[key])) state.legacy[key] = [...new Set(legacy[key].filter(i => Number.isInteger(i) && i >= 0 && i < map.length))];
    }
    return state;
  }
  function read() {
    try {
      const raw = localStorage.getItem(KEY);
      return raw ? clean(JSON.parse(raw)) : empty();
    } catch (_) { readable = false; available = false; return empty(); }
  }
  let state = read();
  function persist() {
    // Preserve an unreadable/corrupt saved value until the user explicitly imports a valid backup.
    if (!readable) { available = false; window.dispatchEvent(new CustomEvent('bifrost-progress')); return; }
    try { localStorage.setItem(KEY, JSON.stringify(state)); available = true; }
    catch (_) { available = false; }
    window.dispatchEvent(new CustomEvent('bifrost-progress'));
  }
  if (!state.legacyImported && available) {
    try {
      const legacy = JSON.parse(localStorage.getItem(LEGACY) || '{}');
      for (const [key, map] of Object.entries(migration)) {
        if (!legacy || !Array.isArray(legacy[key])) continue;
        const indices = [...new Set(legacy[key].filter(i => Number.isInteger(i) && i >= 0 && i < map.length))];
        state.legacy[key] = indices;
        indices.forEach(i => { if (map[i] && validIds.has(map[i])) state.completed[map[i]] = true; });
      }
      state.legacyImported = true;
      persist();
    } catch (_) { available = false; }
  }
  window.addEventListener('storage', event => {
    if (event.key === KEY || event.key === null) {
      state = read();
      window.dispatchEvent(new CustomEvent('bifrost-progress'));
    }
  });
  window.addEventListener('pageshow', event => {
    if (event.persisted && available) {
      state = read();
      window.dispatchEvent(new CustomEvent('bifrost-progress'));
    }
  });
  window.BifrostProgress = {
    has: id => state.completed[id] === true,
    set(id, done) {
      if (!validIds.has(id)) return;
      // Re-read before changing one entry so another tab's work is preserved.
      if (available) state = read();
      if (done) state.completed[id] = true; else delete state.completed[id];
      persist();
    },
    visit(id) {
      if (!validIds.has(id)) return;
      if (available) state = read();
      state.lastLesson = id;
      persist();
    },
    count: lessons => lessons.filter(l => state.completed[l.id] === true).length,
    last: () => state.lastLesson,
    available: () => available,
    legacyCount: () => Object.values(state.legacy).reduce((n, a) => n + a.length, 0),
    export: () => JSON.stringify(state, null, 2),
    import(text) {
      if (text.length > 1000000) throw new Error('진도 파일은 1MB 이하여야 합니다.');
      const incoming = clean(JSON.parse(text));
      state = readable ? read() : empty();
      readable = true;
      // Import merges completion records; existing completed work stays checked.
      Object.assign(state.completed, incoming.completed);
      if (incoming.lastLesson) state.lastLesson = incoming.lastLesson;
      for (const key of Object.keys(migration)) state.legacy[key] = [...new Set([...(state.legacy[key] || []), ...(incoming.legacy[key] || [])])];
      state.legacyImported = true;
      persist();
    }
  };
})();
