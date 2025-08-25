# backend/app/main.py
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse

from .settings import settings
from .db import engine, Base
from . import models  # noqa: F401 (ensure models are imported so tables exist)

from .auth_router import router as auth_router
from .reservations_router import router as reservations_router
from .console_router import router as console_router

# DEV: create tables on first run (for prod prefer Alembic migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Full App (FastAPI + SQLite)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in (settings.CORS_ORIGINS or "*").split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

# ---- Static mounts (order doesn't matter) ----
if (FRONTEND_DIR / "welcome").exists():
    app.mount("/welcome", StaticFiles(directory=str(FRONTEND_DIR / "welcome")), name="welcome")
if (FRONTEND_DIR / "login").exists():
    app.mount("/login", StaticFiles(directory=str(FRONTEND_DIR / "login")), name="login")
if (FRONTEND_DIR / "registration").exists():
    app.mount("/registration", StaticFiles(directory=str(FRONTEND_DIR / "registration")), name="registration")
if (FRONTEND_DIR / "menu").exists():
    app.mount("/menu", StaticFiles(directory=str(FRONTEND_DIR / "menu")), name="menu")
if (FRONTEND_DIR / "goodbye").exists():
    app.mount("/goodbye", StaticFiles(directory=str(FRONTEND_DIR / "goodbye")), name="goodbye")

# ---- Views (HTML redirects to the correct static files) ----
@app.get("/", response_class=HTMLResponse)
def root():
    if (FRONTEND_DIR / "welcome" / "index.html").exists():
        return RedirectResponse(url="/welcome/index.html")
    if (FRONTEND_DIR / "login" / "index.html").exists():
        return RedirectResponse(url="/login/index.html")
    return HTMLResponse("<h1>Upload your frontend: welcome/index.html or login/index.html</h1>", status_code=200)

@app.get("/register", response_class=HTMLResponse)
def register_view():
    if (FRONTEND_DIR / "registration" / "index2.html").exists():
        return RedirectResponse(url="/registration/index2.html")
    if (FRONTEND_DIR / "registration" / "index.html").exists():
        return RedirectResponse(url="/registration/index.html")
    return HTMLResponse("<h1>Upload your frontend: registration/index.html</h1>", status_code=200)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_view():
    if (FRONTEND_DIR / "menu" / "dashboard.html").exists():
        return RedirectResponse(url="/menu/dashboard.html")
    if (FRONTEND_DIR / "menu" / "index.html").exists():
        return RedirectResponse(url="/menu/index.html")
    return HTMLResponse("<h1>Upload your frontend: menu/dashboard.html</h1>", status_code=200)

@app.get("/logout", response_class=HTMLResponse)
def logout_view():
    # Klient czyści token w JS; tu podajemy stronę pożegnalną
    if (FRONTEND_DIR / "goodbye" / "index.html").exists():
        return RedirectResponse(url="/goodbye/index.html")
    return HTMLResponse("<h1>Logged out. (goodbye view missing)</h1>", status_code=200)

# ---- Debug helpers (możesz usunąć po diagnozie) ----
@app.get("/__debug/where")
def debug_where():
    p_login = FRONTEND_DIR / "login" / "index.html"
    p_welcome = FRONTEND_DIR / "welcome" / "index.html"
    p_menu = FRONTEND_DIR / "menu" / "dashboard.html"
    return JSONResponse(
        {
            "FRONTEND_DIR": str(FRONTEND_DIR.resolve()),
            "welcome_index_exists": p_welcome.exists(),
            "welcome_index_path": str(p_welcome.resolve()) if p_welcome.exists() else None,
            "login_index_exists": p_login.exists(),
            "login_index_path": str(p_login.resolve()) if p_login.exists() else None,
            "dashboard_exists": p_menu.exists(),
            "dashboard_path": str(p_menu.resolve()) if p_menu.exists() else None,
        }
    )

@app.get("/__debug/login-html", response_class=HTMLResponse)
def debug_login_html():
    p = FRONTEND_DIR / "login" / "index.html"
    if p.exists():
        return HTMLResponse(p.read_text(encoding="utf-8", errors="ignore")[:400])
    return HTMLResponse("login/index.html: MISSING", status_code=404)

# ---- API routers ----
app.include_router(auth_router)
app.include_router(reservations_router)
app.include_router(console_router)
