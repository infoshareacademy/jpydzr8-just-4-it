# Coworking – mój mega prosty setup krok po kroku

Poniżej rozpisałem wszystko, co zrobiłem, żeby każdy z nas mógł w kilka minut postawić środowisko dev z Google OAuth, SMTP i powiadomieniami push. Jeśli będziemy trzymać się listy kroków, każdy przejdzie proces bez pytania „co dalej?”.

---

## Krok 0. Co musisz mieć zainstalowane
1. **Python 3.13** – najlepiej sprawdź `python --version`.  
2. **Virtualenv** – standardowo tworzymy `coworking/venv`.  
3. **Opcjonalnie Node/npm** – tylko jeśli ruszasz assety frontowe.  
4. **Konto w Google Cloud** – do logowania OAuth.  
5. **Konto pocztowe** (np. Gmail) – App Password do SMTP.  
6. **Przeglądarka obsługująca push** – Chrome/Firefox na `https` lub `http://localhost`.

---

## Krok 1. Skopiuj repo i odpal virtualenv
```bash
cd django_app/coworking
python -m venv venv
venv\Scripts\activate            # Windows
# lub source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

> Jeśli `pip install` wyrzuci brakujące pakiety, uruchom go ponownie – w requirements mamy wszystko (łącznie z pywebpush).

---

## Krok 2. Przygotuj plik `.env`
1. Skopiuj `env_example.txt` → `.env` w tym samym katalogu.
2. Uzupełnij wartości według poniższych kroków. Każda sekcja jest opisana osobno.

### 2.1 Ogólne ustawienia
- `SECRET_KEY` – wpisz dowolny ciąg znaków (np. wygeneruj w Pythonie).  
- `DEBUG=True` – na dev zostawiam włączone.  
- `ALLOWED_HOSTS=localhost,127.0.0.1` – tyle wystarczy.  
- `CORS_ALLOWED_ORIGINS` – ustaw tylko jeśli masz osobny frontend.

### 2.2 SMTP – wysyłka maili (Gmail)
1. Wchodzisz na [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).  
2. Tworzysz App Password (wybierz „Mail” → „Other” → np. „Coworking dev”).  
3. W `.env` ustawiasz:
   ```
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=twoj.email@gmail.com
   EMAIL_HOST_PASSWORD=TU_WKLEJ_APP_PASSWORD
   DEFAULT_FROM_EMAIL=noreply@twojadomena.com
   ```
4. Jeśli czegoś brakuje, Django wyświetli w logach ostrzeżenie i przełączy się na backend konsolowy (maile będą wypisywane w terminalu).

### 2.3 Google OAuth – logowanie przez Google
Poniżej dokładny przepis, żeby każdy mógł samodzielnie skonfigurować logowanie przez Google:

1. **Zaloguj się** na konto Google, które ma dostęp do [Google Cloud Console](https://console.cloud.google.com/).  
2. Wybierz istniejący projekt albo kliknij „Select a project” → „New Project” (np. nazwij go `Coworking Dev`).  
3. Po utworzeniu projektu kliknij w lewym menu **APIs & Services → OAuth consent screen**:
   - Tryb: `Internal` (w dev wystarczy, jeśli konto należy do tej samej organizacji Google Workspace; jeśli nie – wybierz `External`).
   - Nazwa aplikacji: wpisz cokolwiek sensownego (`Coworking Dev Login`).
   - Contact email: swój adres.
   - W sekcji Scopes nic nie dodawałem – domyślne wystarczą.
   - W sekcji Test users dodaj swój adres Gmail (i ewentualnie innych z zespołu).
   - Kliknij „Save and Continue” aż do końca.
4. Teraz wchodzimy w **APIs & Services → Credentials**:
   - Kliknij „Create Credentials” → „OAuth client ID”.
   - Typ aplikacji: `Web application`.
   - Nazwa klienta: np. `Coworking Dev Local`.
   - W sekcji **Authorized JavaScript origins** dodaj:
     - `http://127.0.0.1:8000`
     - `http://localhost:8000`
   - W sekcji **Authorized redirect URIs** dodaj:
     - `http://127.0.0.1:8000/accounts/google/login/callback/`
     - `http://localhost:8000/accounts/google/login/callback/`
   - Kliknij „Create”.
5. Wyskoczy modal z `Client ID` i `Client Secret`. Skopiuj je i dopisz do `.env`:
   ```
   GOOGLE_OAUTH2_CLIENT_ID=tu_wklej_client_id
   GOOGLE_OAUTH2_SECRET=tu_wklej_client_secret
   ```
6. W repo nic więcej ustawiać nie trzeba (`SITE_ID = 1` i odpowiednie backendy są już skonfigurowane w `settings.py`).
7. Uruchom ponownie serwer (`python manage.py runserver`), wejdź na `/login` i przetestuj „Zaloguj przez Google”.
8. Jeśli Google pokaże komunikat „This app isn’t verified” – to normalne przy devowych ustawieniach w trybie testowym; kliknij „Continue”.  
9. Gdy pojawi się błąd `invalid redirect`, wróć do kroku 4 i upewnij się, że wszystkie URI są dokładnie takie jak adres, pod którym testujesz (często literówka albo brak `localhost` vs `127.0.0.1`).
10. Dodatkowe screeny i opis znajdziesz też w pliku `GOOGLE_OAUTH_SETUP.md`, ale powyższa lista wystarcza, żeby puścić logowanie w zespole.

### 2.4 Powiadomienia push (Web Push)
1. Wygeneruj klucze VAPID:  
   ```bash
   python -m py_vapid generate
   ```
   Jeśli nie chcesz bawić się teraz, możesz wkleić nasze devowe wartości:
   ```
   WEBPUSH_VAPID_PUBLIC_KEY=BLejcM9BvIV4NvkAcUC0PDZYyY4tFQdYnE-wBJwdPqZ6k-p2R_tUBGDKZYZg2YXkCDd-pJc06cVyk3yDUGTT-H0
   WEBPUSH_VAPID_PRIVATE_KEY=j3b_zKixil37XRpLjuU3Oum5j4IUprDDOvU7-pY3YAc
   WEBPUSH_VAPID_CLAIM=mailto:notifications@localhost
   ```
2. W produkcji wygeneruj nowe klucze i zaktualizuj `CLAIM` na własny e-mail/domenę.

> Tip: po restarcie serwera w logach zobaczysz info, czy konfiguracja Web Push się włączyła.

---

## Krok 3. Migracje i start dev servera
```bash
python manage.py migrate
python manage.py runserver
```

Teraz masz dostępne:
- `http://127.0.0.1:8000/` – panel rezerwacji.
- `/reservations/notification-settings/` – ustawienia powiadomień (tu testujemy push).
- `/admin/` – panel Django (najpierw `python manage.py createsuperuser`).
- `/api/...` – endpointy REST.

---

## Krok 4. Test logowania przez Google
1. Odpal `http://127.0.0.1:8000/login`.
2. Kliknij „Zaloguj przez Google”.
3. Jeśli wszystko jest dobrze ustawione, Google powinno Cię przepuścić i przekierować z powrotem.
4. Gdy pojawi się błąd `invalid redirect`, wróć do Cloud Console i popraw URI (u mnie raz literówki zrobiły robotę).

---

## Krok 5. Test SMTP
1. Utwórz konto (lub podepnij już istniejące).
2. W panelu spróbuj zresetować hasło, włączyć 2FA albo wyślij powiadomienie manualnie.
3. Jeśli maile nie przychodzą:
   - sprawdź log serwera – błędy SMTP są tam opisane,
   - upewnij się, że App Password w `.env` ma odpowiedni format (16 znaków, bez spacji).

---

## Krok 6. Test powiadomień push
1. Wejdź na `/reservations/notification-settings/`.
2. Kliknij „Włącz powiadomienia” → zaakceptuj prośbę w przeglądarce.
3. Kliknij „Test Notification”. Jeśli wszystko gra, dostaniesz powiadomienie systemowe.
4. Dla pewności w logach sprawdź moduł `reservations.push_notifications` – znajdziesz tam info o powodzeniu lub błędach (np. jeśli subskrypcja wygasła).
5. Przy okazji sprawdź, że powiadomienie dotyczy właściwego maila (ten sam co w formularzu).

---

## Przydatne komendy, które używam
- `python manage.py createsuperuser` – lokalny admin.
- `python manage.py compilemessages -l pl` – po zmianach w tłumaczeniach.
- `python manage.py shell` – szybkie testy w Pythonie.
- `python manage.py dumpdata reservations.Reservation` – zrzut rezerwacji (np. backup dev).

---

## Typowe problemy i jak je ogarnąć
- **Maile nie przychodzą** – w logach zobaczysz, czy brakuje App Password; jeśli tak, popraw `.env`.  
- **Google OAuth krzyczy o redirect** – zwykle literówka w URI; pamiętaj o obu wersjach hosta (localhost i 127.0.0.1).  
- **Push nie działa** – sprawdź konsolę przeglądarki (czy pobrano publiczny klucz i zarejestrowano Service Worker). W logach backendu zobaczysz status – jeśli subskrypcja jest martwa, backend ją automatycznie wyłączy.  
- **Klucze VAPID** – devowe są w repo, bo nie są wrażliwe. Produkcyjne trzymaj w secretach, nie commituj.

---

## Na koniec
Jeśli potrzebujesz danych do kont pocztowych, Google itp., zapisujemy je w vaultcie zespołu – nie w repo. README ma być na tyle bezpieczny, żeby można go było wrzucić na GitHuba.  

Powodzenia! Jak coś nie działa, dopiszemy kolejne kroki do tego pliku. 💪
