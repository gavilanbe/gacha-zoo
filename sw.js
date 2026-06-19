const C='gachazoo-v3';
self.addEventListener('install',e=>{
  e.waitUntil(caches.open(C).then(c=>c.addAll(['./','./index.html','./manifest.json','./icon-192.png','./icon-512.png','./icon-180.png'])));
  self.skipWaiting();
});
self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET') return;
  const u=new URL(e.request.url);
  const isNav = e.request.mode==='navigate' ||
    (u.origin===location.origin && (u.pathname==='/'||u.pathname.endsWith('/index.html')));
  if(isNav){
    // la página SIEMPRE intenta red primero; la caché es solo paracaídas offline
    e.respondWith(
      fetch(e.request).then(r=>{
        const cp=r.clone(); caches.open(C).then(c=>c.put('./index.html',cp));
        return r;
      }).catch(()=>caches.match('./index.html'))
    );
    return;
  }
  const cacheable = u.origin===location.origin || /jsdelivr\.net|gstatic\.com|googleapis\.com/.test(u.host);
  e.respondWith(
    caches.match(e.request).then(hit=> hit || fetch(e.request).then(r=>{
      if(r.ok && cacheable){ const cp=r.clone(); caches.open(C).then(c=>c.put(e.request,cp)); }
      return r;
    }).catch(()=>hit))
  );
});
