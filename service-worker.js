// Service Worker for Metal Prices PWA
const CACHE_NAME = 'metal-prices-v3';

// Get the base path from the service worker's scope
const getBasePath = () => {
  const path = self.location.pathname;
  const basePath = path.substring(0, path.lastIndexOf('/') + 1);
  return basePath;
};

const basePath = getBasePath();
const urlsToCache = [
  basePath,
  basePath + 'index.html',
  basePath + 'manifest.json'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  // Skip caching for external requests (APMEX, CORS proxies) - always fetch fresh data
  if (event.request.url.includes('apmex.com') || event.request.url.includes('allorigins.win')) {
    return fetch(event.request);
  }
  
  // For local assets, use network first to get latest version, then cache
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Cache the response for future use
        const responseToCache = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
        return response;
      })
      .catch(() => {
        // If network fails, try cache
        return caches.match(event.request);
      })
  );
});

// Activate event - clean up old caches and skip waiting
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      // Take control of all pages immediately
      return self.clients.claim();
    })
  );
});

// Listen for skip waiting message
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

