# config.py - مدیریت متمرکز تنظیمات برای تمام PaaS ها
import os
import secrets
from pathlib import Path

class Config:
    """تنظیمات مرکزی پروژه - سازگار با تمام سرویس‌های PaaS"""
    
    # ====== متغیرهای اصلی ======
    PORT: int = int(os.environ.get("PORT", 8000))
    
    # ====== دامنه عمومی ======
    # اولویت: PUBLIC_DOMAIN > RAILWAY_PUBLIC_DOMAIN > RENDER_EXTERNAL_URL > KOYEB_PUBLIC_DOMAIN > HOSTNAME > localhost
    PUBLIC_DOMAIN: str = (
        os.environ.get("PUBLIC_DOMAIN") or
        os.environ.get("RAILWAY_PUBLIC_DOMAIN") or
        os.environ.get("RENDER_EXTERNAL_URL", "").replace("https://", "") or
        os.environ.get("KOYEB_PUBLIC_DOMAIN") or
        os.environ.get("FLY_APP_NAME", "") + ".fly.dev" if os.environ.get("FLY_APP_NAME") else "" or
        os.environ.get("HOSTNAME", "localhost")
    )
    
    # ====== دایرکتوری داده ======
    # اولویت: DATA_DIR > ./data (در اکثر PaaS ها persistent است)
    DATA_DIR: Path = Path(os.environ.get("DATA_DIR", "./data"))
    
    # ====== سکرت ======
    # اولویت: SECRET_KEY > تولید خودکار
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "")
    
    # ====== آپدیتر ======
    UPDATE_MANIFEST_URL: str = os.environ.get(
        "UPDATE_MANIFEST_URL",
        "https://rvg-update.arvin341az.workers.dev/version.json"
    )
    
    # ====== سرویس مرکزی ======
    CENTRAL_URL: str = os.environ.get(
        "CENTRAL_URL",
        "https://panel-rvg.arvin341az.workers.dev"
    )
    
    # ====== تنظیمات پیشرفته ======
    WORKERS: int = int(os.environ.get("WORKERS", 1))
    RELAY_BUF: int = int(os.environ.get("RELAY_BUF", 256 * 1024))
    SESSION_TTL: int = int(os.environ.get("SESSION_TTL", 60 * 60 * 24 * 7))
    
    @classmethod
    def ensure_dirs(cls) -> Path:
        """اطمینان از وجود دایرکتوری‌های مورد نیاز"""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        return cls.DATA_DIR
    
    @classmethod
    def get_host(cls) -> str:
        """دریافت دامنه‌ی عمومی با fallback های متعدد"""
        host = cls.PUBLIC_DOMAIN
        if not host or host == "localhost":
            # اگر هیچ دامنه‌ای تنظیم نشده، از localhost استفاده کن
            return "localhost"
        return host

# نمونه singleton برای استفاده در سراسر پروژه
config = Config()
