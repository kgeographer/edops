// Shared help-tooltip harness (2026-08-07). One markup contract, wired once here instead of a
// bespoke bootstrap.Tooltip() call per icon (the pattern Workbench's EA042/EA034 icons used
// before this existed -- see DOCSv4 TODO §6, "systematize the existing incidental icons").
//
// Two mutually-exclusive icon behaviors, chosen by which data attribute is present:
//   - Hover tooltip:  <i class="bi bi-question-circle edops-help" data-help-text="..."></i>
//                      Optional: data-help-placement="top|right|bottom|left" (defaults "right").
//   - Click-to-toggle a panel (for content too long for a tooltip, e.g. a legend list):
//                      <i class="bi bi-question-circle edops-help" data-help-toggle="#some-id"></i>
//                      Clicking shows/hides the element matching the selector; no hover tooltip
//                      on this icon. The target starts hidden via its own style="display:none".
//
// Self-initializes on DOMContentLoaded -- no per-page call needed. Included once via
// _edops_header.html, which all three pages (Sandbox/Explorer/Workbench) already share.
(function () {
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
      el.addEventListener('click', function (e) {
        e.stopPropagation();
        var target = document.querySelector(el.dataset.helpToggle);
        if (target) target.style.display = target.style.display === 'none' ? '' : 'none';
      });
    });
  }

  function initEdopsHelp() {
    initEdopsHelpTooltips();
    initEdopsHelpToggles();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initEdopsHelp);
  } else {
    initEdopsHelp();
  }

  // Exposed for pages that render new .edops-help icons dynamically after page load (e.g. from
  // a fetched API response) and need to re-scan.
  window.initEdopsHelpTooltips = initEdopsHelp;
})();
