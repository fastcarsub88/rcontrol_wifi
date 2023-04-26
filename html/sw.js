var farmname = location.pathname.replace('/sw.js','')
farmname = farmname.replace('/','')
var cacheName = farmname+'rctlv56';
var filesToCache = [
  "index.js?"+cacheName,
  "style.css?"+cacheName,
  "manifest.json?"+cacheName,
  "index.html?"+cacheName,
  "img/maskable_icon_x192.png?"+cacheName,
  "img/maskable_icon_x512.png?"+cacheName,
  "img/apple-touch-icon.png?"+cacheName,
  "img/rcontrol_icon.png?"+cacheName,
  "img/favicon-16x16.png?"+cacheName,
  "img/favicon-32x32.png?"+cacheName
]
self.addEventListener('install', function(e) {
  console.log('installing sw '+cacheName);
  self.skipWaiting();
  e.waitUntil(
    caches.open(cacheName).then(function(cache) {
      cache.addAll(filesToCache);
    })
  );
});

self.addEventListener('activate',  event => {
  event.waitUntil(
    caches.keys().then(keys=> Promise.all(
      keys.map(key=>{
        if (key.includes(farmname)) {
          if (key != cacheName) {
            return caches.delete(key);
          }
        }
      })
    )).then(()=>{
      console.log(cacheName+' is activated');
    })
  );
});

self.addEventListener(
  'fetch',
  event => {
    var a = event.request.url
    var b = a.substr(a.lastIndexOf('/'))
    if (b == '/api') { return }
    if (b == '/') {
      event.respondWith(caches.match(a + 'index.html?' + cacheName))
      return
    }
    event.respondWith(caches.match(a + "?" + cacheName))
  }
)
