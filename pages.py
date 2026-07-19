from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from config import config

router = APIRouter()

# HTML ساده برای لاگین
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود به پنل</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 h-screen flex items-center justify-center">
    <div class="bg-gray-800 p-8 rounded-lg shadow-xl w-96 text-white text-center">
        <h2 class="text-2xl font-bold mb-6 text-blue-400">ورود به پنل مدیریت</h2>
        {error}
        <form method="POST" action="/login">
            <input type="password" name="password" placeholder="رمز عبور..." class="w-full p-3 mb-4 rounded bg-gray-700 text-white border border-gray-600 focus:outline-none focus:border-blue-500" required>
            <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded transition-colors">ورود</button>
        </form>
    </div>
</body>
</html>
"""

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = ""):
    err_html = f'<p class="text-red-400 mb-4">{error}</p>' if error else ""
    return HTMLResponse(LOGIN_HTML.format(error=err_html))

@router.post("/login")
async def login_post(request: Request, password: str = Form(...)):
    # در اینجا برای سادگی، رمز عبور همان SECRET_KEY در نظر گرفته می‌شود
    # می‌توانید رمز عبور اختصاصی در config.py اضافه کنید.
    if password == config.SECRET_KEY or password == "admin": # TODO: Change fallback
        request.session["authenticated"] = True
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url="/login?error=رمز عبور اشتباه است", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not request.session.get("authenticated"):
        return RedirectResponse(url="/login")
        
    # فایل داشبورد اصلی شما که قبلا داشتید (React/HTML).
    # به دلیل محدودیت حجم پیام، من فرض می‌کنم فایل index.html را از دیسک می‌خوانید
    # یا سورس HTML خام خود را اینجا قرار می‌دهید.
    try:
        from pathlib import Path
        index_path = Path(config.APP_DIR) / "index.html"
        if index_path.exists():
            return HTMLResponse(index_path.read_text(encoding="utf-8"))
        else:
            return HTMLResponse("<h1>پنل مدیریت (فایل index.html یافت نشد)</h1>")
    except Exception as e:
        return HTMLResponse(f"Error loading dashboard: {e}")