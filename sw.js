// Offline cache: app shell + data (network-first), mushaf pages and fonts (cache-first once fetched).
const SHELL = "waqf-shell-v12", RUNTIME = "waqf-runtime-v2";
const SHELL_FILES = ["./", "index.html", "manifest.webmanifest", "data/waqf.json", "data/text_preview.json", "icon-192.png", "icon-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(SHELL_FILES)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== SHELL && k !== RUNTIME).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET") return;
  const isRemote = /cdn\.jsdelivr\.net|static-cdn\.tarteel\.ai|fonts\.(googleapis|gstatic)\.com/.test(url.host)
    || (url.origin === location.origin && url.pathname.includes("/data/q4/"));  // fonts and fixed page layouts never change
  if (isRemote) {
    e.respondWith(caches.open(RUNTIME).then(async c => {
      const hit = await c.match(e.request);
      if (hit) return hit;
      const res = await fetch(e.request);
      if (res.ok || res.type === "opaque") c.put(e.request, res.clone());
      return res;
    }));
    return;
  }
  if (url.origin === location.origin) {
    e.respondWith(fetch(e.request).then(res => {
      const copy = res.clone(); caches.open(SHELL).then(c => c.put(e.request, copy)); return res;
    }).catch(() => caches.match(e.request)));
  }
});
