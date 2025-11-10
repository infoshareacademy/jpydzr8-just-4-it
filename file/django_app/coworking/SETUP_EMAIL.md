# 📧 Konfiguracja Email - Krok po Kroku

## Szybki Przewodnik

### Krok 1: Utwórz Hasło Aplikacji Gmail

1. **Wejdź na stronę Google:**
   - Otwórz: https://myaccount.google.com/apppasswords
   - Zaloguj się na swoje konto Google

2. **Wybierz opcje:**
   - Aplikacja: **Mail**
   - Urządzenie: **Inne (niestandardowa nazwa)**
   - Wpisz: `Django App` lub `Just 4 IT Coworking`

3. **Skopiuj hasło:**
   - Google wygeneruje 16-znakowe hasło (np. `abcd efgh ijkl mnop`)
   - **Skopiuj je** - będzie potrzebne w następnym kroku

### Krok 2: Skonfiguruj w Django

**Opcja A: Automatyczna konfiguracja (zalecana)**

```bash
cd django_app/coworking
python manage.py setup_email \
  --email twoj_email@gmail.com \
  --password "abcd efgh ijkl mnop"
```

**Opcja B: Ręczna edycja pliku `.env`**

1. Otwórz plik: `django_app/coworking/.env`
2. Znajdź linie:
   ```bash
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password_here
   ```
3. Zamień na:
   ```bash
   EMAIL_HOST_USER=twoj_prawdziwy_email@gmail.com
   EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
   ```
   (użyj hasła aplikacji z Kroku 1)

### Krok 3: Uruchom ponownie serwer Django

```bash
# Zatrzymaj serwer (Ctrl+C)
# Uruchom ponownie
python manage.py runserver
```

### Krok 4: Sprawdź czy działa

Po uruchomieniu serwera powinieneś zobaczyć:
```
✅ Email configuration auto-saved to .env file
```

Zamiast:
```
⚠️  WARNING: Email credentials contain example values...
```

## 🔍 Testowanie

Po konfiguracji możesz przetestować wysyłanie emaili:

1. Przejdź na: http://127.0.0.1:8000/forgot-password
2. Wprowadź email użytkownika
3. Sprawdź skrzynkę email - powinieneś otrzymać wiadomość z linkiem resetującym

## ❓ Problemy?

**Email nie przychodzi:**
- Sprawdź folder Spam/Śmieci
- Upewnij się, że używasz hasła aplikacji, nie zwykłego hasła
- Sprawdź czy serwer Django nie pokazuje błędów SMTP

**Błąd uwierzytelniania:**
- Upewnij się, że używasz hasła aplikacji (16 znaków)
- Sprawdź czy włączona jest weryfikacja dwuetapowa w Google

## 📝 Dla innych dostawców email

**Outlook/Hotmail:**
```bash
python manage.py setup_email \
  --email twoj_email@outlook.com \
  --password twoje_haslo \
  --host smtp-mail.outlook.com
```

**Yahoo:**
```bash
python manage.py setup_email \
  --email twoj_email@yahoo.com \
  --password twoje_haslo \
  --host smtp.mail.yahoo.com
```

