# storage.py - مدیریت ذخیره‌سازی پایدار با fallback به in-memory
import json
import asyncio
import secrets
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

from config import config

class Storage:
    """مدیریت ذخیره‌سازی داده‌ها با پشتیبانی از persistent storage"""
    
    def __init__(self):
        self.data_dir = config.DATA_DIR
        self.state_file = self.data_dir / "rvg_state.json"
        self.secret_file = self.data_dir / ".rvg_secret"
        self.history_file = self.data_dir / "update_history.json"
        self._lock = asyncio.Lock()
        self._cache: Dict[str, Any] = {}
        self._in_memory: Dict[str, Any] = {}
        self._use_persistent = True
    
    async def ensure_dirs(self):
        """اطمینان از وجود دایرکتوری‌ها"""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            # تست نوشتن
            test_file = self.data_dir / ".write_test"
            test_file.write_text("ok")
            test_file.unlink()
            self._use_persistent = True
        except Exception:
            self._use_persistent = False
            print("[STORAGE] ⚠️ Persistent storage not available, using in-memory only")
        return self.data_dir
    
    async def load_state(self) -> Dict[str, Any]:
        """بارگذاری state از فایل یا حافظه"""
        if not self._use_persistent:
            return self._in_memory.get("state", {})
        
        try:
            if self.state_file.exists():
                async with self._lock:
                    with open(self.state_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self._cache["state"] = data
                    return data
        except Exception as e:
            print(f"[STORAGE] ⚠️ Error loading state: {e}")
        
        # Fallback به in-memory
        return self._in_memory.get("state", {})
    
    async def save_state(self, data: Dict[str, Any]) -> bool:
        """ذخیره state در فایل یا حافظه"""
        self._in_memory["state"] = data
        
        if not self._use_persistent:
            return True
        
        async with self._lock:
            try:
                self.data_dir.mkdir(parents=True, exist_ok=True)
                tmp = self.state_file.with_suffix(".tmp")
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                tmp.replace(self.state_file)
                self._cache["state"] = data
                return True
            except Exception as e:
                print(f"[STORAGE] ⚠️ Error saving state: {e}")
                return False
    
    def get_secret(self) -> str:
        """دریافت یا ایجاد secret key"""
        # اولویت 1: متغیر محیطی
        if config.SECRET_KEY:
            return config.SECRET_KEY
        
        # اولویت 2: فایل persistent
        if self._use_persistent:
            try:
                self.data_dir.mkdir(parents=True, exist_ok=True)
                if self.secret_file.exists():
                    val = self.secret_file.read_text(encoding="utf-8").strip()
                    if val:
                        return val
                
                new_secret = secrets.token_urlsafe(32)
                self.secret_file.write_text(new_secret, encoding="utf-8")
                return new_secret
            except Exception:
                pass
        
        # Fallback: تولید موقت
        return secrets.token_urlsafe(32)
    
    async def load_history(self) -> list:
        """بارگذاری تاریخچه بروزرسانی"""
        if not self._use_persistent:
            return self._in_memory.get("history", [])
        
        try:
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
        except Exception:
            pass
        return []
    
    async def save_history_entry(self, entry: dict) -> bool:
        """ذخیره یک ورودی در تاریخچه بروزرسانی"""
        self._in_memory.setdefault("history", []).insert(0, entry)
        
        if not self._use_persistent:
            return True
        
        try:
            hist = await self.load_history()
            hist.insert(0, entry)
            hist = hist[:200]  # حداکثر 200 ورودی
            
            self.data_dir.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(hist, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

# نمونه singleton
storage = Storage()
