/* Inline, theme-aware teaching diagrams. No requests, libraries or user data. */
(() => {
  'use strict';
  const data = window.BifrostVisualData;
  const W = 760;
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const kinds = { flow: '흐름도', sequence: '순서도', compare: '비교도', table: '비교표', timeline: '타임라인', map: '구조도', cells: '데이터 모형', wheel: '연산 모형' };
  const measure = (value, size) => [...String(value)].reduce((sum, c) => sum + (/[^\x00-\xff]/.test(c) ? 1 : /[MW@#%]/.test(c) ? .85 : /[il.,:;!|' ]/.test(c) ? .34 : .62) * size, 0);
  function wrap(value, width, size) {
    const result = [];
    for (const paragraph of String(value).split('\n')) {
      let line = '';
      for (const word of paragraph.split(/(\s+)/).filter(Boolean)) {
        if (!word.trim()) { if (line) line += ' '; continue; }
        if (measure(line + word, size) <= width) { line += word; continue; }
        if (line.trim()) { result.push(line.trim()); line = ''; }
        for (const char of word) {
          if (line && measure(line + char, size) > width) { result.push(line); line = ''; }
          line += char;
        }
      }
      result.push(line.trim());
    }
    return result;
  }
  function text(value, x, y, width, { size = 14, line = 21, cls = '', anchor = 'start' } = {}) {
    const lines = wrap(value, width, size);
    return { height: lines.length * line, svg: `<text class="v-text ${cls}" font-size="${size}" text-anchor="${anchor}">${lines.map((s, i) => `<tspan x="${x}" y="${y + i * line}">${esc(s)}</tspan>`).join('')}</text>` };
  }
  const rect = (x, y, w, h, cls = '', radius = 12) => `<rect class="${cls}" x="${x}" y="${y}" width="${w}" height="${h}" rx="${radius}"/>`;
  function box(x, y, w, h, title, body = '', tone = '') {
    const heading = text(title, x + 17, y + 28, w - 34, { size: 15, line: 22, cls: 'v-heading' });
    const detail = body ? text(Array.isArray(body) ? body.join('\n') : body, x + 17, y + 28 + heading.height + 9, w - 34, { size: 13, line: 20, cls: 'v-secondary' }) : { height: 0, svg: '' };
    if (28 + heading.height + (body ? 9 + detail.height - 20 : -22) > h - 10) throw new Error(`Diagram box too small: ${title}`);
    return `<g class="v-tone ${esc(tone)}">${rect(x, y, w, h, 'v-node')}${rect(x + 1, y + 13, 3, h - 26, 'v-accent', 1)}${heading.svg}${detail.svg}</g>`;
  }
  function label(value, x, y, width = 220) {
    const t = text(value, x, y, width, { size: 12, line: 18, cls: 'v-edge-label', anchor: 'middle' });
    const actual = Math.min(width, Math.max(...wrap(value, width, 12).map(s => measure(s, 12)))) + 18;
    return `${rect(x - actual / 2, y - 14, actual, t.height + 2, 'v-label-bg', 5)}${t.svg}`;
  }
  const arrow = (d, prefix, tone = '', dashed = false) => `<path class="v-edge ${esc(tone)}${dashed ? ' v-dashed' : ''}" d="${d}" marker-end="url(#${prefix}-arrow)"/>`;
  function flow(v, prefix) {
    const gap = 30, width = (704 - gap * (v.steps.length - 1)) / v.steps.length;
    const contentHeight = Math.max(...v.steps.map(s => 51 + wrap(s[0], width - 34, 15).length * 22 + wrap(s[1], width - 34, 13).length * 20));
    const height = Math.max(144, contentHeight);
    let svg = '';
    v.steps.forEach(([title, body, tone], i) => {
      const x = 28 + i * (width + gap);
      svg += `<circle class="v-step-circle" cx="${x + 14}" cy="27" r="13"/><text class="v-step-number" x="${x + 14}" y="31" text-anchor="middle">${i + 1}</text>`;
      svg += box(x, 54, width, height, title, body, tone);
      if (i) svg += arrow(`M${x - gap + 4} ${54 + height / 2}H${x - 5}`, prefix);
    });
    return { svg, height: height + 78 };
  }
  function sequence(v, prefix) {
    const centers = v.actors.map((_, i) => 110 + i * 540 / (v.actors.length - 1));
    const height = 116 + v.messages.length * 66;
    let svg = centers.map(x => `<path class="v-lifeline" d="M${x} 76V${height - 14}"/>`).join('');
    v.actors.forEach((actor, i) => { svg += box(centers[i] - 82, 18, 164, 56, actor); });
    v.messages.forEach(([from, to, message, tone], i) => {
      const y = 124 + i * 66, a = centers[from], b = centers[to];
      const sign = Math.sign(b - a);
      svg += arrow(`M${a + sign * 7} ${y}H${b - sign * 10}`, prefix, tone);
      svg += label(`${i + 1}. ${message}`, (a + b) / 2, y - 12, Math.abs(b - a) - 32);
    });
    return { svg, height };
  }
  function compare(v) {
    const width = (704 - 24 * (v.panels.length - 1)) / v.panels.length;
    const rowHeights = v.panels[0].rows.map((_, i) => Math.max(...v.panels.map(p => {
      const row = p.rows[i] || ['', ''];
      return 22 + wrap(row[0], width - 34, 13).length * 20 + wrap(row[1], width - 34, 14).length * 22;
    })));
    const height = 88 + rowHeights.reduce((a, b) => a + b, 0);
    let svg = '';
    v.panels.forEach((panel, i) => {
      const x = 28 + i * (width + 24);
      svg += `<g class="v-tone ${esc(panel.tone || '')}">${rect(x, 20, width, height - 36, 'v-node')}${rect(x + 1, 21, width - 2, 5, 'v-accent', 2)}`;
      svg += text(panel.title, x + 17, 55, width - 34, { size: 16, cls: 'v-heading' }).svg;
      let y = 84;
      panel.rows.forEach(([name, value], ri) => {
        const t = text(name, x + 17, y, width - 34, { size: 13, line: 20, cls: 'v-secondary' });
        svg += t.svg + text(value, x + 17, y + t.height + 3, width - 34, { size: 14, line: 22 }).svg;
        y += rowHeights[ri];
        if (ri < panel.rows.length - 1) svg += `<path class="v-separator" d="M${x + 17} ${y - 20}H${x + width - 17}"/>`;
      });
      svg += '</g>';
    });
    return { svg, height };
  }
  function table(v) {
    const widths = v.widths || [230, ...v.columns.slice(1).map(() => 474 / (v.columns.length - 1))];
    let y = 20, svg = '';
    [v.columns, ...v.rows].forEach((row, ri) => {
      const height = Math.max(58, ...row.map((cell, ci) => 28 + wrap(typeof cell === 'string' ? cell : cell[0], widths[ci] - 26, ri ? 13 : 14).length * 20));
      let x = 28;
      row.forEach((cell, ci) => {
        const value = typeof cell === 'string' ? cell : cell[0];
        const tone = typeof cell === 'string' ? '' : cell[1];
        svg += `<g class="v-tone ${esc(tone)}">${rect(x, y, widths[ci], height, ri ? 'v-table-cell' : 'v-table-head', 0)}${text(value, x + 13, y + 27, widths[ci] - 26, { size: ri ? 13 : 14, line: 20, cls: ri ? '' : 'v-heading' }).svg}</g>`;
        x += widths[ci];
      });
      y += height;
    });
    return { svg, height: y + 20 };
  }
  function timeline(v, prefix) {
    let y = 26, svg = '';
    const parts = [];
    v.events.forEach(([time, title, body, tone]) => {
      const h = Math.max(90, 45 + wrap(title, 464, 15).length * 22 + wrap(body, 464, 13).length * 20);
      parts.push({ y, h, time, title, body, tone }); y += h + 16;
    });
    svg += arrow(`M166 40V${y - 16}`, prefix);
    parts.forEach(e => {
      svg += text(e.time, 140, e.y + 31, 112, { size: 12, line: 18, cls: 'v-secondary', anchor: 'end' }).svg;
      svg += `<circle class="v-point" cx="166" cy="${e.y + 26}" r="6"/>` + box(202, e.y, 502, e.h, e.title, e.body, e.tone);
    });
    return { svg, height: y + 10 };
  }
  function map(v, prefix) {
    let svg = (v.zones || []).map(z => `${rect(z[0], z[1], z[2], z[3], 'v-zone')}${text(z[4], z[0] + 14, z[1] + 23, z[2] - 28, { size: 12, cls: 'v-secondary' }).svg}`).join('');
    const nodes = Object.fromEntries(v.nodes.map(n => [n[0], n]));
    for (const e of v.edges || []) {
      let d;
      if (e.points) d = e.points.map((p, i) => `${i ? 'L' : 'M'}${p.join(' ')}`).join('');
      else {
        const a = nodes[e.from], b = nodes[e.to];
        const dx = b[1] + b[3] / 2 - a[1] - a[3] / 2, dy = b[2] + b[4] / 2 - a[2] - a[4] / 2;
        // Choose an axis with actual space between the rectangles. Center distance
        // alone can point a curve back through a wide source or destination box.
        const gapX = Math.max(b[1] - a[1] - a[3], a[1] - b[1] - b[3]);
        const gapY = Math.max(b[2] - a[2] - a[4], a[2] - b[2] - b[4]);
        if (gapX >= 0 && gapX >= gapY) {
          const ax = dx > 0 ? a[1] + a[3] : a[1], bx = dx > 0 ? b[1] : b[1] + b[3], ay = a[2] + a[4] / 2, by = b[2] + b[4] / 2, mid = (ax + bx) / 2;
          d = `M${ax} ${ay}C${mid} ${ay} ${mid} ${by} ${bx} ${by}`;
        } else {
          const ax = a[1] + a[3] / 2, bx = b[1] + b[3] / 2, ay = dy > 0 ? a[2] + a[4] : a[2], by = dy > 0 ? b[2] : b[2] + b[4], mid = (ay + by) / 2;
          d = `M${ax} ${ay}C${ax} ${mid} ${bx} ${mid} ${bx} ${by}`;
        }
      }
      svg += arrow(d, prefix, e.tone, e.dashed);
    }
    for (const n of v.nodes) svg += box(...n.slice(1));
    for (const e of v.edges || []) if (e.label) svg += label(e.label, e.at[0], e.at[1], e.at[2] || 210);
    return { svg, height: v.height };
  }
  function cells(v) {
    let y = 30, svg = '';
    for (const row of v.rows) {
      svg += text(row.title, 28, y, 704, { size: 14, cls: 'v-heading' }).svg;
      const width = Math.min(132, 704 / row.values.length);
      const x = (W - width * row.values.length) / 2;
      row.values.forEach((cell, i) => {
        const [value, tone = ''] = Array.isArray(cell) ? cell : [cell];
        svg += `<g class="v-tone ${esc(tone)}">${rect(x + i * width, y + 35, width - 5, 62, `v-node${tone === 'danger' ? ' v-outside' : ''}`, 7)}${text(row.labels?.[i] ?? String(i), x + i * width + (width - 5) / 2, y + 24, width - 12, { size: 11, anchor: 'middle', cls: 'v-secondary' }).svg}${text(value, x + i * width + (width - 5) / 2, y + 72, width - 14, { size: 16, anchor: 'middle', cls: 'v-heading' }).svg}</g>`;
      });
      if (row.validCount) {
        svg += `<path class="v-edge" d="M${x} ${y + 106}v6h${row.validCount * width - 5}v-6"/>`;
        svg += text(`유효한 ${row.validCount}개 원소`, x + (row.validCount * width - 5) / 2, y + 134, 300, { size: 12, anchor: 'middle', cls: 'v-secondary' }).svg;
      }
      y += row.validCount ? 173 : 145;
    }
    return { svg, height: y - 15 };
  }
  function wheel(v, prefix) {
    let svg = '<circle class="v-zone" cx="190" cy="160" r="113"/>';
    for (let i = 0; i < 5; i++) {
      const angle = -Math.PI / 2 + i * 2 * Math.PI / 5;
      const x = 190 + Math.cos(angle) * 91, y = 160 + Math.sin(angle) * 91;
      svg += `<circle class="${i === 2 ? 'v-highlight-circle' : 'v-step-circle'}" cx="${x}" cy="${y}" r="19"/><text class="v-wheel-number" x="${x}" y="${y + 5}" text-anchor="middle">${i}</text>`;
    }
    svg += arrow('M195 91Q203 170 235 214', prefix) + label('17칸 → 2', 225, 165, 110);
    svg += text('17 = 5 × 3 + 2', 190, 303, 280, { size: 14, anchor: 'middle', cls: 'v-heading' }).svg;
    svg += box(355, 48, 377, 232, '역원은 곱한 나머지가 1', ['기준: mod 26', '3 × 9 = 27 → 나머지 1', '따라서 3의 역원은 9', '존재 조건: gcd(3, 26) = 1']);
    return { svg, height: 320 };
  }
  const renderers = { flow, sequence, compare, table, timeline, map, cells, wheel };
  function render(id, course = false) {
    const v = (course ? data.courses : data.lessons)[id];
    if (!v) return '';
    const prefix = `visual-${course ? 'course-' : ''}${id.replace(/[^a-z0-9-]/gi, '-')}`;
    const { svg, height } = renderers[v.type](v, prefix);
    return `<figure class="learning-visual${course ? ' course-visual' : ''}" data-visual-id="${esc(id)}"><header class="visual-heading"><span class="visual-kicker">${course ? '이 분야의 학습 흐름' : '그림으로 이해하기'} · ${kinds[v.type]}</span><h3>${esc(v.title)}</h3></header><div class="visual-viewport" tabindex="0" role="region" aria-label="${esc(v.title)} 그림. 화면이 좁으면 좌우로 스크롤할 수 있습니다."><svg class="teaching-diagram" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${height}" width="${W}" height="${height}" role="img" aria-labelledby="${prefix}-title ${prefix}-desc" focusable="false"><title id="${prefix}-title">${esc(v.title)}</title><desc id="${prefix}-desc">${esc(v.description)}</desc><defs><marker id="${prefix}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="v-arrow-head" d="M1 1L9 5L1 9Z"/></marker></defs>${svg}</svg></div><figcaption><span class="visual-takeaway">${esc(v.takeaway)}</span>${v.note ? `<small class="visual-note">${esc(v.note)}</small>` : ''}</figcaption><details class="visual-description"><summary>그림 설명 읽기</summary><p>${esc(v.description)}</p></details></figure>`;
  }
  window.BifrostVisuals = Object.freeze({ renderLesson: id => render(id), renderCourse: id => render(id, true) });
})();
