from django.core.mail import send_mail
from django.utils import timezone
from django.template.loader import render_to_string
from django.db import models
from datetime import datetime, timedelta
from .models import Notification, UserPreferences, Reservation, Waitlist
import json

def send_notification_email(email, subject, message, notification_type='CONFIRMATION'):
    """Wyślij email z powiadomieniem"""
    try:
        # Sprawdź preferencje użytkownika
        try:
            prefs = UserPreferences.objects.get(email=email)
            if not prefs.email_notifications:
                return False
        except UserPreferences.DoesNotExist:
            pass  # Wyślij domyślnie
        
        # Wyślij email
        send_mail(
            subject=subject,
            message=message,
            from_email='noreply@office-reservations.com',
            recipient_list=[email],
            fail_silently=False,
        )
        
        # Zapisz powiadomienie w bazie
        Notification.objects.create(
            email=email,
            type=notification_type,
            title=subject,
            message=message,
            is_sent=True,
            sent_at=timezone.now()
        )
        
        return True
    except Exception as e:
        print(f"Błąd wysyłania powiadomienia: {e}")
        return False

def send_reservation_reminder(reservation):
    """Wyślij przypomnienie o rezerwacji"""
    subject = f"Przypomnienie: Rezerwacja {reservation.desk.label} za 30 minut"
    
    message = f"""
Przypomnienie o rezerwacji

Stanowisko: {reservation.desk.label} (Piętro {reservation.desk.floor.number})
Data: {reservation.date}
Godziny: {reservation.time_from} - {reservation.time_to}

Miłej pracy!

---
System rezerwacji stanowisk
    """
    
    return send_notification_email(
        reservation.email, 
        subject, 
        message, 
        'REMINDER'
    )

def send_waitlist_notification(waitlist_entry):
    """Wyślij powiadomienie z waitlist"""
    subject = f"Stanowisko {waitlist_entry.desk.label} jest dostępne!"
    
    message = f"""
Stanowisko się zwolniło!

Stanowisko: {waitlist_entry.desk.label} (Piętro {waitlist_entry.desk.floor.number})
Data: {waitlist_entry.preferred_date}
Godziny: {waitlist_entry.time_from} - {waitlist_entry.time_to}

Masz 24 godziny na potwierdzenie rezerwacji.

---
System rezerwacji stanowisk
    """
    
    return send_notification_email(
        waitlist_entry.email, 
        subject, 
        message, 
        'WAITLIST'
    )

def send_daily_summary(email, reservations):
    """Wyślij dzienne podsumowanie"""
    if not reservations:
        return
    
    subject = f"Podsumowanie rezerwacji na {reservations[0].date}"
    
    message = f"""
Dzienne podsumowanie rezerwacji

Masz {len(reservations)} rezerwacji na {reservations[0].date}:

"""
    
    for res in reservations:
        message += f"• {res.desk.label} (Piętro {res.desk.floor.number}) - {res.time_from} - {res.time_to}\n"
    
    message += """
Miłego dnia!

---
System rezerwacji stanowisk
    """
    
    return send_notification_email(
        email, 
        subject, 
        message, 
        'DAILY_SUMMARY'
    )

def send_weekly_report(email, stats):
    """Wyślij tygodniowy raport"""
    subject = "Tygodniowy raport rezerwacji"
    
    message = f"""
Tygodniowy raport rezerwacji

Liczba rezerwacji: {stats.get('total_reservations', 0)}
Ulubione stanowisko: {stats.get('favorite_desk', 'Brak')}
Ulubione piętro: {stats.get('favorite_floor', 'Brak')}
Średni czas rezerwacji: {stats.get('avg_duration', 'Brak')} godzin

Dziękujemy za korzystanie z systemu rezerwacji!

---
System rezerwacji stanowisk
    """
    
    return send_notification_email(
        email, 
        subject, 
        message, 
        'WEEKLY_REPORT'
    )

def send_cancellation_notification(reservation):
    """Wyślij powiadomienie o anulowaniu"""
    subject = f"Rezerwacja {reservation.desk.label} została anulowana"
    
    message = f"""
Rezerwacja została anulowana

Stanowisko: {reservation.desk.label} (Piętro {reservation.desk.floor.number})
Data: {reservation.date}
Godziny: {reservation.time_from} - {reservation.time_to}

Stanowisko jest ponownie dostępne dla innych.

---
System rezerwacji stanowisk
    """
    
    return send_notification_email(
        reservation.email, 
        subject, 
        message, 
        'CANCELLATION'
    )

def check_and_send_reminders():
    """Sprawdź i wyślij przypomnienia o rezerwacjach"""
    now = timezone.now()
    reminder_time = now + timedelta(minutes=30)
    
    # Znajdź rezerwacje za 30 minut
    reservations = Reservation.objects.filter(
        date=now.date(),
        time_from__hour=reminder_time.hour,
        time_from__minute=reminder_time.minute,
        is_cancelled=False
    )
    
    sent_count = 0
    for reservation in reservations:
        try:
            prefs = UserPreferences.objects.get(email=reservation.email)
            if prefs.reminder_before_booking == 30:  # Tylko dla 30-minutowych przypomnień
                if send_reservation_reminder(reservation):
                    sent_count += 1
        except UserPreferences.DoesNotExist:
            if send_reservation_reminder(reservation):
                sent_count += 1
    
    return sent_count

def send_daily_summaries():
    """Wyślij dzienne podsumowania"""
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    # Znajdź wszystkich użytkowników z rezerwacjami na jutro
    reservations = Reservation.objects.filter(
        date=tomorrow,
        is_cancelled=False
    ).order_by('email', 'time_from')
    
    # Grupuj po emailu
    user_reservations = {}
    for res in reservations:
        if res.email not in user_reservations:
            user_reservations[res.email] = []
        user_reservations[res.email].append(res)
    
    sent_count = 0
    for email, user_res in user_reservations.items():
        try:
            prefs = UserPreferences.objects.get(email=email)
            if prefs.daily_summary:
                if send_daily_summary(email, user_res):
                    sent_count += 1
        except UserPreferences.DoesNotExist:
            if send_daily_summary(email, user_res):
                sent_count += 1
    
    return sent_count

def send_weekly_reports():
    """Wyślij tygodniowe raporty"""
    # Znajdź użytkowników z włączonymi raportami tygodniowymi
    users_with_reports = UserPreferences.objects.filter(weekly_report=True)
    
    sent_count = 0
    for prefs in users_with_reports:
        # Oblicz statystyki z ostatniego tygodnia
        week_ago = timezone.now().date() - timedelta(days=7)
        reservations = Reservation.objects.filter(
            email=prefs.email,
            date__gte=week_ago,
            is_cancelled=False
        )
        
        if reservations.exists():
            # Oblicz statystyki
            stats = {
                'total_reservations': reservations.count(),
                'favorite_desk': reservations.values('desk__label').annotate(count=models.Count('id')).order_by('-count').first()['desk__label'] if reservations.exists() else 'Brak',
                'favorite_floor': reservations.values('desk__floor__number').annotate(count=models.Count('id')).order_by('-count').first()['desk__floor__number'] if reservations.exists() else 'Brak',
                'avg_duration': 'N/A'  # Można dodać obliczenia
            }
            
            if send_weekly_report(prefs.email, stats):
                sent_count += 1
    
    return sent_count
