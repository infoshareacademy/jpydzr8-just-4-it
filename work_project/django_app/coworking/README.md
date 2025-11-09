# Coworking – jak to odpalam krok po kroku

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
1. Kopiuję wzór: `cp env_example.txt .env` i od razu go otwieram.
2. `SECRET_KEY` generuję lokalnie. W terminalu wpisuję:
   ```
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```
   Wynik wklejam do `SECRET_KEY=`. (Jak ktoś utknie, mam swój klucz i mogę podrzucić).
3. `DEBUG` zostawiam na `True`, dopóki działam lokalnie.
4. Sekcję mailową uzupełniam danymi ze skrzynki:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=moj_email@gmail.com
   EMAIL_HOST_PASSWORD=moje_haslo_aplikacji
   DEFAULT_FROM_EMAIL=biuro@mojadomena.com
   ```
   Skąd to biorę:
   - `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS` – dokumentacja poczty (dla Gmaila jak wyżej; dla innych providerów ich ustawienia).
   - `EMAIL_HOST_USER` – adres skrzynki wysyłającej.
   - `EMAIL_HOST_PASSWORD` – hasło aplikacji/SMTP wygenerowane w panelu (np. w Gmailu w sekcji „Hasła aplikacji”).
   - `DEFAULT_FROM_EMAIL` – nadawca, którego zobaczy odbiorca.
5. Pozostałe sekcje (`GOOGLE_OAUTH`, `JWT`, `CORS`) wypełniam zgodnie z własnymi potrzebami. Opisy mam w plikach obok (`GOOGLE_OAUTH_SETUP.md`, itp.).
6. Zapisuję `.env`. Przy starcie Django samo zaczyta wszystkie wartości.

> Jeśli zapomnę o `EMAIL_BACKEND`, Django użyje trybu konsolowego i mail pokaże się tylko w terminalu.

## 4. Migracje i konto
1. `python manage.py migrate` – uruchamiam w katalogu projektu; tworzy wszystkie tabele w lokalnej bazie SQLite
2. `python manage.py createsuperuser` (opcjonalnie) – podaję e-mail i hasło, potem mogę zalogować się do panelu admina (`/admin`)

## 5. Test serwera i maila
1. `python manage.py runserver`
2. Wchodzę na `http://127.0.0.1:8000/login`
3. Wpisuję mail użytkownika i wysyłam magic link
4. Sprawdzam wynik:
   - Jeśli skonfigurowałem SMTP → mail wpada na skrzynkę jak standardowa wiadomość.
   - Jeśli ustawiłem `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` → mail pojawia się w terminalu; z tekstu mogę skopiować link i wkleić w przeglądarce.
   - Jeśli chcę mieć podgląd w przeglądarce bez prawdziwego SMTP → odpalam MailHog:
     ```
     # Mac (brew)
     brew install mailhog
     mailhog

     # Docker
     docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
     ```
     Ustawiam w `.env`:
     ```
     EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
     EMAIL_HOST=127.0.0.1
     EMAIL_PORT=1025
     EMAIL_USE_TLS=False
     ```
     Maile są wtedy widoczne pod `http://localhost:8025`.

## 6. Logowanie Google (jeśli potrzebne)
1. Loguję się do [Google Cloud Console](https://console.cloud.google.com/) i wybieram projekt (albo tworzę nowy).
2. Wchodzę w `APIs & Services → Credentials`.
3. Klikam `Create Credentials → OAuth client ID`.
4. Typ aplikacji: `Web application`.
5. W sekcji redirectów dodaję:
   - `http://127.0.0.1:8000/accounts/google/login/callback/`
   - `http://localhost:8000/accounts/google/login/callback/` (jeżeli korzystam z localhosta)
6. Zapisuję – dostaję `Client ID` i `Client Secret`.
7. W `.env` dopisuję:
   ```
   GOOGLE_OAUTH2_CLIENT_ID=tu_wklejam_client_id
   GOOGLE_OAUTH2_SECRET=tu_wklejam_client_secret
   ```
8. Restartuję serwer (`Ctrl+C`, potem `python manage.py runserver`) i testuję logowanie przez Google.

## 7. Szybka diagnostyka
- Brak maila → w terminalu pewnie pojawiła się cała treść (czyli nadal backend konsolowy)
- `SMTPAuthenticationError` → złe hasło albo brak hasła aplikacji
- Problemy z Google → sprawdzam redirecty i czy domena jest dodana w Google Cloud

Na tym koniec. Po tym zestawie kroków wszystko działa lokalnie – można logować się magic linkiem, a konfiguracja leży tylko w `.env`. Zrobione raz, działa każdemu. 
