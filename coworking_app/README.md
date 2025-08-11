# Coworking App (Django-ready demo)

This small Django-ready demo provides a desktop-first seat reservation frontend (no database required).
It uses `localStorage` for persistence so you can run and test the interface immediately.

## Structure

```
coworking_app/
├── templates/
│   └── coworking.html
├── static/
│   ├── css/
│   │   └── coworking.css
│   └── js/
│       └── coworking.js
├── views.py
├── urls.py
└── README.md
```
 Coworking Reservation System

## Installation
```bash
git clone <repo_url>
cd myproject
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver

## Installation (quick)

1. Copy the `coworking_app` folder into your Django project directory.

2. Add the app to `INSTALLED_APPS` in `settings.py` (optional — the app does not require models):
```python
INSTALLED_APPS = [
    # ...
    'coworking_app',
]
```

3. Include the app URLs in your project's `urls.py` (if you prefer global include; alternatively keep the app's `urls.py`):
```python
from django.urls import include, path

urlpatterns = [
    # ...
    path('', include('coworking_app.urls')),
]
```

4. Make sure Django can serve static files in development (run `python manage.py runserver` and open `http://localhost:8000/coworking/`).

## Notes

- The frontend stores seat features and reservations in `localStorage` for demo/testing. Replace `saveReservationToServer` and `deleteReservationFromServer` in `static/js/coworking.js` with real `fetch()` calls to your API when ready.
- The template uses `{% load static %}` and expects static files to be collected/served via Django's staticfiles during development/production.
- For production, implement server-side validation to ensure no double-booking and replace client-side conflict checks with server-side checks.

Enjoy — if you want, I can now:
- Split the app into a proper Django app with `apps.py` and tests.
- Add Django REST endpoints and simple models for reservations.
- Add authentication (login) integration.
