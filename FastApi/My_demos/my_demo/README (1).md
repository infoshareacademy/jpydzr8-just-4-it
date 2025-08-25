# Workspace Bookings — README

Aplikacja demonstracyjna: **FastAPI + SQLite + statyczny frontend** + prosta konsola.  
Działa na **macOS** i **Linux**.

## Wymagania

- Python **3.10+** (polecany 3.11/3.12)
- pip
- (opcjonalnie) `virtualenv` / `venv`
- Brak dodatkowych systemowych bibliotek (koła binarne dla `bcrypt`/`uvicorn` zwykle wystarczą)

## Struktura katalogów

```
my_demo/
├─ backend/
│  └─ app/
│     ├─ main.py           # FastAPI, mounty frontendu, /logout, przekierowania
│     ├─ auth_router.py    # rejestracja, logowanie, /me
│     ├─ reservations_*    # CRUD do rezerwacji
│     ├─ security.py       # bcrypt + JWT
│     ├─ models.py         # SQLAlchemy modele (User, Reservation)
│     └─ db.py, settings.py
├─ frontend/
│  ├─ welcome/             # strona startowa
│  ├─ login/               # logowanie
│  ├─ registration/        # rejestracja (auto-login po sukcesie)
│  ├─ menu/                # dashboard, guard.js, itp.
│  └─ goodbye/             # ekran „Goodbye” + auto-redirect na welcome
└─ app.db                  # SQLite (tworzy się automatycznie)
```

## Konfiguracja środowiska (macOS & Linux)

W terminalu przejdź do katalogu projektu `my_demo/` i wykonaj:

```bash
# 1) Utwórz i aktywuj wirtualne środowisko
python3 -m venv venv
source venv/bin/activate

# 2) Zainstaluj zależności
pip install fastapi "uvicorn[standard]" "passlib[bcrypt]==1.7.4" "bcrypt==4.0.1"   "python-jose[cryptography]" "SQLAlchemy>=2.0" alembic python-dotenv   pydantic-settings email-validator
```

> Uwaga: przypięcie `passlib[bcrypt]==1.7.4` i `bcrypt==4.0.1` eliminuje znane ostrzeżenia/niezgodności wersji na niektórych systemach.

### (Opcjonalnie) `.env`

Możesz dodać plik `.env` w katalogu `my_demo/`:

```
APP_ENV=dev
SECRET_KEY=change_me_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=60
SQLITE_PATH=app.db
CORS_ORIGINS=*
```

## Uruchomienie backendu

Z katalogu `my_demo/`:

```bash
source venv/bin/activate
python3 -m uvicorn backend.app.main:app --reload
```

Serwer: http://127.0.0.1:8000

### Dostępne widoki (statyczny frontend)

- `GET /` → przekierowanie do `/welcome/index.html` (jeśli istnieje) lub `/login/index.html`
- `GET /welcome/` → strona startowa
- `GET /login/` → logowanie
- `GET /registration/` → rejestracja (**po sukcesie automatyczny login**, token zapisany w `localStorage`)
- `GET /dashboard` → przekierowanie do `/menu/dashboard.html`
- `GET /logout` → przekierowanie do `/goodbye/index.html`  
  Strona `goodbye`:
  - czyści token z `localStorage`,
  - po ~3s **automatycznie** przenosi na `/welcome/index.html`.

### API (wybrane)

- `POST /api/auth/register`  
  Body (JSON): `{"email":"u@x.com","password":"Haslo123!","full_name":"Twoje Imię"}`
- `POST /api/auth/login`  
  Body (JSON): `{"email":"u@x.com","password":"Haslo123!"}`
- `GET /api/auth/me`  
  Header: `Authorization: Bearer <token>`

Szybki test z curl:

```bash
# Rejestracja
curl -X POST http://127.0.0.1:8000/api/auth/register   -H "Content-Type: application/json"   -d '{"email":"test@example.com","password":"Test123!","full_name":"Test"}'

# Logowanie
curl -X POST http://127.0.0.1:8000/api/auth/login   -H "Content-Type: application/json"   -d '{"email":"test@example.com","password":"Test123!"}'
```

## Uruchomienie aplikacji konsolowej (opcjonalnie)

W drugim terminalu (z aktywnym `venv`):

```bash
python3 console_py/src/app.py
```

## Typowe problemy i rozwiązania

- **`No module named uvicorn`**  
  Użyj formy modułu: `python3 -m uvicorn backend.app.main:app --reload`.  
  Upewnij się, że masz aktywne `venv`.

- **Bcrypt/Passlib ostrzeżenia/błędy**  
  Zainstaluj zgodne wersje:  
  `pip install --upgrade "passlib[bcrypt]==1.7.4" "bcrypt==4.0.1"`

- **Frontend ładuje „stare” pliki** (cache)  
  Zrób twardy reload (**Cmd+Shift+R / Ctrl+F5**) albo DevTools → Network → **Disable cache**,  
  ewentualnie dopisz `?v=dev1` do linków CSS/JS.

- **404 na plikach statycznych**  
  Upewnij się, że w `backend/app/main.py` są mounty: `/welcome`, `/login`, `/registration`, `/menu`, `/goodbye`  
  oraz że ścieżki w HTML są **względne** (np. `dashboard.js`, `logout_goodbye_white.css`) — bez `/frontend/...`.

## Deployment (skrót)

Na produkcję rozważ:

```bash
pip install "uvicorn[standard]" gunicorn
# uruchomienie przykładowe:
gunicorn -k uvicorn.workers.UvicornWorker backend.app.main:app -w 2 -b 0.0.0.0:8000
```

Front serwowany przez FastAPI (StaticFiles) lub przez nginx.  
Pamiętaj o **SECRET_KEY** z `.env`.

## Licencja

Własna / do uzgodnienia.

---

### Quick start (TL;DR)

```bash
cd my_demo
python3 -m venv venv
source venv/bin/activate
pip install fastapi "uvicorn[standard]" "passlib[bcrypt]==1.7.4" "bcrypt==4.0.1"   "python-jose[cryptography]" "SQLAlchemy>=2.0" alembic python-dotenv   pydantic-settings email-validator
python3 -m uvicorn backend.app.main:app --reload
# -> otwórz: http://127.0.0.1:8000/welcome/
```
