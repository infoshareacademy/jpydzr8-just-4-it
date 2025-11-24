# System Rezerwacji Stanowisk Coworkingowych

Aplikacja Django do zarządzania rezerwacjami stanowisk w przestrzeni coworkingowej. System wspiera rezerwacje indywidualne, grupowe, cykliczne oraz rezerwacje sal konferencyjnych.

## 🚀 Szybki Start

### Wymagania

- Python 3.10+ (pobierz z https://www.python.org/downloads/)
- Virtualenv (lub venv - wbudowane w Python 3.10+)
- PowerShell 5.1+ lub Windows Terminal (zalecane)
- Node.js i npm (opcjonalnie, tylko dla assetów frontendowych)
- GNU gettext (opcjonalnie, potrzebne do kompilacji tłumaczeń - zobacz SETUP.md)

### Instalacja

1. **Sklonuj repozytorium i przejdź do katalogu projektu:**
   ```bash
   cd django_app/coworking
   ```

2. **Utwórz i aktywuj środowisko wirtualne:**
   
   **Windows (PowerShell):**
   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```
   
   **Windows (CMD):**
   ```cmd
   python -m venv venv
   venv\Scripts\activate.bat
   ```
   
   > **Uwaga:** Jeśli w PowerShell dostaniesz błąd o wykonywaniu skryptów, uruchom:
   > ```powershell
   > Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   > ```
   
   **macOS/Linux:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Zainstaluj zależności:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Skonfiguruj zmienne środowiskowe:**
   
   **Windows:**
   ```powershell
   # PowerShell
   Copy-Item env.example .env
   
   # Lub w CMD
   copy env.example .env
   ```
   
   Następnie otwórz plik `.env` w Notatniku lub innym edytorze i uzupełnij wymagane wartości.
   Szczegółowe instrukcje znajdziesz w pliku SETUP.md

5. **Wykonaj migracje bazy danych:**
   ```bash
   python manage.py migrate
   ```
   
   > **Uwaga:** Migracje automatycznie utworzą podstawowe dane:
   > - Piętra 4, 5, 6, 7
   > - Strefy (Open Workspace, Deep Work, Chill Room, Kuchnia)
   > - Przykładowe stanowiska na każdym piętrze
   > - Sale konferencyjne dla każdego piętra
   > 
   > Nie musisz uruchamiać `seed_office` - wszystko jest już w migracjach!

6. **Utwórz superużytkownika (opcjonalnie):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Uruchom serwer deweloperski:**
   ```bash
   python manage.py runserver
   ```

8. **Otwórz przeglądarkę:**
   - Główna aplikacja: http://127.0.0.1:8000
   - Panel administracyjny: http://127.0.0.1:8000/admin

## 📚 Dokumentacja

- **[SETUP.md](SETUP.md)** - Szczegółowe instrukcje konfiguracji wszystkich funkcjonalności (email, powiadomienia, Google OAuth, Slack)
- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Rozszerzony przewodnik instalacji z dodatkowymi informacjami

## 🔧 Główne Funkcjonalności

- ✅ Rezerwacje indywidualne stanowisk
- ✅ Rezerwacje grupowe (wspólne rezerwacje dla zespołów)
- ✅ Rezerwacje cykliczne (tygodniowe, miesięczne)
- ✅ Rezerwacje sal konferencyjnych
- ✅ System powiadomień email i push
- ✅ Logowanie przez Google OAuth
- ✅ Dwuskładnikowe uwierzytelnienie (2FA) przez email
- ✅ Magic Link - logowanie bez hasła
- ✅ Integracja ze Slack (opcjonalnie)
- ✅ Dashboard z kalendarzem rezerwacji
- ✅ Raporty tygodniowe i dzienne
- ✅ Inteligentne rekomendacje stanowisk (AI)

## 📁 Struktura Projektu

```
coworking/
├── api/                    # Aplikacja API - autoryzacja, użytkownicy
│   ├── models.py          # Modele użytkowników, rezerwacji (legacy)
│   ├── views.py           # Endpointy API
│   └── management/        # Komendy zarządzania
├── reservations/          # Aplikacja rezerwacji
│   ├── models.py         # Modele rezerwacji, stanowisk, sal
│   ├── views.py          # Widoki rezerwacji
│   ├── forms.py          # Formularze Django
│   └── management/       # Komendy automatyczne (przypomnienia, raporty)
├── coworking/            # Konfiguracja projektu Django
│   ├── settings.py       # Ustawienia projektu
│   └── urls.py           # Główny routing
├── templates/            # Szablony HTML
├── static/               # Pliki statyczne (CSS, JS, obrazy)
├── locale/               # Pliki tłumaczeń (i18n)
└── manage.py             # Skrypt zarządzania Django
```

## 🛠️ Przydatne Komendy

### Zarządzanie danymi

```bash
# Utwórz superużytkownika
python manage.py createsuperuser

# Wykonaj migracje
python manage.py migrate
python manage.py makemigrations

# Dane testowe są automatycznie tworzone podczas migracji!
# Jeśli chcesz zaktualizować dane, możesz użyć:
python manage.py seed_office
```

### Tłumaczenia

```powershell
# Skompiluj tłumaczenia
python manage.py compilemessages

# Tylko dla języka polskiego
python manage.py compilemessages -l pl
```

> **Uwaga dla Windows**: Jeśli dostaniesz błąd `Can't find msgfmt`, musisz zainstalować GNU gettext:
> 
> **Szybka instalacja przez Chocolatey:**
> ```powershell
> choco install gettext
> ```
> 
> **Lub ręcznie:** 
> 1. Pobierz z https://mlocati.github.io/articles/gettext-iconv-windows.html
> 2. Rozpakuj i dodaj folder `bin` do zmiennej środowiskowej PATH
> 3. Zrestartuj terminal
> 
> Zobacz więcej szczegółów w `SETUP.md`.

### Automatyczne powiadomienia

```powershell
# Uruchom serwis przypomnień (sprawdza co 5 minut)
python manage.py auto_send_reminders --interval 300

# Wyślij dzienne podsumowania
python manage.py send_daily_summaries

# Wyślij tygodniowe raporty
python manage.py send_weekly_reports
```

> **Uwaga dla Windows:** Dla automatycznego uruchamiania użyj Task Scheduler. Szczegółowe instrukcje znajdziesz w `SETUP.md` w sekcji "Automatyczne Powiadomienia".

### Inne komendy

```powershell
# Python shell Django
python manage.py shell

# Export danych (Windows)
python manage.py dumpdata reservations.Reservation > backup.json

# Export danych z UTF-8 (jeśli są problemy z kodowaniem)
python manage.py dumpdata reservations.Reservation | Out-File -Encoding utf8 backup.json

# Import danych
python manage.py loaddata backup.json
```

## 🔐 Konfiguracja Bezpieczeństwa

### Wymagane dla działania aplikacji:

1. **SECRET_KEY** - Zmień domyślną wartość w `.env`
2. **Email SMTP** - Konfiguracja do wysyłki maili (2FA, przypomnienia)
3. **Google OAuth** - Do logowania przez Google

### Opcjonalne:

- **Web Push** - Powiadomienia przeglądarkowe
- **Slack** - Integracja z Slack botem

Szczegółowe instrukcje konfiguracji znajdziesz w [SETUP.md](SETUP.md).

## 🌐 Środowisko Produkcyjne

### Przed wdrożeniem:

1. Ustaw `DEBUG=False` w `.env`
2. Zmień `SECRET_KEY` na bezpieczną losową wartość
3. Skonfiguruj właściwy `ALLOWED_HOSTS`
4. Użyj produkcyjnej bazy danych (PostgreSQL zalecane)
5. Skonfiguruj HTTPS (wymagane dla Web Push)
6. Ustaw właściwe `CORS_ALLOWED_ORIGINS`
7. Wygeneruj nowe klucze VAPID dla Web Push

### Przykładowa konfiguracja produkcji:

```bash
DEBUG=False
SECRET_KEY=<wygeneruj_bezpieczny_klucz>
ALLOWED_HOSTS=twoja-domena.com,www.twoja-domena.com
CORS_ALLOWED_ORIGINS=https://twoja-domena.com
EMAIL_HOST=smtp.twoja-domena.com
```

## 🐛 Rozwiązywanie Problemów

### Maile nie są wysyłane

- Sprawdź logi serwera - Django pokaże błędy SMTP
- Upewnij się, że App Password w `.env` jest poprawny (16 znaków, bez spacji)
- Sprawdź ustawienia zapory sieciowej
- W trybie dev maile są wyświetlane w konsoli

### Google OAuth nie działa

- Sprawdź czy URI w Google Cloud Console są identyczne z adresem testowym
- Pamiętaj o dodaniu zarówno `localhost` jak i `127.0.0.1`
- Zweryfikuj Client ID i Client Secret w `.env`

### Web Push nie działa

- Sprawdź konsolę przeglądarki (F12) - zobaczysz błędy Service Worker
- Web Push wymaga HTTPS (lub localhost w dev)
- Sprawdź czy klucze VAPID są poprawnie skonfigurowane
- Sprawdź logi backendu - subskrypcje wygasłe są automatycznie wyłączane

### Błąd `Can't find msgfmt`

- Na Windows musisz zainstalować GNU gettext
- **Szybka instalacja przez Chocolatey:**
  ```powershell
  choco install gettext
  ```
- **Lub ręcznie:** Pobierz z https://mlocati.github.io/articles/gettext-iconv-windows.html
- Zobacz szczegóły w `SETUP.md` w sekcji o tłumaczeniach

### Problem z kodowaniem znaków w terminalu Windows

- Jeśli widzisz zniekształcone znaki, ustaw kodowanie UTF-8:
  ```powershell
  # PowerShell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  ```
- Lub użyj Windows Terminal zamiast zwykłego CMD

## 📝 Licencja

[Wpisz informacje o licencji]

## 👥 Autorzy

[Wpisz informacje o autorach]

## 🤝 Wsparcie

W razie problemów sprawdź:
1. Plik `SETUP.md` z szczegółowymi instrukcjami konfiguracji
2. Logi aplikacji w katalogu `logs/`
3. Dokumentację Django: https://docs.djangoproject.com/

---

**Gotowe do działania!** 🎉

Po podstawowej konfiguracji uruchom `python manage.py runserver` i wejdź na http://127.0.0.1:8000
