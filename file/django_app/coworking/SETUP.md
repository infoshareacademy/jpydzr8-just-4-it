# 📋 Szczegółowa Instrukcja Konfiguracji

Ten dokument zawiera krok po kroku instrukcje konfiguracji wszystkich funkcjonalności aplikacji. Jeśli dopiero zaczynasz, zacznij od [README.md](README.md).

## 🪟 Windows - Instalacja Narzędzi (Opcjonalnie)

### Instalacja GNU gettext (do kompilacji tłumaczeń)

Jeśli planujesz pracować z tłumaczeniami, zainstaluj GNU gettext:

**Metoda 1: Chocolatey (najłatwiejsze)**
```powershell
# Najpierw zainstaluj Chocolatey jeśli nie masz: https://chocolatey.org/install
choco install gettext
```

**Metoda 2: Ręczna instalacja**
1. Pobierz z https://mlocati.github.io/articles/gettext-iconv-windows.html
2. Rozpakuj do np. `C:\gettext`
3. Dodaj `C:\gettext\bin` do zmiennej środowiskowej PATH:
   - Otwórz **Panel Sterowania** → **System** → **Zaawansowane ustawienia systemu**
   - Kliknij **Zmienne środowiskowe**
   - W **Zmienne systemowe** znajdź `Path`, kliknij **Edytuj**
   - Kliknij **Nowy** i dodaj `C:\gettext\bin`
   - Kliknij **OK** wszędzie
4. Zrestartuj terminal/PowerShell

**Weryfikacja instalacji:**
```powershell
msgfmt --version
```

### Windows Terminal (Zalecane)

Dla lepszego doświadczenia zainstaluj Windows Terminal z Microsoft Store lub z:
https://aka.ms/terminal

---

## 📦 Krok 1: Podstawowa Konfiguracja

### 1.1. Tworzenie pliku `.env`

1. Skopiuj plik `env.example` do `.env`:
   
   **Windows PowerShell:**
   ```powershell
   Copy-Item env.example .env
   ```
   
   **Windows CMD:**
   ```cmd
   copy env.example .env
   ```
   
   **macOS/Linux:**
   ```bash
   cp env.example .env
   ```

2. Otwórz plik `.env` w edytorze tekstu i uzupełnij wartości.

### 1.2. Konfiguracja Django (Wymagane)

**Wygenerowanie SECRET_KEY (Windows PowerShell):**
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Lub w Python shell:**
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Następnie skopiuj wygenerowany klucz do pliku `.env`:

```bash
SECRET_KEY=twoj_wygenerowany_secret_key
```

# DEBUG - True dla rozwoju, False dla produkcji
DEBUG=True

# ALLOWED_HOSTS - hosty na których działa aplikacja
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS - jeśli masz osobny frontend
CORS_ALLOWED_ORIGINS=http://127.0.0.1:3000,http://localhost:3000
CORS_ALLOW_ALL=False
```

### 1.3. Migracje i pierwsze uruchomienie

**Windows (PowerShell/CMD):**
```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

> **Uwaga:** Migracje automatycznie utworzą podstawowe dane:
> - Piętra 4, 5, 6, 7 z planami pięter
> - Strefy (Open Workspace, Deep Work, Chill Room, Kuchnia)
> - Przykładowe stanowiska na każdym piętrze (20+ stanowisk na piętro)
> - Sale konferencyjne dla każdego piętra
> 
> **Nie musisz uruchamiać `seed_office`** - wszystko jest już w migracjach!

Sprawdź czy aplikacja działa: http://127.0.0.1:8000

> **Uwaga:** Jeśli w PowerShell dostaniesz błąd o wykonywaniu skryptów podczas aktywacji venv, uruchom:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

## 📧 Krok 2: Konfiguracja Email (SMTP)

Email jest wymagany do:
- Dwuskładnikowego uwierzytelnienia (2FA)
- Resetowania hasła
- Powiadomień o rezerwacjach
- Przypomnień i raportów

### 2.1. Konfiguracja Gmail

**Krok 1: Utwórz App Password**

1. Przejdź na stronę: https://myaccount.google.com/apppasswords
2. Zaloguj się na konto Google
3. Kliknij "Wybierz aplikację" → "Poczta"
4. Kliknij "Wybierz urządzenie" → "Inne (Niestandardowa nazwa)"
5. Wpisz np. "Coworking App"
6. Kliknij "Generuj"
7. **Skopiuj wygenerowane hasło** (16 znaków, bez spacji)

**Krok 2: Uzupełnij `.env`**

```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=twoj.email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx  # Wklej App Password (16 znaków)
DEFAULT_FROM_EMAIL=noreply@twoja-domena.com
```

**Uwaga**: 
- App Password to nie twoje zwykłe hasło Google
- Hasło ma 16 znaków i może mieć spacje - możesz je usunąć lub zostawić
- Jeśli nie masz 2FA włączonego na koncie Google, najpierw je włącz

### 2.2. Konfiguracja innych dostawców SMTP

**Outlook/Office 365:**
```bash
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=twoj.email@outlook.com
EMAIL_HOST_PASSWORD=twoje_haslo
```

**SendGrid:**
```bash
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=twój_api_key_sendgrid
DEFAULT_FROM_EMAIL=noreply@twoja-domena.com
```

**Lokalny SMTP (dla testów):**
```bash
# Użyj django.core.mail.backends.console.EmailBackend
# Maile będą wyświetlane w konsoli - ustaw w settings.py:
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### 2.3. Testowanie konfiguracji email

1. **Uruchom serwer:**
   ```powershell
   python manage.py runserver
   ```

2. **Sprawdź logi:**
   - `WARNING: Email credentials not configured...` - jeśli brakuje danych
   - Brak komunikatu - jeśli wszystko jest OK
   - W Windows maile będą wyświetlane w oknie PowerShell/CMD jeśli używasz console backend

3. **Przetestuj wysyłkę:**
   - Utwórz konto użytkownika przez panel admina lub rejestrację
   - Spróbuj zresetować hasło przez `/password_reset/`
   - Sprawdź czy email przychodzi (lub jest w konsoli jeśli używasz console backend)
   
4. **Debugowanie (Windows):**
   - Jeśli maile nie przychodzą, sprawdź czy App Password jest poprawnie wklejony w `.env`
   - Usuń spacje z App Password jeśli występują
   - Sprawdź ustawienia Windows Firewall - może blokować połączenia SMTP

---

## 🔐 Krok 3: Konfiguracja Google OAuth (Logowanie przez Google)

### 3.1. Tworzenie projektu w Google Cloud Console

1. **Przejdź do Google Cloud Console:**
   https://console.cloud.google.com/

2. **Utwórz nowy projekt:**
   - Kliknij "Select a project" → "New Project"
   - Nazwij projekt np. "Coworking App"
   - Kliknij "Create"

3. **Włącz Google+ API:**
   - Menu po lewej → "APIs & Services" → "Library"
   - Wyszukaj "Google+ API"
   - Kliknij "Enable"

### 3.2. Konfiguracja OAuth Consent Screen

1. **APIs & Services → OAuth consent screen:**
   - **User Type**: 
     - `Internal` - jeśli masz Google Workspace (tylko użytkownicy z organizacji)
     - `External` - dla publicznej aplikacji (wymaga weryfikacji dla produkcji)
   - **App name**: np. "Coworking Reservation System"
   - **User support email**: twój email
   - **Developer contact information**: twój email
   - Kliknij "Save and Continue"

2. **Scopes** - zostaw domyślne, kliknij "Save and Continue"

3. **Test users** (tylko dla External):
   - Dodaj emaile użytkowników, którzy będą mogli testować
   - Kliknij "Save and Continue"

4. **Summary** - sprawdź i kliknij "Back to Dashboard"

### 3.3. Utworzenie OAuth Client ID

1. **APIs & Services → Credentials → Create Credentials → OAuth client ID**

2. **Wypełnij formularz:**
   - **Application type**: `Web application`
   - **Name**: np. "Coworking Dev Local"

3. **Authorized JavaScript origins:**
   ```
   http://127.0.0.1:8000
   http://localhost:8000
   ```
   *(W produkcji dodaj też adres z HTTPS)*

4. **Authorized redirect URIs:**
   ```
   http://127.0.0.1:8000/accounts/google/login/callback/
   http://localhost:8000/accounts/google/login/callback/
   ```
   *(W produkcji dodaj też adres z HTTPS)*

5. **Kliknij "Create"**

6. **Skopiuj Client ID i Client Secret** - wklej do `.env`

### 3.4. Konfiguracja w aplikacji

W pliku `.env` dodaj:

```bash
GOOGLE_OAUTH2_CLIENT_ID=twoj_client_id.apps.googleusercontent.com
GOOGLE_OAUTH2_SECRET=twoj_client_secret
```

### 3.5. Testowanie Google OAuth

1. Uruchom serwer: `python manage.py runserver`
2. Wejdź na: http://127.0.0.1:8000/login
3. Kliknij "Zaloguj przez Google"
4. Zaloguj się i autoryzuj aplikację
5. Powinieneś zostać przekierowany z powrotem i zalogowany

**Typowe problemy:**
- `Error 400: redirect_uri_mismatch` - sprawdź czy URI w Google Console są identyczne
- `Error 403: access_denied` - sprawdź czy email jest na liście test users (External)
- `Error 401: invalid_client` - sprawdź Client ID i Secret w `.env`

---

## 🔔 Krok 4: Konfiguracja Web Push Notifications

Web Push pozwala na wysyłanie powiadomień przeglądarkowych (nawet gdy użytkownik nie ma otwartej strony).

### 4.1. Generowanie kluczy VAPID

**Opcja 1: Używając py_vapid (zalecane dla Windows)**

```powershell
# Zainstaluj py_vapid (powinno być w requirements.txt)
pip install py_vapid

# Wygeneruj klucze
python -m py_vapid generate

# Skopiuj wygenerowane klucze do .env
```

**Opcja 2: Używając Node.js (web-push)**

```powershell
# Najpierw zainstaluj Node.js z https://nodejs.org/
npm install -g web-push
web-push generate-vapid-keys
```

### 4.2. Konfiguracja w `.env`

```bash
WEBPUSH_VAPID_PUBLIC_KEY=twoj_public_key
WEBPUSH_VAPID_PRIVATE_KEY=twoj_private_key
WEBPUSH_VAPID_CLAIM=mailto:admin@twoja-domena.com
WEBPUSH_CONTACT_EMAIL=admin@twoja-domena.com
```

**Uwaga**: 
- `WEBPUSH_VAPID_CLAIM` musi zawierać `mailto:` na początku
- W produkcji użyj prawdziwego adresu email i domeny

### 4.3. Testowanie Web Push

1. Uruchom serwer: `python manage.py runserver`
2. Wejdź na: http://127.0.0.1:8000/reservations/notification-settings/
3. Kliknij "Włącz powiadomienia"
4. Przeglądarka zapyta o pozwolenie - zaakceptuj
5. Kliknij "Test Notification"
6. Powinieneś otrzymać powiadomienie systemowe

**Wymagania:**
- Web Push działa tylko na HTTPS (lub localhost)
- Użytkownik musi wyrazić zgodę
- Service Worker musi być poprawnie zarejestrowany

**Debugowanie:**
- Otwórz konsolę przeglądarki (F12) → zakładka "Console"
- Sprawdź czy są błędy Service Worker
- Sprawdź zakładkę "Application" → "Service Workers"
- W logach backendu zobaczysz informacje o statusie subskrypcji

---

## 💬 Krok 5: Konfiguracja Slack (Opcjonalnie)

Integracja ze Slack pozwala na zarządzanie rezerwacjami przez komendy Slack.

### 5.1. Utworzenie Slack App

1. Przejdź do: https://api.slack.com/apps
2. Kliknij "Create New App" → "From scratch"
3. **App Name**: np. "Coworking Bot"
4. **Pick a workspace**: wybierz swój workspace
5. Kliknij "Create App"

### 5.2. Konfiguracja OAuth & Permissions

1. **OAuth & Permissions** (lewe menu):
   - Scrolluj w dół do "Scopes"
   - **Bot Token Scopes** - dodaj:
     - `commands` - do obsługi slash commands
     - `chat:write` - do wysyłania wiadomości
     - `channels:read` - do odczytu kanałów
   - Kliknij "Save Changes"

2. Scrolluj do góry i kliknij "Install to Workspace"
3. Autoryzuj aplikację
4. **Skopiuj Bot User OAuth Token** (zaczyna się od `xoxb-`)

### 5.3. Konfiguracja Event Subscriptions

1. **Event Subscriptions** (lewe menu):
   - Włącz "Enable Events"
   - **Request URL**: `https://twoja-domena.com/slack/events/`
   - W produkcji musisz mieć publiczny URL (użyj ngrok dla testów lokalnych)

2. **Subscribe to bot events** - dodaj:
   - `message.channels` - odbieranie wiadomości

### 5.4. Konfiguracja Slash Commands

1. **Slash Commands** (lewe menu):
   - Kliknij "Create New Command"
   - **Command**: `/rezerwacja`
   - **Request URL**: `https://twoja-domena.com/slack/commands/`
   - **Short Description**: "Rezerwuj stanowisko"
   - **Usage Hint**: `[data] [godzina]`
   - Kliknij "Save"

### 5.5. Pobranie Signing Secret

1. **Basic Information** (lewe menu):
   - Scrolluj w dół do "App Credentials"
   - **Signing Secret** - kliknij "Show" i skopiuj

### 5.6. Konfiguracja w aplikacji

W pliku `.env` dodaj:

```bash
SLACK_VERIFICATION_TOKEN=xoxp-...  # Opcjonalne, dla starszych wersji
SLACK_BOT_TOKEN=xoxb-...            # Bot User OAuth Token
SLACK_SIGNING_SECRET=...            # Signing Secret
```

### 5.7. Testowanie integracji Slack

**Dla lokalnego testowania użyj ngrok:**

1. **Zainstaluj ngrok:**
   - Pobierz z https://ngrok.com/download
   - Rozpakuj plik `ngrok.exe` do folderu (np. `C:\ngrok\`)
   - Dodaj folder do PATH lub użyj pełnej ścieżki

2. **Uruchom ngrok:**
   ```powershell
   # Jeśli ngrok jest w PATH
   ngrok http 8000
   
   # Lub podaj pełną ścieżkę
   C:\ngrok\ngrok.exe http 8000
   ```

3. **Skonfiguruj Slack:**
   - Skopiuj URL z ngrok (np. `https://abc123.ngrok.io`)
   - Użyj tego URL w konfiguracji Slack Event Subscriptions i Slash Commands
   - Dodaj `/slack/events/` i `/slack/commands/` na końcu URL

4. **Uruchom i przetestuj:**
   ```powershell
   # Terminal 1 - Django
   python manage.py runserver
   
   # Terminal 2 - ngrok
   ngrok http 8000
   ```
   
5. Przetestuj komendy w Slack

---

## 🔑 Krok 6: Konfiguracja JWT (Opcjonalnie)

Jeśli używasz API z tokenami JWT:

```bash
JWT_ACCESS_MINUTES=30     # Czas ważności access token (minuty)
JWT_REFRESH_DAYS=7        # Czas ważności refresh token (dni)
```

---

## 📊 Krok 7: Automatyczne Powiadomienia

### 7.1. Przypomnienia o rezerwacjach

Aplikacja może automatycznie wysyłać przypomnienia przed rezerwacją.

**Uruchomienie jako proces w tle:**

```bash
# Sprawdza co 5 minut i wysyła przypomnienia
python manage.py auto_send_reminders --interval 300
```

**Uruchomienie jednorazowe:**

```bash
# Wyślij wszystkie przypomnienia od razu
python manage.py send_reminders
```

**Konfiguracja w cron/scheduler:**

**Windows - Task Scheduler:**

1. Otwórz **Zarządzanie zadaniami** (Task Scheduler)
2. Kliknij **Utwórz zadanie** (Create Task)
3. Zakładka **Ogólne:**
   - Nazwa: `Coworking - Przypomnienia`
   - Uruchom jako: wybierz konto użytkownika
   - Zaznacz "Uruchom niezależnie od tego, czy użytkownik jest zalogowany"
4. Zakładka **Wyzwalacze:**
   - Kliknij **Nowy**
   - Uruchom zadanie: **Według harmonogramu**
   - Ustawienia: **Codziennie**
   - Powtarzaj zadanie co: **5 minut**, przez czas: **Bez limitu**
5. Zakładka **Akcje:**
   - Kliknij **Nowa**
   - Akcja: **Uruchom program**
   - Program/skrypt: `C:\Ścieżka\Do\Projektu\venv\Scripts\python.exe`
   - Argumenty: `manage.py auto_send_reminders --interval 300`
   - Rozpocznij w: `C:\Ścieżka\Do\Projektu`

**Alternatywnie - utwórz plik .bat:**

Utwórz plik `run_reminders.bat`:
```batch
@echo off
cd C:\Ścieżka\Do\Projektu
call venv\Scripts\activate.bat
python manage.py auto_send_reminders --interval 300
```

Następnie w Task Scheduler ustaw uruchomienie tego pliku .bat co 5 minut.

**Linux/Mac - crontab:**
```bash
# Dodaj do crontab (crontab -e)
*/5 * * * * cd /ścieżka/do/projektu && source venv/bin/activate && python manage.py auto_send_reminders --interval 300
```

### 7.2. Dzienne podsumowania

```powershell
# Wyślij dzienne podsumowania wszystkim użytkownikom
python manage.py send_daily_summaries
```

**Automatyzacja (Windows Task Scheduler):**
- Utwórz zadanie uruchamiane codziennie o 20:00
- Program: `C:\Ścieżka\Do\Projektu\venv\Scripts\python.exe`
- Argumenty: `manage.py send_daily_summaries`
- Katalog: `C:\Ścieżka\Do\Projektu`

**Lub plik .bat:**
```batch
@echo off
cd C:\Ścieżka\Do\Projektu
call venv\Scripts\activate.bat
python manage.py send_daily_summaries
```

**Linux/Mac (cron):**
```bash
0 20 * * * cd /ścieżka/do/projektu && source venv/bin/activate && python manage.py send_daily_summaries
```

### 7.3. Tygodniowe raporty

```powershell
# Wyślij tygodniowe raporty
python manage.py send_weekly_reports
```

**Automatyzacja (Windows Task Scheduler):**
- Utwórz zadanie uruchamiane w poniedziałki o 9:00
- Program: `C:\Ścieżka\Do\Projektu\venv\Scripts\python.exe`
- Argumenty: `manage.py send_weekly_reports`
- Katalog: `C:\Ścieżka\Do\Projektu`

**Lub plik .bat:**
```batch
@echo off
cd C:\Ścieżka\Do\Projektu
call venv\Scripts\activate.bat
python manage.py send_weekly_reports
```

**Linux/Mac (cron):**
```bash
0 9 * * 1 cd /ścieżka/do/projektu && source venv/bin/activate && python manage.py send_weekly_reports
```

---

## ✅ Sprawdzenie Konfiguracji

### Checklist przed uruchomieniem:

- [ ] Plik `.env` utworzony i skonfigurowany
- [ ] `SECRET_KEY` zmieniony na bezpieczną wartość
- [ ] Migracje wykonane (`python manage.py migrate`)
- [ ] Superużytkownik utworzony
- [ ] Email SMTP skonfigurowany (test wysyłki)
- [ ] Google OAuth skonfigurowany (test logowania)
- [ ] Web Push skonfigurowany (test powiadomienia)
- [ ] Aplikacja uruchamia się bez błędów

### Testy funkcjonalności:

1. **Email:**
   - Utwórz nowe konto
   - Spróbuj zresetować hasło
   - Włącz 2FA

2. **Google OAuth:**
   - Kliknij "Zaloguj przez Google" na stronie logowania
   - Sprawdź czy logowanie działa

3. **Web Push:**
   - Wejdź na `/reservations/notification-settings/`
   - Włącz powiadomienia
   - Wyślij testowe powiadomienie

4. **Rezerwacje:**
   - Utwórz rezerwację
   - Sprawdź czy przychodzi email potwierdzający
   - Anuluj rezerwację

---

## 🚨 Rozwiązywanie Problemów

### Problem: Maile nie są wysyłane

**Rozwiązanie:**
1. Sprawdź logi serwera Django - błędy SMTP są tam widoczne
2. Zweryfikuj App Password w `.env` (dla Gmail)
3. Sprawdź ustawienia zapory sieciowej
4. Testuj z prostym mailem: `python manage.py send_reminders`

### Problem: Google OAuth - redirect_uri_mismatch

**Rozwiązanie:**
1. Sprawdź dokładnie URI w Google Cloud Console
2. Muszą być identyczne (w tym slasze na końcu)
3. Dodaj oba warianty: `localhost` i `127.0.0.1`
4. W produkcji użyj HTTPS

### Problem: Web Push nie działa

**Rozwiązanie:**
1. Sprawdź konsolę przeglądarki (F12)
2. Web Push wymaga HTTPS (lub localhost)
3. Zweryfikuj klucze VAPID w `.env`
4. Sprawdź czy Service Worker jest zarejestrowany
5. Sprawdź logi backendu

### Problem: Slack - błędy weryfikacji

**Rozwiązanie:**
1. Sprawdź `SLACK_SIGNING_SECRET` w `.env`
2. W produkcji użyj HTTPS
3. Dla testów lokalnych użyj ngrok
4. Sprawdź czy URL w Slack App jest poprawny

---

## 📝 Uwagi Końcowe

- **Nie commituj pliku `.env` do repozytorium!** (powinien być w `.gitignore`)
- W produkcji użyj bezpiecznych wartości dla wszystkich kluczy
- Web Push wymaga HTTPS w produkcji
- Regularnie sprawdzaj logi aplikacji w katalogu `logs/`
- Twórz kopie zapasowe bazy danych przed aktualizacjami

## 🪟 Windows - Dodatkowe Uwagi

### PowerShell vs CMD

- **PowerShell** (zalecane) - nowocześniejszy, lepsze wsparcie dla UTF-8
- **CMD** - tradycyjny, działa wszędzie
- Większość komend działa w obu, ale składnia może się różnić

### Kodowanie znaków

Jeśli widzisz zniekształcone znaki polskie w terminalu:

**PowerShell:**
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
```

**CMD:**
```cmd
chcp 65001
```

### Ścieżki w plikach .bat

W plikach .bat używaj podwójnych backslashów lub forward slashes:
```batch
cd C:\\Ścieżka\\Do\\Projektu
# lub
cd C:/Ścieżka/Do/Projektu
```

### Uruchamianie jako usługa Windows

Dla automatycznego uruchamiania serwera Django możesz użyć:
- **NSSM** (Non-Sucking Service Manager) - https://nssm.cc/
- **Windows Service** utworzony przez sc.exe
- **Task Scheduler** - najprostsze rozwiązanie

**Gotowe!** 🎉 

Wszystkie funkcjonalności powinny być teraz skonfigurowane. Jeśli masz problemy, sprawdź logi aplikacji lub skontaktuj się z zespołem.

