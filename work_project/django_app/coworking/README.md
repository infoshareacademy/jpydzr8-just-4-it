# Coworking – jak to odpalić krok po kroku

Poniżej rozpisuję dokładnie, co robię po świeżym klonie repo. Zrobione raz, działa każdemu – zero grzebania w kodzie.

## 1. Co trzeba mieć
- Python 3.11 (u mnie działa także 3.10, ale stawiałem na 3.11)
- Pip + wbudowany `venv`
- Konto pocztowe z dostępem SMTP (np. Gmail z hasłem aplikacji)
- (Opcjonalnie) projekt w Google Cloud, jeśli ktoś chce logowanie Google

## 2. Instalacja projektu
1. `git clone <repo-url>`
2. `cd django_app/coworking`
3. `python3 -m venv venv`
4. `source venv/bin/activate`  
   (Windows: `venv\Scripts\activate`)
5. `pip install -r requirements.txt`
6. `cp env_example.txt .env`

## 3. Ustawiam `.env`
1. Otwieram `.env` (powstał przed chwilą z `env_example.txt`)
2. `SECRET_KEY` – wklejam własny. Można go szybko wygenerować:
   - w Pythonie: `python -c "import secrets; print(secrets.token_urlsafe(50))"`
   - albo skopiować z istniejącego projektu, byle nie zostawić domyślnego
3. `DEBUG=True` zostawiam na środowisku lokalnym, na produkcji zmienię na `False`
4. Sekcja mailowa – wszystko biorę z panelu pocztowego:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=moj_email@gmail.com
   EMAIL_HOST_PASSWORD=moje_haslo_aplikacji
   DEFAULT_FROM_EMAIL=biuro@mojadomena.com
   ```
   Skąd wziąć te dane?
   - `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS` → dokumentacja serwera pocztowego (dla Gmaila jak powyżej, dla innych dostawców wpisuję ich wartości)
   - `EMAIL_HOST_USER` → pełny adres skrzynki, z której chcę wysyłać maile
   - `EMAIL_HOST_PASSWORD` → hasło aplikacji lub hasło SMTP z panelu pocztowego
   - `DEFAULT_FROM_EMAIL` → adres, który zobaczy odbiorca jako nadawcę
5. Dodatkowe sekcje (`GOOGLE_OAUTH`, `JWT`, `CORS`) uzależniam od tego, czego używam – opisy są w odpowiednich plikach (`GOOGLE_OAUTH_SETUP.md` itd.)
6. Zapisuję `.env` – przy starcie serwer automatycznie zaczyta te wartości

> Jeśli zapomnę o `EMAIL_BACKEND`, Django użyje trybu konsolowego i mail pokaże się tylko w terminalu.

## 4. Migracje i konto
1. `python manage.py migrate` – uruchamiam w katalogu projektu; tworzy wszystkie tabele w lokalnej bazie SQLite
2. `python manage.py createsuperuser` (opcjonalnie) – podaję e-mail i hasło, potem mogę zalogować się do panelu admina (`/admin`)

## 5. Test serwera i maila
1. `python manage.py runserver`
2. Wchodzę na `http://127.0.0.1:8000/login`
3. Wpisuję mail użytkownika i wysyłam magic link
4. Mail powinien przyjść normalnie na skrzynkę – jeśli nie, sprawdzam czy `EMAIL_BACKEND` był ustawiony oraz czy dane SMTP są poprawne

## 6. Logowanie Google (jeśli potrzebne)
- Uzupełniam w `.env` `GOOGLE_OAUTH2_CLIENT_ID` i `GOOGLE_OAUTH2_SECRET`
- W Google Cloud dodaję redirect `http://127.0.0.1:8000/accounts/google/login/callback/`
- Szczegóły w `GOOGLE_OAUTH_SETUP.md`

## 7. Szybka diagnostyka
- Brak maila → w terminalu pewnie pojawiła się cała treść (czyli nadal backend konsolowy)
- `SMTPAuthenticationError` → złe hasło albo brak hasła aplikacji
- Problemy z Google → sprawdzam redirecty i czy domena jest dodana w Google Cloud

Na tym koniec. Po tym zestawie kroków wszystko działa lokalnie – można logować się magic linkiem, a konfiguracja leży tylko w `.env`. Zrobione raz, działa każdemu. 
