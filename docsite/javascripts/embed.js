// Hides Material's own header when this page is loaded inside an iframe (e.g. the app's Guide
// modals, which supply their own header/close button) -- never affects the standalone Docs site.
(function () {
  if (window.self === window.top) return;
  var header = document.querySelector('.md-header');
  if (header) header.style.display = 'none';
})();
