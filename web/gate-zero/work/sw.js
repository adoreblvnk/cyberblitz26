const CACHE = 'gate-zero-v5';

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll([
      '/archive/flight-prior.json',
      '/archive/flight.json',
      '/dispatch'
    ]))
  );
});
