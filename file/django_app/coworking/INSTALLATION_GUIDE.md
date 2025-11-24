# Przewodnik instalacji - Google Login + Email 2FA

## 🚀 Nowe funkcje

✅ **Google OAuth Login** - Logowanie przez konto Google  
✅ **Email 2FA** - Dwuskładnikowe uwierzytelnienie przez email  
✅ **Bezpieczne API** - Nowe endpointy dla uwierzytelnienia  

## 📦 Instalacja

### 1. Zainstaluj nowe pakiety

```bash
cd django_app/coworking
pip install -r requirements.txt
```

### 2. Wykonaj migracje

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2.1. Skompiluj tłumaczenia (opcjonalnie, jeśli zmieniasz pliki .po)

```bash
python manage.py compilemessages
```

> **Uwaga dla Windows**: Jeśli dostaniesz błąd `Can't find msgfmt`, musisz zainstalować GNU gettext. Zobacz szczegółowe instrukcje w `GETTEXT_WINDOWS_SETUP.md`.

### 3. Utwórz superużytkownika (jeśli potrzebny)

```bash
python manage.py createsuperuser
```

### 4. Skonfiguruj Google OAuth

Postępuj zgodnie z instrukcjami w `GOOGLE_OAUTH_SETUP.md`

## 🔧 Konfiguracja

### Zmienne środowiskowe (.env)

```bash
# Google OAuth (wymagane dla Google Login)
GOOGLE_OAUTH2_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH2_SECRET=your_google_client_secret

# Email (wymagane dla 2FA)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Django
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 🎯 Nowe endpointy API

### Uwierzytelnienie
- `POST /api/auth/login-2fa` - Logowanie z obsługą 2FA
- `POST /api/auth/verify-2fa-login` - Weryfikacja kodu 2FA

### 2FA Management
- `GET /api/auth/2fa/status` - Sprawdź status 2FA
- `POST /api/auth/2fa/setup` - Konfiguracja 2FA
- `POST /api/auth/2fa/verify-setup` - Weryfikacja konfiguracji 2FA
- `POST /api/auth/2fa/disable` - Wyłączenie 2FA

### Google OAuth
- `GET /accounts/google/login/` - Logowanie przez Google
- `GET /accounts/google/login/callback/` - Callback Google

## 🎨 Nowe strony

### Logowanie
- `/login` - Zaktualizowana strona z Google Login i 2FA

### Bezpieczeństwo
- `/security` - Panel zarządzania 2FA (wymaga logowania)

## 🔄 Przepływ logowania

### Standardowe logowanie
1. Użytkownik wprowadza email/hasło
2. System sprawdza czy ma włączone 2FA
3. Jeśli TAK → wysyła kod na email
4. Jeśli NIE → loguje od razu

### Google Login
1. Użytkownik klika "Continue with Google"
2. Przekierowanie do Google
3. Zgoda na udostępnienie danych
4. Powrót i automatyczne logowanie

### Konfiguracja 2FA
1. Użytkownik idzie do `/security`
2. Klika "Enable 2FA"
3. Otrzymuje kod na email
4. Wprowadza kod i aktywuje 2FA

## 🧪 Testowanie

### 1. Uruchom serwer
```bash
python manage.py runserver
```

### 2. Testuj logowanie
- Przejdź do `http://127.0.0.1:8000/login`
- Sprawdź Google Login (wymaga konfiguracji)
- Sprawdź standardowe logowanie

### 3. Testuj 2FA
- Zaloguj się standardowo
- Przejdź do `/security`
- Włącz 2FA
- Wyloguj się i zaloguj ponownie
- Sprawdź czy wymaga kodu 2FA

## 🔒 Bezpieczeństwo

### Zalecenia
- Używaj HTTPS w produkcji
- Nie commituj kluczy API
- Regularnie rotuj hasła
- Monitoruj logi uwierzytelnienia

### Email 2FA
- Kody są ważne 5 minut
- Można wysłać nowy kod co 60 sekund
- Automatyczne usuwanie starych kodów

## 🐛 Rozwiązywanie problemów

### Google Login nie działa
1. Sprawdź Client ID i Secret
2. Sprawdź redirect URIs w Google Console
3. Sprawdź konfigurację w Django Admin

### 2FA nie wysyła emaili
1. Sprawdź konfigurację SMTP
2. Sprawdź logi Django
3. W development używa console backend

### Błędy migracji
```bash
python manage.py migrate --run-syncdb
```

## 📞 Wsparcie

W przypadku problemów:
1. Sprawdź logi Django
2. Sprawdź konfigurację zmiennych środowiskowych
3. Sprawdź czy wszystkie pakiety są zainstalowane

---

**Gotowe!** 🎉 Masz teraz Google Login i Email 2FA w swojej aplikacji Django!



