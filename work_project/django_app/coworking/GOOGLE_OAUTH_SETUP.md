# Konfiguracja Google OAuth

## Krok 1: Utworzenie projektu w Google Cloud Console

1. Przejdź do [Google Cloud Console](https://console.cloud.google.com/)
2. Utwórz nowy projekt lub wybierz istniejący
3. Włącz Google+ API i Google OAuth2 API

## Krok 2: Konfiguracja OAuth 2.0

1. Przejdź do **APIs & Services** > **Credentials**
2. Kliknij **Create Credentials** > **OAuth 2.0 Client IDs**
3. Wybierz **Web application**
4. Dodaj **Authorized redirect URIs**:
   ```
   http://127.0.0.1:8000/accounts/google/login/callback/
   http://localhost:8000/accounts/google/login/callback/
   https://yourdomain.com/accounts/google/login/callback/
   ```

## Krok 3: Konfiguracja zmiennych środowiskowych

Dodaj do pliku `.env` lub ustaw jako zmienne środowiskowe:

```bash
# Google OAuth
GOOGLE_OAUTH2_CLIENT_ID=your_client_id_here
GOOGLE_OAUTH2_SECRET=your_client_secret_here

# Email configuration (for 2FA)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

## Krok 4: Aktualizacja ustawień Django

Dodaj do `settings.py`:

```python
# Google OAuth Configuration
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

# Social account settings
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'mandatory'
```

## Krok 5: Migracje i instalacja

```bash
# Zainstaluj nowe pakiety
pip install -r requirements.txt

# Wykonaj migracje
python manage.py makemigrations
python manage.py migrate

# Utwórz superużytkownika (jeśli nie istnieje)
python manage.py createsuperuser
```

## Krok 6: Konfiguracja w Django Admin

1. Przejdź do `/admin/`
2. W sekcji **Sites** ustaw prawidłową domenę
3. W sekcji **Social Applications** dodaj Google:
   - **Provider**: Google
   - **Name**: Google
   - **Client id**: Twój Client ID z Google Console
   - **Secret key**: Twój Client Secret z Google Console
   - **Sites**: Wybierz swoją domenę

## Testowanie

1. Uruchom serwer: `python manage.py runserver`
2. Przejdź do `/login`
3. Kliknij "Continue with Google"
4. Sprawdź czy logowanie działa

## Uwagi bezpieczeństwa

- Nigdy nie commituj Client Secret do repozytorium
- Użyj zmiennych środowiskowych dla wrażliwych danych
- W produkcji używaj HTTPS
- Regularnie rotuj klucze API



