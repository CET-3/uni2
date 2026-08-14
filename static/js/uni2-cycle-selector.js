(function () {
  "use strict";

  var mobile = window.matchMedia("(max-width: 575.98px)");

  function initializeSelector(root) {
    var tablist = root.querySelector("[data-cycle-tabs]");
    if (!tablist) {
      return;
    }

    var tabs = Array.from(tablist.querySelectorAll("[data-cycle-tab]"));
    var panels = Array.from(root.querySelectorAll("[data-cycle-panel]"));
    var initialIndex = tabs.findIndex(function (tab) {
      return tab.dataset.cycleTab === "cb";
    });
    var activeIndex = initialIndex >= 0 ? initialIndex : 0;

    function selectTab(index, moveFocus) {
      activeIndex = index;
      tabs.forEach(function (tab, tabIndex) {
        var selected = tabIndex === activeIndex;
        tab.setAttribute("aria-selected", selected ? "true" : "false");
        tab.tabIndex = selected ? 0 : -1;
        if (selected && moveFocus) {
          tab.focus();
        }
      });
      panels.forEach(function (panel) {
        panel.hidden = panel.dataset.cyclePanel !== tabs[activeIndex].dataset.cycleTab;
      });
    }

    function updateLayout() {
      if (mobile.matches) {
        tablist.hidden = false;
        selectTab(activeIndex, false);
        return;
      }

      tablist.hidden = true;
      panels.forEach(function (panel) {
        panel.hidden = false;
      });
    }

    tabs.forEach(function (tab, index) {
      tab.addEventListener("click", function () {
        selectTab(index, false);
      });
      tab.addEventListener("keydown", function (event) {
        if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") {
          return;
        }
        event.preventDefault();
        var direction = event.key === "ArrowRight" ? 1 : -1;
        var nextIndex = (index + direction + tabs.length) % tabs.length;
        selectTab(nextIndex, true);
      });
    });

    updateLayout();
    if (typeof mobile.addEventListener === "function") {
      mobile.addEventListener("change", updateLayout);
    } else {
      mobile.addListener(updateLayout);
    }
  }

  document.querySelectorAll("[data-cycle-selector]").forEach(initializeSelector);
})();
