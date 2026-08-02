// Renderizado del QR y copia consentida de la credencial en IndexedDB.
(function () {
  'use strict';

  const configuredRetentionDays = Number.parseInt(
    document.body.dataset.pwaCredentialTtlDays || '7',
    10
  );
  const RETENTION_DAYS =
    Number.isFinite(configuredRetentionDays) && configuredRetentionDays > 0
      ? configuredRetentionDays
      : 7;

  function renderQRCode(container, token, accessibleName) {
    if (!container) return;
    container.textContent = '';

    try {
      if (typeof window.qrcode !== 'function') throw new Error('Generador QR no disponible.');
      const code = window.qrcode(0, 'M');
      code.addData(String(token), 'Byte');
      code.make();
      container.innerHTML = code.createSvgTag(6, 4);
      const svg = container.querySelector('svg');
      if (svg) {
        svg.setAttribute('role', 'img');
        svg.setAttribute('aria-label', accessibleName || 'Código QR de la credencial');
        svg.setAttribute('focusable', 'false');
      }
    } catch (error) {
      const fallback = document.createElement('p');
      fallback.className = 'small text-secondary mb-0 text-center';
      fallback.textContent = 'No se pudo generar el QR. Usá el token escrito en la credencial.';
      container.appendChild(fallback);
    }
  }

  function formatDateTime(value) {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return 'en una fecha desconocida';
    return new Intl.DateTimeFormat('es-AR', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(date);
  }

  function formatDate(value) {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return 'una fecha desconocida';
    return new Intl.DateTimeFormat('es-AR', { dateStyle: 'medium' }).format(date);
  }

  function setText(selector, value, root) {
    (root || document).querySelectorAll(selector).forEach(function (element) {
      element.textContent = value;
    });
  }

  function newExpiryDate() {
    const expiry = new Date();
    expiry.setDate(expiry.getDate() + RETENTION_DAYS);
    return expiry.toISOString();
  }

  async function initializeOnlineCredential(root) {
    const storage = window.Uni2PrivateStorage;
    const saveButton = document.getElementById('uni2-credential-save');
    const saveConfirmButton = document.getElementById('uni2-credential-save-confirm');
    const deleteButton = document.getElementById('uni2-credential-delete');
    const status = document.getElementById('uni2-credential-storage-status');
    const ownerSource = document.body.dataset.pwaOwnerSource || '';

    renderQRCode(
      root.querySelector('[data-uni2-qr-value]'),
      root.dataset.credentialToken,
      'Código QR de la credencial de ' +
        root.dataset.credentialNombre +
        ' ' +
        root.dataset.credentialApellido
    );

    if (!storage || !ownerSource) {
      if (status) status.textContent = 'Este navegador no permite guardar la credencial.';
      return;
    }

    let ownerId;
    try {
      ownerId = await storage.ownerIdFromSource(ownerSource);
    } catch (error) {
      ownerId = null;
    }
    if (!ownerId) {
      if (status) status.textContent = 'Este navegador no permite guardar la credencial.';
      return;
    }

    function snapshot() {
      return {
        ownerId: ownerId,
        nombre: root.dataset.credentialNombre,
        apellido: root.dataset.credentialApellido,
        numero: root.dataset.credentialNumero,
        tipo: root.dataset.credentialTipo,
        ultimoEstado: root.dataset.credentialEstado,
        token: root.dataset.credentialToken,
        updatedAt: new Date().toISOString(),
        expiresAt: newExpiryDate(),
      };
    }

    function showSaved(record, refreshed) {
      saveButton.hidden = true;
      deleteButton.hidden = false;
      if (status) {
        status.textContent =
          (refreshed ? 'Credencial actualizada en este dispositivo. ' : 'Credencial guardada. ') +
          'Disponible hasta ' +
          formatDate(record.expiresAt) +
          '.';
      }
    }

    function showNotSaved(message) {
      saveButton.hidden = false;
      deleteButton.hidden = true;
      if (status) status.textContent = message || '';
    }

    try {
      // La navegación global inicia esta reconciliación antes de que esta
      // pantalla habilite acciones. El fallback mantiene el contrato si este
      // módulo se reutiliza alguna vez sin el script global.
      await (
        storage.ownerReady ||
        storage.reconcileAuthenticatedOwner(ownerSource)
      );
      const saved = await storage.getActiveCredential();
      if (saved && saved.ownerId === ownerId) {
        const refreshed = await storage.saveActiveCredential(snapshot());
        showSaved(refreshed, true);
      } else {
        showNotSaved('');
      }
    } catch (error) {
      showNotSaved('No pudimos acceder al almacenamiento de este navegador.');
    }

    saveConfirmButton.addEventListener('click', async function () {
      saveConfirmButton.disabled = true;
      try {
        const saved = await storage.saveActiveCredential(snapshot());
        showSaved(saved, false);
        const modalElement = document.getElementById('uni2-credential-consent');
        if (modalElement && window.bootstrap) {
          window.bootstrap.Modal.getOrCreateInstance(modalElement).hide();
        }
      } catch (error) {
        if (status) status.textContent = 'No pudimos guardar la credencial en este dispositivo.';
      } finally {
        saveConfirmButton.disabled = false;
      }
    });

    deleteButton.addEventListener('click', async function () {
      deleteButton.disabled = true;
      try {
        await storage.deleteActiveCredential();
        showNotSaved('La credencial se eliminó de este dispositivo.');
        saveButton.focus();
      } catch (error) {
        if (status) status.textContent = 'No pudimos eliminar la credencial de este dispositivo.';
      } finally {
        deleteButton.disabled = false;
      }
    });
  }

  function showEmptyOfflineCredential() {
    const loading = document.getElementById('uni2-offline-credential-loading');
    const empty = document.getElementById('uni2-offline-credential-empty');
    const content = document.getElementById('uni2-offline-credential-content');
    if (loading) loading.hidden = true;
    if (content) content.hidden = true;
    if (empty) {
      empty.hidden = false;
      const heading = empty.querySelector('h1');
      if (heading) {
        heading.setAttribute('tabindex', '-1');
        heading.focus();
      }
    }
  }

  async function initializeOfflineCredential() {
    const storage = window.Uni2PrivateStorage;
    if (!storage) {
      showEmptyOfflineCredential();
      return;
    }

    let credential;
    try {
      credential = await storage.getActiveCredential();
    } catch (error) {
      credential = null;
    }
    if (!credential) {
      showEmptyOfflineCredential();
      return;
    }

    const loading = document.getElementById('uni2-offline-credential-loading');
    const empty = document.getElementById('uni2-offline-credential-empty');
    const content = document.getElementById('uni2-offline-credential-content');
    if (loading) loading.hidden = true;
    if (empty) empty.hidden = true;
    if (content) content.hidden = false;

    setText(
      '[data-offline-credential-name]',
      credential.nombre + ' ' + credential.apellido,
      content
    );
    setText('[data-offline-credential-number]', credential.numero, content);
    setText('[data-offline-credential-type]', credential.tipo, content);
    setText('[data-offline-credential-token]', credential.token, content);
    setText('[data-offline-credential-updated]', formatDateTime(credential.updatedAt), content);
    setText('[data-offline-credential-expires]', formatDate(credential.expiresAt), content);

    const state = content.querySelector('[data-offline-credential-state]');
    if (state) {
      state.textContent = credential.ultimoEstado + ' al actualizar';
      const wasActive = credential.ultimoEstado.trim().toLowerCase() === 'activo';
      state.classList.toggle('uni2-credential-state-active', wasActive);
      state.classList.toggle('uni2-credential-state-inactive', !wasActive);
    }

    renderQRCode(
      content.querySelector('[data-offline-credential-qr]'),
      credential.token,
      'Código QR de la credencial guardada de ' +
        credential.nombre +
        ' ' +
        credential.apellido
    );

    const deleteButton = document.getElementById('uni2-offline-credential-delete');
    if (deleteButton) {
      deleteButton.addEventListener('click', async function () {
        deleteButton.disabled = true;
        try {
          await storage.deleteActiveCredential();
          showEmptyOfflineCredential();
        } catch (error) {
          deleteButton.disabled = false;
        }
      });
    }
  }

  function initialize() {
    const onlineCredential = document.getElementById('uni2-credential');
    if (onlineCredential) initializeOnlineCredential(onlineCredential);
    if (document.getElementById('uni2-offline-credential-loading')) {
      initializeOfflineCredential();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize, { once: true });
  } else {
    initialize();
  }
})();
