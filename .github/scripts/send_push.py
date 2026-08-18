# -*- coding: utf-8 -*-
"""GitHub Actions 클라우드 발송기 — PC가 꺼져 있어도 알림을 보낸다.
allw_pull_due(원자적 클레임, 15분+ 오래된 건 미발송 마감)로 due 알림을 받아 웹푸시.
anon 키는 공개용(앱에도 들어있음). PUSH_SECRET 만 GitHub Secret."""
import os, json, urllib.request, urllib.error
from pywebpush import webpush, WebPushException

SUPA = "https://tysrlmjbnkyswqjtfeuc.supabase.co"
ANON = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR5c3"
        "JsbWpibmt5c3dxanRmZXVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI4ODU3MjgsImV4cCI6"
        "MjA5ODQ2MTcyOH0.HKeQ0NtIcj_YEGlsElzmC21D22gl6fYYOgSX5za9nCA")
SECRET = os.environ.get("PUSH_SECRET", "")


def rpc(fn, args):
    body = json.dumps(args).encode()
    req = urllib.request.Request(
        SUPA + "/rest/v1/rpc/" + fn, data=body, method="POST",
        headers={"Content-Type": "application/json", "apikey": ANON,
                 "Authorization": "Bearer " + ANON})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def main():
    res = rpc("allw_pull_due", {"p_secret": SECRET, "p_limit": 100})
    if not res.get("ok"):
        print("pull_due 실패:", res.get("error"))
        return
    items = res.get("items") or []
    if not items:
        print("보낼 알림 없음")
        return
    priv = json.loads(res["vapidPrivate"])["d"]
    subject = res.get("vapidSubject") or "mailto:koreanobo@gmail.com"
    sent = 0
    for it in items:
        payload = json.dumps({"title": it["title"], "body": it["body"],
                              "url": it.get("url") or "./index.html"})
        try:
            webpush(subscription_info={"endpoint": it["endpoint"],
                                       "keys": {"p256dh": it["p256dh"], "auth": it["auth"]}},
                    data=payload, vapid_private_key=priv,
                    vapid_claims={"sub": subject}, ttl=3600)
            sent += 1
        except WebPushException as e:
            code = getattr(getattr(e, "response", None), "status_code", None)
            if code in (404, 410):
                try:
                    rpc("allw_drop_sub", {"p_secret": SECRET, "p_endpoint": it["endpoint"]})
                except Exception:
                    pass
            else:
                print("발송 실패", code)
        except Exception as e:  # noqa: BLE001
            print("오류", str(e)[:80])
    print(f"발송 {sent}/{len(items)}")


if __name__ == "__main__":
    main()
