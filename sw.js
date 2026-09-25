// Garde une copie de l'app pour qu'elle s'ouvre sans connexion.
// En ligne, on prend toujours la version la plus récente (et on met la copie à jour).
const CACHE = 'factures-v1';
const FICHIERS = [
  './', './index.html', './manifest.webmanifest', './icone-180.png', './icone-192.png', './icone-512.png',
  'https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js'
];

self.addEventListener('install', e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(FICHIERS))));

self.addEventListener('activate', e => e.waitUntil(
  caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
));

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request)
      .then(r => { const copie = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copie)); return r; })
      .catch(() => caches.match(e.request, {ignoreSearch: true}))
  );
});
