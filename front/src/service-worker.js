import { build, files, version } from '$service-worker';

const CACHE = `cache-${version}`;
const ASSETS = [...build, ...files];

self.addEventListener('install', (event) => {
  async function addFilesToCache() {
    const cache = await caches.open(CACHE);
    await cache.addAll(ASSETS);
  }
  event.waitUntil(addFilesToCache());
});

self.addEventListener('activate', (event) => {
  async function deleteOldCaches() {
    for (const key of await caches.keys()) {
      if (key !== CACHE) await caches.delete(key);
    }
  }
  event.waitUntil(deleteOldCaches());
});

self.addEventListener('fetch', (event) => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;

  async function respond() {
    const url = new URL(event.request.url);
    const cache = await caches.open(CACHE);

    // Skip API requests - let them go directly to the network
    if (url.pathname.startsWith('/api/') || url.hostname !== location.hostname) {
      try {
        return await fetch(event.request);
      } catch (error) {
        // For API requests that fail, return a proper error response
        return new Response(
          JSON.stringify({ error: 'Network error', offline: true }), 
          {
            status: 503,
            statusText: 'Service Unavailable',
            headers: { 'Content-Type': 'application/json' }
          }
        );
      }
    }

    // Handle static assets
    if (ASSETS.includes(url.pathname)) {
      const cachedResponse = await cache.match(event.request);
      if (cachedResponse) {
        return cachedResponse;
      }
    }

    // Try network first, then cache
    try {
      const response = await fetch(event.request);
      if (response.status === 200) {
        cache.put(event.request, response.clone());
      }
      return response;
    } catch (error) {
      // Try to get from cache
      const cachedResponse = await cache.match(event.request);
      if (cachedResponse) {
        return cachedResponse;
      }
      
      // If nothing in cache and network failed, return proper offline response
      if (event.request.destination === 'document') {
        // For page requests, try to return cached index.html or create offline page
        const offlineResponse = await cache.match('/') || await cache.match('/index.html');
        return offlineResponse || new Response(
          '<!DOCTYPE html><html><head><title>Offline</title></head><body><h1>Offline</h1><p>Please check your internet connection.</p></body></html>',
          { 
            status: 503, 
            statusText: 'Service Unavailable',
            headers: { 'Content-Type': 'text/html' }
          }
        );
      }
      
      // For other requests, return a proper error response
      return new Response(
        'Offline', 
        { 
          status: 503, 
          statusText: 'Service Unavailable',
          headers: { 'Content-Type': 'text/plain' }
        }
      );
    }
  }

  event.respondWith(respond());
});