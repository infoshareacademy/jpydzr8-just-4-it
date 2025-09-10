# Coworking Demo

Demo aplikacji (Django + DRF + statyczny frontend) z rozbudowanym **Django Admin**:
- model **Seats** (miejsca) + udogodnienia: `0 / D / S / E / DS / DE / SE / DSE`
- akcje masowe, generator miejsc, import CSV
- gotowy superuser do testów (`seed_demo_admin`)

## Wymagania
- Python 3.10–3.13 (testowane na 3.13)
- Django 5.2.x
- Django REST Framework
- django-cors-headers
- SQLite (plikowo, zero konfiguracji)

---

## 1) Szybki start

```bash
git clone <URL_DO_REPO>
cd <katalog_repo>

python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1

# Jeśli jest requirements.txt:
pip install -r requirements.txt
# Jeśli nie ma:
pip install "Django==5.2.6" djangorestframework django-cors-headers
```

Zainicjuj bazę i stwórz konto demo:

```bash
python manage.py migrate

# preferowane (komenda do seedowania demo admina):
python manage.py seed_demo_admin

# alternatywnie, bez komendy:
# DJANGO_SUPERUSER_EMAIL=demo@acme.io DJANGO_SUPERUSER_PASSWORD=Demo123! python manage.py createsuperuser --noinput
```

Uruchom serwer dev:

```bash
python manage.py runserver
```

Wejdź w przeglądarce: **http://127.0.0.1:8000/**

---

## 2) Logowanie

- **Django Admin:** `http://127.0.0.1:8000/admin/`  
  E-mail: **demo@acme.io**, hasło: **Demo123!**

- **Frontend (statyczny UI):**
  - Dashboard: `/menu/dashboard.html` *(lub `/menu/index.html` w zależności od konfiguracji)*
  - Show all seats: `/menu/index.html`
  - Rezerwacja: `/menu/reserve.html`
  - Anulowanie: `/menu/cancel.html`

> W `coworking/urls.py` root (`/`) przekierowuje na frontend oraz ustawiony jest link **“View site”** w panelu admina:
> ```python
> from django.views.generic.base import RedirectView
> from django.contrib import admin
> admin.site.site_url = "/menu/index.html"  # lub "/menu/dashboard.html"
> path("", RedirectView.as_view(url="/menu/index.html", permanent=False), name="home")
> ```

---

## 3) Admin → Seats

Sekcja **Seats** w adminie umożliwia:
- Dodawanie/edycję miejsc (`code`, `floor`, `features`)
- **Checkboxy D/S/E** na formularzu automatycznie ustawiają pole `features` (`0`, `D`, `S`, `E`, `DS`, `DE`, `SE`, `DSE`)
- **Akcje masowe** do hurtowej zmiany `features`

### Generator miejsc
Szybkie tworzenie numeracji:
```
/admin/api/seat/generate/
```
Przykład: Floor=5, Rows=12, Prefix=5, Pad=2 → `5-01 … 5-12`

### Import z CSV
Tworzenie/aktualizacja rekordów z pliku:
```
/admin/api/seat/import-csv/
```
Format:
```csv
code,floor,features
5-01,5,DE
5-02,5,0
5-03,5,DS
```

### Legend (kody udogodnień)
- **D** Docking station  
- **S** Two screens  
- **E** Electric desk  
- Kombinacje: **DS**, **DE**, **SE**, **DSE**  
- **0** Unreserved (brak udogodnień)

---

## 4) Struktura ważnych plików

```
api/
  models.py                 # zawiera klasę Seat
  admin.py                  # SeatAdmin + generator/import
  management/
    __init__.py
    commands/
      __init__.py
      seed_demo_admin.py    # tworzy superusera demo
  templates/admin/
    base_site.html
    index.html
    seat_import.html
    seat_generate.html
  static/admin/
    brand.css

coworking/urls.py           # redirect "/" → /menu/... + admin.site.site_url
static/frontend/...         # HTML/CSS/JS frontu (np. /menu/index.html, /menu/dashboard.html)
```

---

## 5) Konfiguracja Django (skrót)

**INSTALLED_APPS:**
```python
INSTALLED_APPS = [
  "django.contrib.admin",
  "django.contrib.auth",
  "django.contrib.contenttypes",
  "django.contrib.sessions",
  "django.contrib.messages",
  "django.contrib.staticfiles",
  "rest_framework",
  "corsheaders",
  "api",  # lokalna appka z modelem Seat i adminem
]
```

**TEMPLATES:**
```python
TEMPLATES = [
  {
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],  # lub [BASE_DIR / "templates"]
    "APP_DIRS": True,
    "OPTIONS": {
      "context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        # opcjonalnie: boxy Today/Shortcuts na stronie głównej admina
        "api.context_processors.admin_metrics",
      ],
    },
  },
]
```

---

## 6) Najczęstsze problemy (FAQ)

**404 na `/menu/dashboard.html`**  
– Sprawdź, czy plik istnieje w `static/frontend/menu/dashboard.html`.  
– Jeśli nie, użyj `/menu/index.html` (zmień `admin.site.site_url` i redirect w `urls.py`).

**Komenda `seed_demo_admin` nie istnieje**  
– Komenda musi leżeć w `api/management/commands/seed_demo_admin.py` oraz istnieć `__init__.py` w `api/management/` i `api/management/commands/`.  
– Alternatywa:  
```bash
DJANGO_SUPERUSER_EMAIL=demo@acme.io DJANGO_SUPERUSER_PASSWORD=Demo123! python manage.py createsuperuser --noinput
```

**AlreadyRegistered(Seat)**  
– Zarejestruj model raz; ewentualnie:
```python
from django.contrib.admin.sites import NotRegistered
try: admin.site.unregister(Seat)
except NotRegistered: pass
admin.site.register(Seat, SeatAdmin)
```

**Style się nie wczytują**  
– Użyj ścieżek absolutnych do statyków w HTML:  
```html
<link rel="stylesheet" href="/static/frontend/menu/theme.css">
```
– Albo połóż CSS obok HTML i linkuj względnie, np. `dashboard.css` → `GET /menu/dashboard.css`.

---

## 7) Bezpieczeństwo (demo)
Hasło w seedzie jest **tylko do demo**. Zmień je przed publikacją lub ustaw zmienną środowiskową i waliduj uruchomienie komendy. Zmiana hasła w shellu:

```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> u = get_user_model().objects.get(email="demo@acme.io")
>>> u.set_password("NewPass123!")
>>> u.save()
```

Miłego testowania! ✨
