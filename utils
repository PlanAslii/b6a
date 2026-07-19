# utils.py - توابع کمکی مشترک
import hashlib
import secrets
import time
from datetime import datetime
from typing import Optional
from urllib.parse import quote

from config import config

IRAN_TZ = None
try:
    from zoneinfo import ZoneInfo
    IRAN_TZ = ZoneInfo("Asia/Tehran")
except ImportError:
    IRAN_TZ = None

# ====== توابع رمزنگاری ======

def hash_password(pw: str) -> str:
    """هش کردن رمز عبور با salt"""
    return hashlib.sha256(f"{pw}{config.SECRET_KEY}".encode()).hexdigest()

def generate_uuid() -> str:
    """تولید UUID تصادفی"""
    h = secrets.token_hex(16)
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"

# ====== توابع زمان ======

def now_ir():
    """زمان فعلی به وقت ایران"""
    if IRAN_TZ:
        return datetime.now(IRAN_TZ)
    return datetime.now()

def uptime(start_time: float) -> str:
    """محاسبه آپتایم از زمان شروع"""
    secs = int(time.time() - start_time)
    h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

# ====== توابع فرمتینگ ======

def fmt_bytes(b: int) -> str:
    """فرمت کردن بایت به صورت خوانا"""
    if b < 1024:
        return f"{b} B"
    if b < 1024**2:
        return f"{b/1024:.1f} KB"
    if b < 1024**3:
        return f"{b/1024**2:.2f} MB"
    return f"{b/1024**3:.2f} GB"

def parse_size_to_bytes(value: float, unit: str) -> int:
    """تبدیل مقدار و واحد به بایت"""
    unit = unit.upper()
    if unit == "GB":
        return int(value * 1024 ** 3)
    if unit == "MB":
        return int(value * 1024 ** 2)
    if unit == "KB":
        return int(value * 1024)
    return int(value)

def time_ago_fa(ts: float) -> str:
    """نمایش زمان گذشته به فارسی"""
    diff = time.time() - ts
    if diff < 60:
        return "همین الان"
    if diff < 3600:
        return f"{int(diff/60)} دقیقه پیش"
    if diff < 86400:
        return f"{int(diff/3600)} ساعت پیش"
    if diff < 2592000:
        return f"{int(diff/86400)} روز پیش"
    return datetime.fromtimestamp(ts).strftime("%Y/%m/%d")

# ====== توابع VLESS ======

def generate_vless_link(uuid: str, host: str, remark: str = "RVG", protocol: str = "vless-ws") -> str:
    """تولید لینک VLESS با پروتکل مشخص"""
    PROTOCOLS = ("vless-ws", "xhttp-packet-up", "xhttp-stream-up", "xhttp-stream-one")
    DEFAULT_PROTOCOL = "vless-ws"
    
    if protocol == "vless-ws":
        path = f"/ws/{uuid}"
        params = {
            "encryption": "none",
            "security": "tls",
            "type": "ws",
            "host": host,
            "path": path,
            "sni": host,
            "fp": "chrome",
            "alpn": "http/1.1",
        }
    else:
        mode = protocol.replace("xhttp-", "")
        path = f"/xhttp-siz10/{mode}/{uuid}"
        params = {
            "encryption": "none",
            "security": "tls",
            "type": "xhttp",
            "mode": mode,
            "host": host,
            "path": path,
            "sni": host,
            "fp": "chrome",
            "alpn": "h2,http/1.1",
        }
    
    query = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
    return f"vless://{uuid}@{host}:443?{query}#{quote(remark)}"

# ====== توابع اعتبارسنجی ======

def is_link_expired(link: dict) -> bool:
    """بررسی انقضای لینک"""
    exp = link.get("expires_at")
    if not exp:
        return False
    try:
        return datetime.now() > datetime.fromisoformat(exp)
    except Exception:
        return False

def is_link_allowed(link: Optional[dict]) -> bool:
    """بررسی مجاز بودن لینک (فعال، منقضی نشده، سهمیه باقی)"""
    if link is None:
        return False
    if not link.get("active", True):
        return False
    if is_link_expired(link):
        return False
    lb = link.get("limit_bytes", 0)
    if lb > 0 and link.get("used_bytes", 0) >= lb:
        return False
    return True

# ====== توابع کلاینت IP ======

def client_ip_from_request(request) -> str:
    """دریافت IP واقعی کلاینت با احتساب هدرهای پراکسی"""
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "نامشخص"
