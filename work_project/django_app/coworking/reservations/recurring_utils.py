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
                Reservation.objects.create(
                    desk=recurring.desk,
                    name=recurring.name,
                    email=recurring.email,
                    date=reservation_date,
                    time_from=recurring.time_from,
                    time_to=recurring.time_to
                )
                created_count += 1
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
    
    return created_count

def get_recurring_dates(start_date, end_date, frequency, days_of_week):
    """Generuje listę dat na podstawie częstotliwości i dni tygodnia"""
    dates = []
    current_date = start_date
    
    while current_date <= end_date:
        if frequency == 'DAILY':
            if should_include_date(current_date, days_of_week):
                dates.append(current_date)
            current_date += timedelta(days=1)
        elif frequency == 'WEEKLY':
            if should_include_date(current_date, days_of_week):
                dates.append(current_date)
            current_date += timedelta(days=7)
        elif frequency == 'MONTHLY':
            if should_include_date(current_date, days_of_week):
                dates.append(current_date)
            # Przejdź do następnego miesiąca
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
    
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

