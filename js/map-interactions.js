/* Bifrost learning map: zoom, pan, and fit-to-view controls. */
(() => {
  const viewport = document.getElementById("mindmapViewport");
  const stage = viewport && viewport.querySelector(".mindmap-stage");
  if (!viewport || !stage) return;
  const zoomOutput = document.getElementById("mapZoomLevel");
  const MIN_SCALE = 0.32, MAX_SCALE = 1.25;
  let scale = 0.7, x = 0, y = 0, drag = null;
  function render() {
    stage.style.transform = `translate(calc(-50% + ${x}px), calc(-50% + ${y}px)) scale(${scale})`;
    if (zoomOutput) zoomOutput.value = `${Math.round(scale * 100)}%`;
  }
  function fit() {
    scale = Math.max(MIN_SCALE, Math.min(1, (viewport.clientWidth - 36) / 1500, (viewport.clientHeight - 36) / 1050));
    x = 0; y = 0; render();
  }
  function zoomAt(next, clientX, clientY) {
    const b = viewport.getBoundingClientRect(), px = clientX ?? b.left + b.width / 2, py = clientY ?? b.top + b.height / 2;
    const ox = px - (b.left + b.width / 2) - x, oy = py - (b.top + b.height / 2) - y;
    const ns = Math.max(MIN_SCALE, Math.min(MAX_SCALE, next)), ratio = ns / scale;
    x -= ox * (ratio - 1); y -= oy * (ratio - 1); scale = ns; render();
  }
  viewport.addEventListener("wheel", e => { e.preventDefault(); zoomAt(scale * (e.deltaY < 0 ? 1.12 : 1 / 1.12), e.clientX, e.clientY); }, { passive:false });
  viewport.addEventListener("pointerdown", e => {
    if (e.target.closest("button")) return;
    drag = { id:e.pointerId, sx:e.clientX, sy:e.clientY, x, y };
    viewport.setPointerCapture(e.pointerId); viewport.classList.add("is-dragging");
  });
  viewport.addEventListener("pointermove", e => { if (drag && drag.id === e.pointerId) { x=drag.x+e.clientX-drag.sx; y=drag.y+e.clientY-drag.sy; render(); } });
  function end(e) { if (drag && drag.id === e.pointerId) { drag=null; viewport.classList.remove("is-dragging"); } }
  viewport.addEventListener("pointerup",end); viewport.addEventListener("pointercancel",end);
  document.querySelectorAll("[data-map-zoom]").forEach(b => b.addEventListener("click", () => b.dataset.mapZoom === "reset" ? fit() : zoomAt(scale * (b.dataset.mapZoom === "in" ? 1.2 : 1/1.2))));
  window.addEventListener("resize",fit); fit();
})();