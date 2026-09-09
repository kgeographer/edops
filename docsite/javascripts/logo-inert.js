// Make the docs-site logo inert on the standalone full-page docs. Material links
// it to href="." (reloads the index). /docs is only ever reached as a disposable
// new tab -- from the modal's "Full page" button, or an external link -- so there
// is nothing to navigate to; the logo is just a mark. embed.js hides this header
// entirely inside the app's Documentation modal, so this only affects full-page /docs.
(function () {
  document.querySelectorAll('[data-md-component="logo"]').forEach(function (a) {
    a.removeAttribute('href');
    a.removeAttribute('title');
    a.style.cursor = 'default';
  });
})();
