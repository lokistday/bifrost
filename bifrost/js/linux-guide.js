let guideReturnFocus = null;
function revealLinuxGuide({pushHistory=false}={}) {
  const overlay = document.getElementById("linuxGuideOverlay");
  const frame = document.getElementById("linuxGuideFrame");
  if (!frame.dataset.loaded) {
    frame.addEventListener("load", () => {
      const theme = document.documentElement.dataset.theme === "dark" ? "dark" : "light";
      if (frame.contentWindow) frame.contentWindow.postMessage({type:"bifrost-theme-change", theme}, location.origin);
    }, {once:false});
    frame.src = "guides/linux.html";
    frame.dataset.loaded = "true";
  } else if (frame.contentWindow) {
    const theme = document.documentElement.dataset.theme === "dark" ? "dark" : "light";
    frame.contentWindow.postMessage({type:"bifrost-theme-change", theme}, location.origin);
  }
  guideReturnFocus = guideReturnFocus || document.activeElement;
  overlay.classList.add("active");
  overlay.setAttribute("aria-hidden", "false");
  document.body.classList.add("guide-open");
  document.querySelectorAll("body > header, body > main, body > footer").forEach(node=>{node.inert=true;});
  if (pushHistory && location.hash !== "#linux-guide") {
    history.pushState({...((history.state && typeof history.state==="object")?history.state:{}), bifrostGuide:"linux"}, "", "#linux-guide");
  }
  document.getElementById("linuxGuideClose").focus({preventScroll:true});
  window.scrollTo(0,0);
}
function openLinuxGuide() {
  revealLinuxGuide({pushHistory:location.hash !== "#linux-guide"});
}
function hideLinuxGuide({restoreFocus=true, clearHash=false}={}) {
  const overlay = document.getElementById("linuxGuideOverlay");
  overlay.classList.remove("active");
  overlay.setAttribute("aria-hidden", "true");
  document.body.classList.remove("guide-open");
  document.querySelectorAll("body > header, body > main, body > footer").forEach(node=>{node.inert=false;});
  if (clearHash && location.hash === "#linux-guide") history.replaceState((history.state && typeof history.state==="object")?history.state:{}, "", location.pathname + location.search);
  if (restoreFocus && guideReturnFocus && typeof guideReturnFocus.focus === "function") guideReturnFocus.focus({preventScroll:true});
  guideReturnFocus = null;
}
function showMainGuide() {
  // 앱에서 연 가이드는 뒤로 가기와 같은 동작으로 닫아 앞으로 가기로 다시 열 수 있게 합니다.
  if (location.hash === "#linux-guide" && history.state && history.state.bifrostGuide === "linux") { history.back(); return; }
  hideLinuxGuide({clearHash:true});
  window.scrollTo(0,0);
}
document.addEventListener("keydown", event => {
  if (event.key === "Escape" && document.getElementById("linuxGuideOverlay").classList.contains("active")) { event.preventDefault(); showMainGuide(); }
});
window.addEventListener("popstate", () => {
  if (location.hash === "#linux-guide") revealLinuxGuide();
  else hideLinuxGuide({restoreFocus:true});
});
if (location.hash === "#linux-guide") revealLinuxGuide();
