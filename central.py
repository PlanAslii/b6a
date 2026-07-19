# central.py — ارتباط با سرویس مرکزی روی Cloudflare Worker
# اصلاح شده برای جلوگیری از circular import
import os
import asyncio
import httpx

from config import config
from updater import get_current_version

CENTRAL_URL = config.CENTRAL_URL

# این متغیرها بعداً از main ست می‌شوند
_AUTH = None
_get_host = None


def init_central(auth, get_host_func):
    """تنظیم وابستگی‌های دایره‌ای - باید از main صدا زده شود"""
    global _AUTH, _get_host
    _AUTH = auth
    _get_host = get_host_func


async def register_instance():
    if not CENTRAL_URL:
        return
    if _AUTH is None or _get_host is None:
        return
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            await c.post(f"{CENTRAL_URL}/api/register", json={
                "domain": _get_host(),
                "version": get_current_version(),
                "panel_password_hash": _AUTH["password_hash"],
                "description": "RVG Gateway instance",
            })
    except Exception:
        pass


async def heartbeat_loop():
    while True:
        await register_instance()
        await asyncio.sleep(300)


async def fetch_announcements():
    if not CENTRAL_URL:
        return []
    if _get_host is None:
        return []
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"{CENTRAL_URL}/api/announcements", params={"domain": _get_host()})
            r.raise_for_status()
            return r.json().get("announcements", [])
    except Exception:
        return []


async def report_announcement_views(ids: list[str]):
    if not CENTRAL_URL or not ids:
        return
    if _get_host is None:
        return
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            await c.post(f"{CENTRAL_URL}/api/announcements/view", json={
                "domain": _get_host(),
                "ids": ids,
            })
    except Exception:
        pass


async def fetch_support_messages():
    if not CENTRAL_URL:
        return [], False
    if _get_host is None:
        return [], False
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"{CENTRAL_URL}/api/support/messages", params={"domain": _get_host()})
            r.raise_for_status()
            d = r.json()
            return d.get("messages", []), bool(d.get("blocked", False))
    except Exception:
        return [], False


async def send_support_message(body: str) -> dict:
    if not CENTRAL_URL:
        return {"ok": False, "blocked": False, "error": "CENTRAL_URL تنظیم نشده"}
    if _get_host is None:
        return {"ok": False, "blocked": False, "error": "سیستم آماده نیست"}
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(f"{CENTRAL_URL}/api/support/send", json={"domain": _get_host(), "body": body})
            if r.status_code == 403:
                return {"ok": False, "blocked": True}
            if r.status_code != 200:
                return {"ok": False, "blocked": False, "error": f"HTTP {r.status_code}: {r.text[:200]}"}
            return {"ok": True, "blocked": False}
    except Exception as e:
        return {"ok": False, "blocked": False, "error": str(e)}


async def close_support_chat() -> bool:
    return False
