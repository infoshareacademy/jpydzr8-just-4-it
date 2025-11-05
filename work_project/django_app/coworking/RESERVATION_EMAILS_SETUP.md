# 📧 Konfiguracja Emaili Rezerwacji

## Funkcjonalności

System automatycznie wysyła emaile związane z rezerwacjami:

1. **Email potwierdzający** - wysyłany natychmiast po utworzeniu rezerwacji
2. **Przypomnienia** - wysyłane X minut przed rozpoczęciem rezerwacji (zgodnie z ustawieniami użytkownika)
3. **Dzienne podsumowania** - wysyłane wieczorem z podsumowaniem rezerwacji na następny dzień
4. **Tygodniowe raporty** - wysyłane w niedzielę z podsumowaniem tygodnia

## Ustawienia użytkownika

Użytkownicy mogą konfigurować powiadomienia w ustawieniach:
- `/notification-settings?email=twoj_email@example.com`

**Dostępne opcje:**
- ✅ Email notifications (włącz/wyłącz wszystkie powiadomienia)
- ⏰ Reminder before booking (ilość minut przed rezerwacją - domyślnie 30)
- 📅 Daily summary (dzienne podsumowania - domyślnie włączone)
- 📊 Weekly report (tygodniowe raporty - domyślnie wyłączone)

## Automatyczne uruchamianie

Aby system automatycznie wysyłał przypomnienia i podsumowania, masz kilka opcji:

### Opcja 1: Automatyczny serwis (NAJŁATWIEJSZE) ⭐

Uruchom prosty skrypt który automatycznie sprawdza przypomnienia:

```bash
# Uruchom automatyczny serwis przypomnień (sprawdza co 5 minut)
./start_email_services.sh

# Zatrzymaj serwis
./stop_email_services.sh
```

**Lub ręcznie:**
```bash
# Uruchom w tle - sprawdza co 5 minut
python manage.py auto_send_reminders --interval 300 &

# Uruchom raz
python manage.py auto_send_reminders --once
```

### Opcja 2: Cron (Linux/Mac)

Dodaj do crontab (`crontab -e`):

```bash
# Przypomnienia - co 5 minut
*/5 * * * * cd /path/to/django_app/coworking && source .venv/bin/activate && python manage.py send_reminders

# Dzienne podsumowania - codziennie o 20:00
0 20 * * * cd /path/to/django_app/coworking && source .venv/bin/activate && python manage.py send_daily_summaries

# Tygodniowe raporty - w każdą niedzielę o 20:00
0 20 * * 0 cd /path/to/django_app/coworking && source .venv/bin/activate && python manage.py send_weekly_reports
```

### Opcja 2: Django Management Command (manual)

Uruchom ręcznie:

```bash
# Przypomnienia
python manage.py send_reminders

# Dzienne podsumowania
python manage.py send_daily_summaries

# Tygodniowe raporty
python manage.py send_weekly_reports
```

### Opcja 3: Celery (zaawansowane)

Jeśli używasz Celery, możesz dodać periodic tasks:

```python
from celery import shared_task
from celery.schedules import crontab

@shared_task
def send_reservation_reminders():
    from reservations.notification_utils import check_and_send_reminders
    return check_and_send_reminders()

@shared_task
def send_daily_summaries_task():
    from reservations.notification_utils import send_daily_summaries
    return send_daily_summaries()

# W settings.py lub celery.py
CELERY_BEAT_SCHEDULE = {
    'send-reminders-every-5-min': {
        'task': 'send_reservation_reminders',
        'schedule': crontab(minute='*/5'),
    },
    'send-daily-summaries': {
        'task': 'send_daily_summaries_task',
        'schedule': crontab(hour=20, minute=0),
    },
}
```

## Testowanie

Aby przetestować funkcjonalność:

1. **Email potwierdzający:**
   - Utwórz nową rezerwację przez dashboard
   - Sprawdź skrzynkę email

2. **Przypomnienia:**
   - Utwórz rezerwację na dziś
   - Ustaw przypomnienie na np. 5 minut przed
   - Uruchom: `python manage.py send_reminders`
   - Sprawdź skrzynkę email

3. **Dzienne podsumowania:**
   - Utwórz rezerwacje na jutro
   - Uruchom: `python manage.py send_daily_summaries`
   - Sprawdź skrzynkę email

## Uwagi

- Wszystkie emaile są wysyłane zgodnie z preferencjami użytkownika
- Jeśli użytkownik wyłączył powiadomienia email, żadne emaile nie będą wysyłane
- System używa skonfigurowanego SMTP backendu (z `.env`)
- Tłumaczenia są automatycznie ładowane na podstawie języka użytkownika

