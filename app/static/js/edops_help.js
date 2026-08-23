// Shared help-icon harness (2026-08-07; extended 2026-08-23 with modal mode + decorators).
// One markup contract for every help icon across all three pages -- mode is chosen by which
// data attribute is present. Non-tooltip modes get a small decorator icon (injected here, never
// hand-authored in a template) that signals what a click will do before the user clicks:
//
//   - Hover tooltip:   <i class="bi bi-question-circle edops-help" data-help-text="..."></i>
//                       Optional: data-help-placement="top|right|bottom|left" (defaults "right").
//                       No decorator -- this is the baseline affordance.
//   - Toggle a panel:  <i class="bi bi-question-circle edops-help" data-help-toggle="#some-id"></i>
//                       Click shows/hides the element matching the selector; the target starts
//                       hidden via its own style="display:none". Gets a chevron decorator that
//                       tracks the panel state (down = closed, up = open).
//   - Open a modal:    <i class="bi bi-question-circle edops-help" data-help-modal="#modal-id"></i>
//                       Click opens the Bootstrap modal matching the selector (harness wires the
//                       data-bs-toggle/data-bs-target attributes itself). Gets a static
//                       up-right-arrow decorator.
//
// Self-initializes on DOMContentLoaded, then keeps watching the page via MutationObserver, so
// any .edops-help markup -- static, or injected later by page JS (AJAX-rendered signature
// panels, dynamically-built lists, etc.) -- is picked up the moment it lands in the DOM. No page
// ever needs to remember to call an init/re-scan function; the contract is purely declarative
// markup. Included once via _edops_header.html, which all three pages (Sandbox/Explorer/
// Workbench) already share.
//
// Icons whose text loads asynchronously (e.g. from a fetched API response): render the icon with
// no data-help-text initially, then once the data arrives set el.dataset.helpText -- the observer
// picks up the attribute change and wires the tooltip itself.
(function () {
  function addDecorator(el, iconClass, extraClass) {
    var deco = document.createElement('i');
    deco.className = 'bi ' + iconClass + ' edops-help-decorator' + (extraClass ? ' ' + extraClass : '');
    el.insertAdjacentElement('afterend', deco);
    return deco;
  }

  function initEdopsHelpTooltips() {
    document.querySelectorAll('.edops-help[data-help-text]').forEach(function (el) {
      if (bootstrap.Tooltip.getInstance(el)) return; // don't double-init if called more than once
      new bootstrap.Tooltip(el, {
        title: el.dataset.helpText,
        placement: el.dataset.helpPlacement || 'right',
        trigger: 'hover',
      });
      // Icons are often inline next to clickable headers (accordion toggles, etc.) --
      // don't let a hover/click on the icon itself bubble into that.
      el.addEventListener('click', function (e) { e.stopPropagation(); });
    });
  }

  function initEdopsHelpToggles() {
    document.querySelectorAll('.edops-help[data-help-toggle]').forEach(function (el) {
      if (el.dataset.edopsToggleWired) return; // don't double-wire if called more than once
      el.dataset.edopsToggleWired = 'true';
      var target = document.querySelector(el.dataset.helpToggle);
      var caret = addDecorator(el, 'bi-chevron-down', 'edops-help-caret');
      function syncCaret() {
        var hidden = !target || target.style.display === 'none';
        caret.className = 'bi ' + (hidden ? 'bi-chevron-down' : 'bi-chevron-up') + ' edops-help-decorator edops-help-caret';
      }
      function handleClick(e) {
        e.stopPropagation();
        if (target) target.style.display = target.style.display === 'none' ? '' : 'none';
        syncCaret();
      }
      syncCaret();
      el.addEventListener('click', handleClick);
      caret.addEventListener('click', handleClick);
    });
  }

  function initEdopsHelpModals() {
    document.querySelectorAll('.edops-help[data-help-modal]').forEach(function (el) {
      if (el.dataset.edopsModalWired) return; // don't double-wire if called more than once
      el.dataset.edopsModalWired = 'true';
      el.setAttribute('data-bs-toggle', 'modal');
      el.setAttribute('data-bs-target', el.dataset.helpModal);
      var arrow = addDecorator(el, 'bi-box-arrow-up-right', 'edops-help-modal-arrow');
      el.addEventListener('click', function (e) { e.stopPropagation(); });
      arrow.addEventListener('click', function () { el.click(); });
    });
  }

  function initEdopsHelp() {
    initEdopsHelpTooltips();
    initEdopsHelpToggles();
    initEdopsHelpModals();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initEdopsHelp);
  } else {
    initEdopsHelp();
  }

  // Watch for .edops-help markup added or changed anywhere after initial load -- new nodes
  // (AJAX-rendered panels) and attribute changes on existing nodes (async-loaded tooltip text)
  // both re-run initEdopsHelp(); every sub-function is guarded against double-wiring, so
  // reprocessing already-wired icons is a no-op.
  new MutationObserver(initEdopsHelp).observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['data-help-text', 'data-help-toggle', 'data-help-modal'],
  });

  // Exposed as a manual fallback; nothing needs to call this anymore under normal use.
  window.initEdopsHelpTooltips = initEdopsHelp;
})();
