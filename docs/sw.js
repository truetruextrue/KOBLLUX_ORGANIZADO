self.addEventListener("install", (event) => {
  console.log("SW instalado");
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  console.log("SW ativo");
});

self.addEventListener("fetch", (event) => {
  // Pass-through simples (sem cache)
  event.respondWith(fetch(event.request));
});
