(function () {
  "use strict";

  function initialize() {
    const modalElement = document.querySelector("[data-commerce-modal]");
    if (!modalElement || !window.bootstrap) return;

    const content = modalElement.querySelector("[data-commerce-modal-content]");
    const modal = window.bootstrap.Modal.getOrCreateInstance(modalElement);
    let opener = null;
    let activeRequest = null;

    function renderLoading() {
      content.innerHTML = [
        '<div class="uni2-commerce-modal-state" role="status">',
        '<h2 id="comercio-modal-title" class="visually-hidden">Ficha del comercio</h2>',
        '<span class="spinner-border" aria-hidden="true"></span>',
        '<span>Cargando ficha del comercio…</span>',
        "</div>",
      ].join("");
    }

    function renderError(fullUrl) {
      content.replaceChildren();
      const body = document.createElement("div");
      body.className = "uni2-commerce-modal-state";
      body.setAttribute("role", "alert");
      const title = document.createElement("h2");
      title.id = "comercio-modal-title";
      title.className = "visually-hidden";
      title.textContent = "Ficha del comercio";
      const message = document.createElement("p");
      message.textContent = "No pudimos cargar la ficha del comercio.";
      const link = document.createElement("a");
      link.className = "uni2-cta uni2-cta-secondary";
      link.href = fullUrl;
      link.textContent = "Abrir ficha completa";
      body.append(title, message, link);
      content.append(body);
    }

    document.addEventListener("click", async function (event) {
      const link = event.target.closest(".js-commerce-modal-link");
      if (
        !link || event.defaultPrevented || event.button !== 0 ||
        event.metaKey || event.ctrlKey || event.shiftKey || event.altKey
      ) return;

      event.preventDefault();
      opener = link;
      if (activeRequest) activeRequest.abort();
      activeRequest = new AbortController();
      renderLoading();
      modal.show();

      try {
        const response = await fetch(link.dataset.commerceModalUrl, {
          signal: activeRequest.signal,
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        if (!response.ok) throw new Error("Respuesta inválida");
        content.innerHTML = await response.text();
      } catch (error) {
        if (error.name !== "AbortError") renderError(link.href);
      }
    });

    modalElement.addEventListener("hide.bs.modal", function () {
      if (activeRequest) activeRequest.abort();
    });

    modalElement.addEventListener("hidden.bs.modal", function () {
      activeRequest = null;
      content.replaceChildren();
      if (opener && document.contains(opener)) opener.focus();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
