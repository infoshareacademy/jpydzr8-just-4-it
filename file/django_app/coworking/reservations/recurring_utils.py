from datetime import datetime, date, timedelta
from django.utils import timezone
from .models import RecurringReservation, Reservation, Waitlist
from .ai_utils import is_available

def generate_recurring_reservations():
    """Generuje rezerwacje na podstawie recurring reservations"""
    today = date.today()
    end_date = today + timedelta(days=30)  # Generuj na 30 dni do przodu
    
    recurring_reservations = RecurringReservation.objects.filter(
        is_active=True,
        start_date__lte=today
    )
    
    created_count = 0
    
    for recurring in recurring_reservations:
        # Sprawdź czy nie ma już wygasłej daty końcowej
        if recurring.end_date and recurring.end_date < today:
            continue
            
        # Generuj daty na podstawie częstotliwości
        dates = get_recurring_dates(
            recurring.start_date,
            end_date,
            recurring.frequency,
            recurring.days_of_week
        )
        
        # Znajdź pierwszą datę rezerwacji, która będzie utworzona (dla informacyjnego emaila)
        first_reservation_date = None
        
        for reservation_date in dates:
            # Sprawdź czy rezerwacja już istnieje
            if Reservation.objects.filter(
                desk=recurring.desk,
                date=reservation_date,
                time_from=recurring.time_from,
                time_to=recurring.time_to,
                is_cancelled=False
            ).exists():
                continue
            
            # Sprawdź dostępność
            if is_available(recurring.desk, reservation_date, recurring.time_from, recurring.time_to):
                # Utwórz rezerwację
                reservation = Reservation.objects.create(
                    desk=recurring.desk,
                    name=recurring.name,
                    email=recurring.email,
                    date=reservation_date,
                    time_from=recurring.time_from,
                    time_to=recurring.time_to
                )
                created_count += 1
                
                # Zapamiętaj pierwszą rezerwację dla emaila informacyjnego
                if first_reservation_date is None:
                    first_reservation_date = reservation
            else:
                # Dodaj do waitlist jeśli stanowisko zajęte
                if not Waitlist.objects.filter(
                    desk=recurring.desk,
                    preferred_date=reservation_date,
                    time_from=recurring.time_from,
                    time_to=recurring.time_to,
                    email=recurring.email
                ).exists():
                    Waitlist.objects.create(
                        desk=recurring.desk,
                        name=recurring.name,
                        email=recurring.email,
                        preferred_date=reservation_date,
                        time_from=recurring.time_from,
                        time_to=recurring.time_to
                    )
        
        # Wyślij email informacyjny tylko o pierwszej utworzonej rezerwacji z cyklu
        if first_reservation_date:
            try:
                from .views import send_reservation_email
                send_reservation_email(first_reservation_date)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f'Błąd podczas wysyłki emaila informacyjnego dla rezerwacji cyklicznej {first_reservation_date.id}: {e}')
    
    return created_count

def get_recurring_dates(start_date, end_date, frequency, days_of_week):
    """Generuje listę dat na podstawie częstotliwości i dni tygodnia"""
    dates = []
    current_date = start_date
    
    if frequency == 'DAILY':
        # Codziennie - sprawdź każdy dzień
        while current_date <= end_date:
            if should_include_date(current_date, days_of_week):
                dates.append(current_date)
            current_date += timedelta(days=1)
    
    elif frequency == 'WEEKLY':
        # Tygodniowo - znajdź wszystkie wybrane dni w każdym tygodniu
        # Znajdź pierwszy dzień tygodnia (poniedziałek) od start_date
        days_since_monday = current_date.weekday()  # 0=Monday, 6=Sunday
        week_start = current_date - timedelta(days=days_since_monday)
        
        # Przejdź przez wszystkie tygodnie do end_date
        while week_start <= end_date:
            # Sprawdź wszystkie 7 dni w tym tygodniu
            for day_offset in range(7):
                check_date = week_start + timedelta(days=day_offset)
                if check_date < start_date:
                    continue  # Skip dates before start_date
                if check_date > end_date:
                    break  # Stop if we've passed end_date
                if should_include_date(check_date, days_of_week):
                    dates.append(check_date)
            # Przejdź do następnego tygodnia
            week_start += timedelta(days=7)
    
    elif frequency == 'MONTHLY':
        # Miesięcznie - znajdź wybrane dni w każdym miesiącu
        current_month_start = start_date.replace(day=1)
        
        while current_month_start <= end_date:
            # Sprawdź wszystkie dni w miesiącu
            if current_month_start.month == 12:
                next_month = current_month_start.replace(year=current_month_start.year + 1, month=1, day=1)
            else:
                next_month = current_month_start.replace(month=current_month_start.month + 1, day=1)
            
            check_date = current_month_start
            while check_date < next_month and check_date <= end_date:
                if check_date >= start_date and should_include_date(check_date, days_of_week):
                    dates.append(check_date)
                check_date += timedelta(days=1)
            
            # Przejdź do następnego miesiąca
            current_month_start = next_month
    
    return dates

def should_include_date(check_date, days_of_week):
    """Sprawdza czy data powinna być uwzględniona na podstawie dni tygodnia"""
    # days_of_week to string '1111111' gdzie 1=Monday, 7=Sunday
    weekday = check_date.weekday()  # 0=Monday, 6=Sunday
    return days_of_week[weekday] == '1'

def check_waitlist_availability():
    """Sprawdza czy są dostępne stanowiska dla osób z waitlist"""
    today = date.today()
    future_date = today + timedelta(days=7)
    
    waitlist_entries = Waitlist.objects.filter(
        preferred_date__gte=today,
        preferred_date__lte=future_date,
        is_notified=False
    ).order_by('created_at')
    
    notified_count = 0
    
    for entry in waitlist_entries:
        if is_available(entry.desk, entry.preferred_date, entry.time_from, entry.time_to):
            # Wyślij powiadomienie (tutaj można dodać email/SMS)
            entry.is_notified = True
            entry.save()
            notified_count += 1
    
    return notified_count

def cancel_recurring_reservation(recurring_id, end_date=None):
    """Anuluje recurring reservation"""
    try:
        recurring = RecurringReservation.objects.get(id=recurring_id)
        if end_date:
            recurring.end_date = end_date
            recurring.save()
        else:
            recurring.is_active = False
            recurring.save()
        return True
    except RecurringReservation.DoesNotExist:
        return False

