// Shared help-tooltip harness (2026-08-07). One markup contract, wired once here instead of a
// bespoke bootstrap.Tooltip() call per icon (the pattern Workbench's EA042/EA034 icons used
// before this existed -- see DOCSv4 TODO §6, "systematize the existing incidental icons").
//
// Usage: <i class="bi bi-question-circle edops-help" data-help-text="..."></i>
// Optional: data-help-placement="top|right|bottom|left" (defaults to "right").
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

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initEdopsHelpTooltips);
  } else {
    initEdopsHelpTooltips();
  }

  // Exposed for pages that render new .edops-help icons dynamically after page load (e.g. from
  // a fetched API response) and need to re-scan.
  window.initEdopsHelpTooltips = initEdopsHelpTooltips;
})();
