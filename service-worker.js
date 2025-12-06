// Service Worker for Metal Prices PWA
const CACHE_NAME = 'metal-prices-v1';

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
  // Skip caching for external API requests - always fetch fresh data
  if (event.request.url.includes('goldapi.io') || event.request.url.includes('metals.dev')) {
    return fetch(event.request);
  }
  
  // For local assets, use cache first, then network
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      })
  );
});

// Activate event - clean up old caches
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
    })
  );
});

