const cacheName = 'gryans-finance-app-cache-v1';
const cacheFiles = [
  '/',
  '/static/img/icon/android-icon-192x192.png',
  '/static/img/icon/apple-icon-57x57.png',
  '/static/img/icon/apple-icon-60x60.png',
  '/static/img/icon/apple-icon-72x72.png',
  '/static/img/icon/apple-icon-76x76.png',
  '/static/img/icon/apple-icon-114x114.png',
  '/static/img/icon/apple-icon-120x120.png',
  '/static/img/icon/apple-icon-144x144.png',
  '/static/img/icon/apple-icon-152x152.png',
  '/static/img/icon/apple-icon-180x180.png',
  '/static/img/icon/favicon-32x32.png',
  '/static/img/icon/favicon-96x96.png',
  '/static/img/icon/favicon-16x16.png',
  '/static/img/icons/icon-48x48.ico',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(cacheName).then((cache) => {
      return cache.addAll(cacheFiles);
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((thisCacheName) => {
          if (thisCacheName !== cacheName) {
            return caches.delete(thisCacheName);
          }
        })
      );
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) {
        return response;
      }
      return fetch(event.request);
    })
  );
});
