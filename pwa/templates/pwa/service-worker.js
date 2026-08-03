const BUILD_ID = {{ pwa_build_id_json|safe }};
const DATA_EPOCH = {{ pwa_private_data_epoch_json|safe }};
const CACHE_VERSION = `${BUILD_ID}-${DATA_EPOCH}`;
const CACHE_PREFIX = "uni2-pwa-";
const SHELL_CACHE = `${CACHE_PREFIX}shell-${CACHE_VERSION}`;
const STATIC_CACHE = `${CACHE_PREFIX}static-${CACHE_VERSION}`;
const PUBLIC_PAGES_CACHE = `${CACHE_PREFIX}public-pages-${CACHE_VERSION}`;
const PUBLIC_IMAGES_CACHE = `${CACHE_PREFIX}public-images-${CACHE_VERSION}`;
const CURRENT_CACHES = new Set([
    SHELL_CACHE,
    STATIC_CACHE,
    PUBLIC_PAGES_CACHE,
    PUBLIC_IMAGES_CACHE,
]);

const STATIC_URL = new URL({{ pwa_static_url_json|safe }}, self.location.origin);
const MEDIA_URL = new URL({{ pwa_media_url_json|safe }}, self.location.origin);
const MEDIA_URL_IS_SAME_ORIGIN = MEDIA_URL.origin === self.location.origin;
const PUBLIC_MEDIA_ORIGIN = {{ pwa_public_media_origin_json|safe }};
const OFFLINE_URL = {{ pwa_offline_url_json|safe }};
const OFFLINE_ACTION_URL = {{ pwa_offline_action_url_json|safe }};
const OFFLINE_CREDENTIAL_URL = {{ pwa_offline_credential_url_json|safe }};
const CREDENTIAL_URL = {{ pwa_credential_url_json|safe }};
const PRECACHE_URLS = JSON.parse({{ pwa_precache_urls_json_literal|safe }});
const MAX_PUBLIC_PAGES = 30;
const MAX_PUBLIC_IMAGES = 60;
const MAX_RUNTIME_STATIC_FILES = 80;

async function trimCache(cacheName, maximumEntries) {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();
    const excess = keys.length - maximumEntries;

    if (excess <= 0) {
        return;
    }

    await Promise.all(keys.slice(0, excess).map((request) => cache.delete(request)));
}

function isSameOriginStatic(url) {
    return url.origin === self.location.origin && url.pathname.startsWith(STATIC_URL.pathname);
}

function isAllowedPublicImage(url) {
    const isSameOriginMedia = (
        MEDIA_URL_IS_SAME_ORIGIN &&
        url.origin === self.location.origin &&
        url.pathname.startsWith(MEDIA_URL.pathname)
    );
    const isConfiguredPublicMedia = (
        PUBLIC_MEDIA_ORIGIN !== "" &&
        url.origin === PUBLIC_MEDIA_ORIGIN
    );
    return isSameOriginMedia || isConfiguredPublicMedia;
}

function isCacheableStaticResponse(response) {
    return response && response.ok && response.status === 200 && response.type === "basic";
}

function isCacheablePublicImageResponse(response, url) {
    if (!response || !isAllowedPublicImage(url)) {
        return false;
    }
    if (response.type === "opaque") {
        return PUBLIC_MEDIA_ORIGIN !== "" && url.origin === PUBLIC_MEDIA_ORIGIN;
    }
    return (
        response.ok &&
        response.status === 200 &&
        (response.type === "basic" || response.type === "cors")
    );
}

function isExplicitlyPublicPage(response) {
    return (
        response &&
        response.ok &&
        response.status === 200 &&
        response.type === "basic" &&
        response.headers.get("X-Uni2-PWA-Cacheable") === "public"
    );
}

async function shellResponse(url) {
    const cached = await caches.match(url, {cacheName: SHELL_CACHE});
    return cached || Response.error();
}

async function cacheFirstStatic(request) {
    const shellCached = await caches.match(request, {cacheName: SHELL_CACHE});
    if (shellCached) {
        return shellCached;
    }

    const cached = await caches.match(request, {cacheName: STATIC_CACHE});
    if (cached) {
        return cached;
    }

    const response = await fetch(request);
    if (isCacheableStaticResponse(response)) {
        const cache = await caches.open(STATIC_CACHE);
        await cache.put(request, response.clone());
        await trimCache(STATIC_CACHE, MAX_RUNTIME_STATIC_FILES);
    }
    return response;
}

async function fetchAndCachePublicImage(request, url) {
    const response = await fetch(request);
    if (isCacheablePublicImageResponse(response, url)) {
        const cache = await caches.open(PUBLIC_IMAGES_CACHE);
        await cache.put(request, response.clone());
        await trimCache(PUBLIC_IMAGES_CACHE, MAX_PUBLIC_IMAGES);
    }
    return response;
}

function staleWhileRevalidatePublicImage(event, request, url) {
    const cachedResponse = caches.match(request, {cacheName: PUBLIC_IMAGES_CACHE});
    const networkResponse = fetchAndCachePublicImage(request, url);

    event.waitUntil(networkResponse.catch(() => undefined));
    return cachedResponse.then((cached) => cached || networkResponse);
}

async function networkFirstNavigation(request) {
    try {
        const response = await fetch(request);
        if (isExplicitlyPublicPage(response)) {
            const cache = await caches.open(PUBLIC_PAGES_CACHE);
            await cache.put(request, response.clone());
            await trimCache(PUBLIC_PAGES_CACHE, MAX_PUBLIC_PAGES);
        }
        return response;
    } catch (error) {
        const requestUrl = new URL(request.url);
        if (requestUrl.pathname === CREDENTIAL_URL) {
            return shellResponse(OFFLINE_CREDENTIAL_URL);
        }

        const cached = await caches.match(request, {cacheName: PUBLIC_PAGES_CACHE});
        if (cached) {
            return cached;
        }
        return shellResponse(OFFLINE_URL);
    }
}

async function networkOnlyMutation(request) {
    try {
        return await fetch(request);
    } catch (error) {
        return shellResponse(OFFLINE_ACTION_URL);
    }
}

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(SHELL_CACHE).then((cache) => cache.addAll(PRECACHE_URLS))
    );
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => Promise.all(
                cacheNames
                    .filter((cacheName) => (
                        cacheName.startsWith(CACHE_PREFIX) && !CURRENT_CACHES.has(cacheName)
                    ))
                    .map((cacheName) => caches.delete(cacheName))
            ))
            .then(() => self.clients.claim())
    );
});

self.addEventListener("message", (event) => {
    if (event.data && event.data.type === "SKIP_WAITING") {
        self.skipWaiting();
    }
});

self.addEventListener("fetch", (event) => {
    const request = event.request;
    const url = new URL(request.url);

    if (request.method === "GET" && request.destination === "image" && isAllowedPublicImage(url)) {
        event.respondWith(staleWhileRevalidatePublicImage(event, request, url));
        return;
    }

    if (url.origin !== self.location.origin) {
        return;
    }

    if (request.method !== "GET") {
        if (request.mode === "navigate") {
            event.respondWith(networkOnlyMutation(request));
        }
        return;
    }

    if (request.mode === "navigate") {
        event.respondWith(networkFirstNavigation(request));
        return;
    }

    if (isSameOriginStatic(url)) {
        event.respondWith(cacheFirstStatic(request));
    }
});
