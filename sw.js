/* 용돈미션 서비스워커 — 설치형(PWA) + 푸시 알림 */
const VER = "1.0.5";

self.addEventListener("install", e => self.skipWaiting());
self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) await caches.delete(k);
    await self.clients.claim();
  })());
});

/* 네트워크 통과 (앱은 온라인 전용 — 캐시로 인한 구버전 고착을 막는다) */
self.addEventListener("fetch", e => {
  e.respondWith(fetch(e.request).catch(() =>
    new Response("<h3 style='font-family:sans-serif;text-align:center;margin-top:40vh'>인터넷 연결을 확인해 주세요 📶</h3>",
      { headers: { "Content-Type": "text/html; charset=utf-8" } })
  ));
});

self.addEventListener("push", e => {
  let d = {};
  try { d = e.data.json(); } catch (err) { d = { title: "용돈미션", body: e.data && e.data.text() }; }
  const isAlarm = /5분|남았|끝/.test(d.title || "");
  e.waitUntil(self.registration.showNotification(d.title || "용돈미션", {
    body: d.body || "",
    icon: "icon-192.png",
    badge: "icon-192.png",
    data: { url: d.url || "./index.html" },
    tag: d.tag || undefined,
    renotify: !!d.tag,
    silent: false,
    requireInteraction: isAlarm,                       // 5분 알림은 계속 떠 있게
    vibrate: isAlarm ? [400, 200, 400, 200, 400] : [200, 100, 200]
  }));
});

self.addEventListener("notificationclick", e => {
  e.notification.close();
  e.waitUntil((async () => {
    const all = await clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const c of all) { if ("focus" in c) return c.focus(); }
    return clients.openWindow("./index.html");
  })());
});
