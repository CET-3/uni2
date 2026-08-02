// Almacenamiento privado y explícito para la única excepción offline del MVP:
// la credencial. No se guardan páginas autenticadas, cuotas ni deuda.
(function () {
  'use strict';

  const DB_NAME = 'uni2-private-v1';
  const DB_VERSION = 1;
  const STORE_NAME = 'credentials';
  const ACTIVE_KEY = 'active';
  const SCHEMA_VERSION = 1;
  const CHANNEL_NAME = 'uni2-private-data';

  function openDatabase() {
    return new Promise(function (resolve, reject) {
      if (!('indexedDB' in window)) {
        reject(new Error('IndexedDB no está disponible.'));
        return;
      }

      const request = window.indexedDB.open(DB_NAME, DB_VERSION);
      request.onupgradeneeded = function () {
        const database = request.result;
        if (!database.objectStoreNames.contains(STORE_NAME)) {
          database.createObjectStore(STORE_NAME, { keyPath: 'key' });
        }
      };
      request.onsuccess = function () {
        resolve(request.result);
      };
      request.onerror = function () {
        reject(request.error || new Error('No se pudo abrir IndexedDB.'));
      };
    });
  }

  async function useStore(mode, operation) {
    const database = await openDatabase();
    try {
      return await new Promise(function (resolve, reject) {
        const transaction = database.transaction(STORE_NAME, mode);
        const store = transaction.objectStore(STORE_NAME);
        let result;

        transaction.oncomplete = function () {
          resolve(result);
        };
        transaction.onerror = function () {
          reject(transaction.error || new Error('Falló una operación de almacenamiento.'));
        };
        transaction.onabort = function () {
          reject(transaction.error || new Error('Se canceló una operación de almacenamiento.'));
        };

        result = operation(store);
      });
    } finally {
      database.close();
    }
  }

  function requestResult(request) {
    return new Promise(function (resolve, reject) {
      request.onsuccess = function () {
        resolve(request.result || null);
      };
      request.onerror = function () {
        reject(request.error || new Error('No se pudo leer la credencial.'));
      };
    });
  }

  function isExpired(record) {
    if (!record || !record.expiresAt) return true;
    const expiresAt = Date.parse(record.expiresAt);
    return !Number.isFinite(expiresAt) || expiresAt <= Date.now();
  }

  function notifyOtherTabs(type) {
    if (!('BroadcastChannel' in window)) return;
    const channel = new BroadcastChannel(CHANNEL_NAME);
    channel.postMessage({ type: type });
    channel.close();
  }

  async function getActiveCredential() {
    const record = await useStore('readonly', function (store) {
      return requestResult(store.get(ACTIVE_KEY));
    });

    if (record && isExpired(record)) {
      await deleteActiveCredential();
      return null;
    }
    if (!record || record.schemaVersion !== SCHEMA_VERSION) return null;
    return record;
  }

  async function saveActiveCredential(credential) {
    const record = {
      key: ACTIVE_KEY,
      schemaVersion: SCHEMA_VERSION,
      ownerId: String(credential.ownerId),
      nombre: String(credential.nombre),
      apellido: String(credential.apellido),
      numero: String(credential.numero),
      tipo: String(credential.tipo),
      ultimoEstado: String(credential.ultimoEstado),
      token: String(credential.token),
      updatedAt: String(credential.updatedAt),
      expiresAt: String(credential.expiresAt),
    };

    await useStore('readwrite', function (store) {
      store.put(record);
    });
    notifyOtherTabs('credential-updated');
    return record;
  }

  async function deleteActiveCredential(options) {
    await useStore('readwrite', function (store) {
      store.delete(ACTIVE_KEY);
    });
    if (!options || options.notify !== false) {
      notifyOtherTabs('credential-deleted');
    }
  }

  async function ownerIdFromSource(ownerSource) {
    const source = String(ownerSource || '').trim();
    if (!source || !window.crypto || !window.crypto.subtle || !window.TextEncoder) {
      return null;
    }

    const material = new TextEncoder().encode(
      'uni2-pwa-owner-v1|' + window.location.origin + '|' + source
    );
    const digest = await window.crypto.subtle.digest('SHA-256', material);
    return Array.from(new Uint8Array(digest))
      .map(function (byte) {
        return byte.toString(16).padStart(2, '0');
      })
      .join('');
  }

  // Un body anónimo puede ser el shell offline o una sesión vencida: en esos
  // casos se conserva la copia consentida. Solo un usuario autenticado distinto
  // permite concluir que hay que eliminarla.
  async function reconcileAuthenticatedOwner(ownerSource) {
    const ownerId = await ownerIdFromSource(ownerSource);
    if (!ownerId) return null;

    const credential = await getActiveCredential();
    if (credential && credential.ownerId !== ownerId) {
      await deleteActiveCredential();
      return null;
    }
    return credential;
  }

  if ('BroadcastChannel' in window) {
    const channel = new BroadcastChannel(CHANNEL_NAME);
    channel.addEventListener('message', function (event) {
      if (event.data && event.data.type === 'credential-deleted') {
        deleteActiveCredential({ notify: false }).catch(function () {
          // La pestaña actual volverá a verificar el dato antes de mostrarlo.
        });
      }
    });
  }

  window.Uni2PrivateStorage = {
    databaseName: DB_NAME,
    storeName: STORE_NAME,
    activeKey: ACTIVE_KEY,
    getActiveCredential: getActiveCredential,
    saveActiveCredential: saveActiveCredential,
    deleteActiveCredential: deleteActiveCredential,
    ownerIdFromSource: ownerIdFromSource,
    reconcileAuthenticatedOwner: reconcileAuthenticatedOwner,
  };
})();
