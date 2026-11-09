/* Preserve old subject-directory bookmarks under a subdirectory deployment. */
(() => {
  'use strict';
  if (location.hash === '#mindmap' || location.hash === '#fields') {
    location.replace(new URL('fields/', location.href).href);
  }
})();
