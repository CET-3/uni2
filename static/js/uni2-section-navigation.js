(function () {
  "use strict";

  function navigateToSection(link) {
    const targetUrl = new URL(link.href, window.location.href);
    const sameDocument =
      targetUrl.origin === window.location.origin &&
      targetUrl.pathname === window.location.pathname &&
      targetUrl.search === window.location.search;

    if (!sameDocument) {
      window.location.assign(targetUrl.href);
      return;
    }

    const target = document.querySelector(targetUrl.hash);
    if (!target) {
      window.location.assign(targetUrl.href);
      return;
    }

    window.history.pushState(null, "", targetUrl.hash);
    target.scrollIntoView({ block: "start" });
  }

  document.addEventListener("click", function (event) {
    const link = event.target.closest(".js-uni2-section-link");
    if (!link) {
      return;
    }

    const menu = document.getElementById("navbarUni2");
    if (!menu || !menu.classList.contains("show") || !window.bootstrap) {
      return;
    }

    event.preventDefault();
    menu.addEventListener(
      "hidden.bs.collapse",
      function () {
        navigateToSection(link);
      },
      { once: true }
    );
    window.bootstrap.Collapse.getOrCreateInstance(menu).hide();
  });
})();
