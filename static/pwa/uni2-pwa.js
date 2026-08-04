// Registro de la PWA y experiencia global de instalación, conexión y actualización.
(function () {
  'use strict';

  let installPrompt = null;
  let waitingWorker = null;
  let reloadRequested = false;
  let onlineMessageTimer = null;
  let installPromotionDismissed = false;

  const INSTALL_PROMOTION_DISMISSED_KEY = 'uni2-pwa-install-promotion-dismissed';
  const standaloneQuery = window.matchMedia('(display-mode: standalone)');
  const isIOS =
    /iPad|iPhone|iPod/.test(navigator.userAgent) ||
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  const isIOSSafari =
    isIOS && /Safari/.test(navigator.userAgent) && !/CriOS|FxiOS|EdgiOS|OPiOS/.test(navigator.userAgent);

  function isStandalone() {
    return standaloneQuery.matches || window.navigator.standalone === true;
  }

  function setStandaloneClass() {
    document.documentElement.classList.toggle('uni2-is-standalone', isStandalone());
  }

  function installItems() {
    return document.querySelectorAll('.js-pwa-install-item');
  }

  function showInstallItems() {
    if (isStandalone()) return;
    installItems().forEach(function (item) {
      if (item.id === 'uni2-install-promotion' && installPromotionDismissed) return;
      item.hidden = false;
    });
  }

  function hideInstallItems() {
    installItems().forEach(function (item) {
      item.hidden = true;
    });
  }

  function showInstallInstructions() {
    const modalElement = document.getElementById('uni2-install-instructions');
    if (!modalElement || !window.bootstrap) return;

    const iosInstructions = modalElement.querySelector('[data-pwa-ios-install-instructions]');
    const browserInstructions = modalElement.querySelector(
      '[data-pwa-browser-install-instructions]'
    );
    const iosBrowserNote = modalElement.querySelector('[data-pwa-ios-browser-note]');
    const browserNote = modalElement.querySelector('[data-pwa-browser-note]');
    if (iosInstructions) iosInstructions.hidden = !isIOS;
    if (browserInstructions) browserInstructions.hidden = isIOS;
    if (iosBrowserNote) iosBrowserNote.hidden = !isIOS || isIOSSafari;
    if (browserNote) browserNote.hidden = isIOS;
    window.bootstrap.Modal.getOrCreateInstance(modalElement).show();
  }

  async function requestInstallation() {
    if (installPrompt) {
      installPrompt.prompt();
      const choice = await installPrompt.userChoice;
      installPrompt = null;
      if (choice.outcome === 'accepted') {
        hideInstallItems();
      } else {
        showInstallItems();
      }
      return;
    }
    showInstallInstructions();
  }

  function setupInstallation() {
    setStandaloneClass();
    try {
      installPromotionDismissed =
        window.sessionStorage.getItem(INSTALL_PROMOTION_DISMISSED_KEY) === 'true';
    } catch (error) {
      installPromotionDismissed = false;
    }
    if (!isStandalone()) showInstallItems();

    document.querySelectorAll('.js-pwa-install-trigger').forEach(function (button) {
      button.addEventListener('click', requestInstallation);
    });
    document.querySelectorAll('[data-pwa-install-dismiss]').forEach(function (button) {
      button.addEventListener('click', function () {
        installPromotionDismissed = true;
        try {
          window.sessionStorage.setItem(INSTALL_PROMOTION_DISMISSED_KEY, 'true');
        } catch (error) {
          // La invitación igual puede ocultarse durante esta vista.
        }
        const promotion = document.getElementById('uni2-install-promotion');
        if (promotion) promotion.hidden = true;
      });
    });

    window.addEventListener('beforeinstallprompt', function (event) {
      event.preventDefault();
      installPrompt = event;
      showInstallItems();
    });

    window.addEventListener('appinstalled', function () {
      installPrompt = null;
      hideInstallItems();
      setStandaloneClass();
    });

    if (standaloneQuery.addEventListener) {
      standaloneQuery.addEventListener('change', function () {
        setStandaloneClass();
        if (isStandalone()) hideInstallItems();
      });
    }
  }

  function connectivityElements() {
    const container = document.getElementById('uni2-connectivity-status');
    return {
      container: container,
      icon: container ? container.querySelector('i') : null,
      message: container ? container.querySelector('[data-pwa-connectivity-message]') : null,
    };
  }

  function showConnectivity(message, restored) {
    const elements = connectivityElements();
    if (!elements.container || !elements.message) return;

    window.clearTimeout(onlineMessageTimer);
    elements.message.textContent = message;
    elements.container.hidden = false;
    elements.container.classList.toggle('uni2-pwa-connectivity-online', restored);
    if (elements.icon) {
      elements.icon.className = restored ? 'bi bi-wifi' : 'bi bi-wifi-off';
    }

    if (restored) {
      onlineMessageTimer = window.setTimeout(function () {
        elements.container.hidden = true;
      }, 4000);
    }
  }

  function setupConnectivity() {
    if (!navigator.onLine) {
      showConnectivity('Sin conexión. Algunas funciones no están disponibles.', false);
    }

    window.addEventListener('offline', function () {
      showConnectivity(
        'Sin conexión. Podés ver una credencial guardada; las operaciones no se enviarán.',
        false
      );
    });
    window.addEventListener('online', function () {
      showConnectivity('Conexión restablecida.', true);
    });

    document.addEventListener(
      'submit',
      function (event) {
        const form = event.target;
        if (
          navigator.onLine ||
          !(form instanceof HTMLFormElement) ||
          form.hasAttribute('data-pwa-logout') ||
          String(form.method).toLowerCase() !== 'post'
        ) {
          return;
        }

        event.preventDefault();
        showConnectivity(
          'La operación no se envió ni quedó pendiente. Revisá la conexión y volvé a intentarlo.',
          false
        );
      },
      true
    );
  }

  function markDirtyForms() {
    document.querySelectorAll('form[method="post"]:not([data-pwa-logout])').forEach(function (form) {
      form.addEventListener('input', function () {
        form.dataset.pwaDirty = 'true';
      });
      form.addEventListener('change', function () {
        form.dataset.pwaDirty = 'true';
      });
    });
  }

  function hasDirtyForm() {
    return Boolean(document.querySelector('form[data-pwa-dirty="true"]'));
  }

  function showUpdate(worker) {
    waitingWorker = worker;
    const banner = document.getElementById('uni2-update-banner');
    if (banner) banner.hidden = false;
  }

  function setupUpdateControls() {
    const banner = document.getElementById('uni2-update-banner');
    const applyButton = document.getElementById('uni2-update-apply');
    const dismissButton = document.getElementById('uni2-update-dismiss');
    const message = banner ? banner.querySelector('[data-pwa-update-message]') : null;

    if (applyButton) {
      applyButton.addEventListener('click', function () {
        if (!waitingWorker) return;
        if (hasDirtyForm()) {
          if (message) {
            message.textContent =
              'Terminá o guardá el formulario abierto antes de actualizar para no perder datos.';
          }
          applyButton.focus();
          return;
        }
        reloadRequested = true;
        applyButton.disabled = true;
        if (message) {
          const shortName = document.body.dataset.pwaShortName || 'UNI2';
          message.textContent = 'Actualizando ' + shortName + '…';
        }
        waitingWorker.postMessage({ type: 'SKIP_WAITING' });
      });
    }

    if (dismissButton) {
      dismissButton.addEventListener('click', function () {
        if (banner) banner.hidden = true;
      });
    }
  }

  async function registerServiceWorker() {
    if (!('serviceWorker' in navigator)) return;

    try {
      const registration = await navigator.serviceWorker.register('/service-worker.js', {
        scope: '/',
        updateViaCache: 'none',
      });

      if (registration.waiting && navigator.serviceWorker.controller) {
        showUpdate(registration.waiting);
      }

      registration.addEventListener('updatefound', function () {
        const installingWorker = registration.installing;
        if (!installingWorker) return;
        installingWorker.addEventListener('statechange', function () {
          if (
            installingWorker.state === 'installed' &&
            navigator.serviceWorker.controller
          ) {
            showUpdate(registration.waiting || installingWorker);
          }
        });
      });

      // La navegación normal también revisa actualizaciones; esta llamada hace
      // explícito que el script del worker nunca se resuelve desde un caché viejo.
      registration.update().catch(function () {
        // La versión activa sigue funcionando aunque esta revisión falle.
      });
    } catch (error) {
      // La web tradicional sigue siendo utilizable si el navegador no puede
      // registrar el worker (por ejemplo, fuera de un contexto seguro).
    }
  }

  function setupControllerChange() {
    if (!('serviceWorker' in navigator)) return;
    navigator.serviceWorker.addEventListener('controllerchange', function () {
      if (!reloadRequested) return;
      reloadRequested = false;
      window.location.reload();
    });
  }

  function updateThemeColor() {
    const meta = document.getElementById('uni2-theme-color');
    if (!meta) return;
    const lightColor = document.body.dataset.pwaThemeColorLight || '#f7f9fc';
    const darkColor = document.body.dataset.pwaThemeColorDark || '#080c16';
    meta.setAttribute(
      'content',
      document.documentElement.getAttribute('data-theme') === 'dark' ? darkColor : lightColor
    );
  }

  function setupThemeColor() {
    updateThemeColor();
    new MutationObserver(updateThemeColor).observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme'],
    });
  }

  async function setupPrivateDataLifecycle() {
    const storage = window.Uni2PrivateStorage;
    if (!storage) return;
    const ownerSource = document.body.dataset.pwaOwnerSource || '';

    // Se comparte la misma promesa con la pantalla de credencial. Así esa
    // pantalla no habilita "Guardar" hasta haber eliminado, si existía, una
    // copia perteneciente a otra cuenta.
    storage.ownerReady = ownerSource
      ? storage.reconcileAuthenticatedOwner(ownerSource)
      : Promise.resolve(null);

    // El listener de logout se instala antes de esperar IndexedDB: cerrar la
    // sesión debe intentar limpiar la copia incluso si la apertura de la base
    // tarda o falla.
    document.querySelectorAll('form[data-pwa-logout]').forEach(function (form) {
      form.addEventListener(
        'submit',
        async function (event) {
          event.preventDefault();
          const submitter = event.submitter;
          if (submitter) submitter.disabled = true;

          try {
            await Promise.race([
              storage.deleteActiveCredential(),
              new Promise(function (resolve) {
                window.setTimeout(resolve, 1200);
              }),
            ]);
          } finally {
            HTMLFormElement.prototype.submit.call(form);
          }
        },
        true
      );
    });

    try {
      await storage.ownerReady;
      const savedCredential = await storage.getActiveCredential();
      document.querySelectorAll('.js-pwa-saved-credential-link').forEach(function (link) {
        link.hidden = !savedCredential;
      });
    } catch (error) {
      // El acceso a la web no depende de IndexedDB.
    }
  }

  function setupOfflineActions() {
    document.querySelectorAll('[data-pwa-retry]').forEach(function (button) {
      button.addEventListener('click', function () {
        window.location.reload();
      });
    });
    document.querySelectorAll('[data-pwa-history-back]').forEach(function (button) {
      button.addEventListener('click', function () {
        window.history.back();
      });
    });
  }

  function initialize() {
    setupInstallation();
    setupConnectivity();
    markDirtyForms();
    setupUpdateControls();
    setupControllerChange();
    setupThemeColor();
    setupOfflineActions();
    setupPrivateDataLifecycle();
    registerServiceWorker();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize, { once: true });
  } else {
    initialize();
  }
})();
