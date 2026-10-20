// Offline support: app files come from cache; prices.json is fetched fresh when online, cached copy when offline.
const CACHE = "sdc-v7";
const FILES = ["./", "index.html", "prices.json", "manifest.webmanifest", "icon-180.png", "icon-192.png", "icon-512.png",
  "badges/30th-celebration.png", "badges/ascended-heroes.png", "badges/black-bolt.png", "badges/chaos-rising.png", "badges/destined-rivals.png", "badges/journey-together.png", "badges/mega-evolution.png", "badges/perfect-order.png", "badges/phantasmal-flames.png", "badges/pitch-black.png", "badges/prismatic-evolutions.png", "badges/surging-sparks.png", "badges/white-flare.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES))); self.skipWaiting(); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin) return;
  const fresh = url.pathname.endsWith("prices.json") || url.pathname.endsWith("/") || url.pathname.endsWith("index.html");
  if (fresh) {
    e.respondWith(fetch(e.request).then(r => { const c = r.clone(); caches.open(CACHE).then(x => x.put(e.request, c)); return r; })
      .catch(() => caches.match(e.request, { ignoreSearch: true })));
  } else {
    e.respondWith(caches.match(e.request).then(m => m || fetch(e.request)));
  }
});
