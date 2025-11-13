import logging
from django.core.mail import send_mail
from django.utils import timezone
from django.template.loader import render_to_string
from django.db import models
from django.conf import settings
from datetime import datetime, timedelta
from .models import Notification, UserPreferences, Reservation, Waitlist
import json
from .push_notifications import send_push_notification, is_webpush_enabled

logger = logging.getLogger(__name__)

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
        
        # Wyślij email używając skonfigurowanego backendu
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        # Zapisz powiadomienie w bazie (jeśli model istnieje)
        try:
            Notification.objects.create(
                email=email,
                type=notification_type,
                title=subject,
                message=message,
                is_sent=True,
                sent_at=timezone.now()
            )
        except Exception:
            pass  # Ignoruj jeśli model nie istnieje
        
        # Wyślij powiadomienie push (jeśli skonfigurowane)
        if is_webpush_enabled():
            send_push_notification(
                email,
                subject,
                message,
                data={
                    'notification_type': notification_type,
                    'generated_at': timezone.now().isoformat(),
                },
                tag=notification_type.lower(),
            )

        return True
    except Exception as e:
        logger.exception("Błąd wysyłania powiadomienia email/push: {0}".format(e))
        return False

def send_reservation_reminder(reservation, minutes_before=30):
    """Wyślij przypomnienie o rezerwacji"""
    from django.utils.translation import gettext as _
    
    subject = _("Reminder: Reservation %(desk)s in %(minutes)d minutes") % {
        'desk': reservation.desk.label if hasattr(reservation, 'desk') else reservation.seat_id,
        'minutes': minutes_before
    }
    
    # Formatuj datę i czas
    if hasattr(reservation, 'date') and hasattr(reservation, 'time_from'):
        date_str = reservation.date.strftime('%Y-%m-%d') if hasattr(reservation.date, 'strftime') else str(reservation.date)
        time_str = f"{reservation.time_from} - {reservation.time_to}" if hasattr(reservation, 'time_to') else str(reservation.time_from)
        desk_label = reservation.desk.label if hasattr(reservation, 'desk') else reservation.seat_id
        floor_info = f" (Floor {reservation.desk.floor.number})" if hasattr(reservation, 'desk') and hasattr(reservation.desk, 'floor') else ""
    else:
        # Dla modelu Reservation z api/models.py
        date_str = reservation.date
        time_str = "All day"
        desk_label = reservation.seat_id
        floor_info = ""
    
    message = _("""
Reservation Reminder

Desk: %(desk)s%(floor)s
Date: %(date)s
Time: %(time)s

Have a great day!

---
Just 4 IT Coworking Reservation System
    """) % {
        'desk': desk_label,
        'floor': floor_info,
        'date': date_str,
        'time': time_str
    }
    
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
    from django.utils.translation import gettext as _
    
    if not reservations:
        return False
    
    # Pobierz datę z pierwszej rezerwacji
    first_res = reservations[0]
    if hasattr(first_res, 'date'):
        date_str = first_res.date.strftime('%Y-%m-%d') if hasattr(first_res.date, 'strftime') else str(first_res.date)
    else:
        date_str = str(first_res.date)
    
    subject = _("Reservation Summary for %(date)s") % {'date': date_str}
    
    message = _("""
Daily Reservation Summary

You have %(count)d reservation(s) for %(date)s:

""") % {'count': len(reservations), 'date': date_str}
    
    for res in reservations:
        if hasattr(res, 'desk'):
            desk_label = res.desk.label
            floor_info = f" (Floor {res.desk.floor.number})" if hasattr(res.desk, 'floor') else ""
            time_info = f"{res.time_from} - {res.time_to}" if hasattr(res, 'time_to') else str(res.time_from)
        else:
            desk_label = res.seat_id
            floor_info = ""
            time_info = "All day"
        
        message += f"• {desk_label}{floor_info} - {time_info}\n"
    
    message += _("""
Have a great day!

---
Just 4 IT Coworking Reservation System
    """)
    
    return send_notification_email(
        email, 
        subject, 
        message, 
        'DAILY_SUMMARY'
    )

def send_weekly_report(email, stats):
    """Wyślij tygodniowy raport"""
    from django.utils.translation import gettext as _
    
    subject = _("Weekly Reservation Report")
    
    message = _("""
Weekly Reservation Report

Total reservations: %(total)d
Favorite desk: %(desk)s
Favorite floor: %(floor)s
Average duration: %(duration)s hours

Thank you for using Just 4 IT Coworking!

---
Just 4 IT Coworking Reservation System
    """) % {
        'total': stats.get('total_reservations', 0),
        'desk': stats.get('favorite_desk', _('None')),
        'floor': stats.get('favorite_floor', _('None')),
        'duration': stats.get('avg_duration', 'N/A')
    }
    
    return send_notification_email(
        email, 
        subject, 
        message, 
        'WEEKLY_REPORT'
    )

def send_reservation_confirmation(reservation):
    """Wyślij email potwierdzający utworzenie rezerwacji"""
    from django.utils.translation import gettext as _
    
    subject = _("Reservation Confirmed: %(desk)s") % {
        'desk': reservation.desk.label if hasattr(reservation, 'desk') else reservation.seat_id
    }
    
    # Formatuj informacje o rezerwacji
    if hasattr(reservation, 'date') and hasattr(reservation, 'time_from'):
        date_str = reservation.date.strftime('%Y-%m-%d') if hasattr(reservation.date, 'strftime') else str(reservation.date)
        time_str = f"{reservation.time_from} - {reservation.time_to}" if hasattr(reservation, 'time_to') else str(reservation.time_from)
        desk_label = reservation.desk.label if hasattr(reservation, 'desk') else reservation.seat_id
        floor_info = f" (Floor {reservation.desk.floor.number})" if hasattr(reservation, 'desk') and hasattr(reservation.desk, 'floor') else ""
    else:
        date_str = reservation.date
        time_str = "All day"
        desk_label = reservation.seat_id
        floor_info = ""
    
    message = _("""
Reservation Confirmed

Your reservation has been successfully created!

Desk: %(desk)s%(floor)s
Date: %(date)s
Time: %(time)s

Thank you for using Just 4 IT Coworking!

---
Just 4 IT Coworking Reservation System
    """) % {
        'desk': desk_label,
        'floor': floor_info,
        'date': date_str,
        'time': time_str
    }
    
    return send_notification_email(
        reservation.email,
        subject,
        message,
        'CONFIRMATION'
    )

def send_cancellation_notification(reservation):
    """Wyślij powiadomienie o anulowaniu"""
    from django.utils.translation import gettext as _
    
    desk_label = reservation.desk.label if hasattr(reservation, 'desk') else reservation.seat_id
    floor_info = f" (Floor {reservation.desk.floor.number})" if hasattr(reservation, 'desk') and hasattr(reservation.desk, 'floor') else ""
    
    subject = _("Reservation Cancelled: %(desk)s") % {'desk': desk_label}
    
    if hasattr(reservation, 'date') and hasattr(reservation, 'time_from'):
        date_str = reservation.date.strftime('%Y-%m-%d') if hasattr(reservation.date, 'strftime') else str(reservation.date)
        time_str = f"{reservation.time_from} - {reservation.time_to}" if hasattr(reservation, 'time_to') else str(reservation.time_from)
    else:
        date_str = reservation.date
        time_str = "All day"
    
    message = _("""
Reservation Cancelled

Your reservation has been cancelled.

Desk: %(desk)s%(floor)s
Date: %(date)s
Time: %(time)s

The desk is now available for others.

---
Just 4 IT Coworking Reservation System
    """) % {
        'desk': desk_label,
        'floor': floor_info,
        'date': date_str,
        'time': time_str
    }
    
    return send_notification_email(
        reservation.email, 
        subject, 
        message, 
        'CANCELLATION'
    )

def check_and_send_reminders():
    """Sprawdź i wyślij przypomnienia o rezerwacjach zgodnie z ustawieniami użytkownika"""
    now = timezone.now()
    today = now.date()
    today_str = today.strftime('%Y-%m-%d')
    
    # Znajdź wszystkie aktywne rezerwacje na dziś z obu modeli
    reservations_list = []
    
    # Model z reservations/models.py
    try:
        from reservations.models import Reservation as ReservationsReservation
        reservations_list.extend(
            ReservationsReservation.objects.filter(
                date=today,
                is_cancelled=False
            )
        )
    except:
        pass
    
    # Model z api/models.py
    try:
        from api.models import Reservation as ApiReservation
        reservations_list.extend(
            ApiReservation.objects.filter(
                date=today_str
            )
        )
    except:
        pass
    
    sent_count = 0
    
    for reservation in reservations_list:
        try:
            # Pobierz preferencje użytkownika
            prefs = UserPreferences.objects.get(email=reservation.email)
            reminder_minutes = prefs.reminder_before_booking
            # Sprawdź czy użytkownik włączył powiadomienia email
            if not prefs.email_notifications:
                continue
        except UserPreferences.DoesNotExist:
            # Domyślne przypomnienie 30 minut przed
            reminder_minutes = 30
        
        # Oblicz czas rozpoczęcia rezerwacji
        if hasattr(reservation, 'time_from') and reservation.time_from:
            # Dla modelu z reservations/models.py
            if isinstance(reservation.date, str):
                reservation_date = datetime.strptime(reservation.date, '%Y-%m-%d').date()
            else:
                reservation_date = reservation.date
            reservation_datetime = datetime.combine(reservation_date, reservation.time_from)
            reservation_time = timezone.make_aware(reservation_datetime)
        else:
            # Dla modelu z api/models.py - przypomnienie o 9:00 (domyślnie)
            if isinstance(reservation.date, str):
                reservation_date = datetime.strptime(reservation.date, '%Y-%m-%d').date()
            else:
                reservation_date = reservation.date
            reservation_datetime = datetime.combine(reservation_date, datetime.min.time().replace(hour=9))
            reservation_time = timezone.make_aware(reservation_datetime)
        
        # Sprawdź czy czas na przypomnienie
        time_diff = (reservation_time - now).total_seconds() / 60
        
        # Wyślij przypomnienie jeśli jest w przedziale 0-5 minut przed czasem przypomnienia
        if reminder_minutes - 5 <= time_diff <= reminder_minutes + 5:
            if send_reservation_reminder(reservation, reminder_minutes):
                sent_count += 1
    
    return sent_count

def send_daily_summaries():
    """Wyślij dzienne podsumowania"""
    tomorrow = timezone.now().date() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    
    # Znajdź wszystkich użytkowników z rezerwacjami na jutro z obu modeli
    reservations_list = []
    
    # Model z reservations/models.py
    try:
        from reservations.models import Reservation as ReservationsReservation
        reservations_list.extend(
            ReservationsReservation.objects.filter(
                date=tomorrow,
                is_cancelled=False
            ).order_by('email', 'time_from')
        )
    except:
        pass
    
    # Model z api/models.py
    try:
        from api.models import Reservation as ApiReservation
        reservations_list.extend(
            ApiReservation.objects.filter(
                date=tomorrow_str
            ).order_by('email')
        )
    except:
        pass
    
    # Grupuj po emailu
    user_reservations = {}
    for res in reservations_list:
        email = getattr(res, 'email', None)
        if email:
            if email not in user_reservations:
                user_reservations[email] = []
            user_reservations[email].append(res)
    
    sent_count = 0
    for email, user_res in user_reservations.items():
        try:
            prefs = UserPreferences.objects.get(email=email)
            if prefs.daily_summary:
                if send_daily_summary(email, user_res):
                    sent_count += 1
        except UserPreferences.DoesNotExist:
            # Domyślnie wyślij jeśli użytkownik nie ma preferencji
            if send_daily_summary(email, user_res):
                sent_count += 1
    
    return sent_count

def send_weekly_reports():
    """Wyślij tygodniowe raporty"""
    from django.utils.translation import gettext as _
    
    # Znajdź użytkowników z włączonymi raportami tygodniowymi
    users_with_reports = UserPreferences.objects.filter(weekly_report=True)
    
    sent_count = 0
    week_ago = timezone.now().date() - timedelta(days=7)
    week_ago_str = week_ago.strftime('%Y-%m-%d')
    
    for prefs in users_with_reports:
        # Zbierz rezerwacje z obu modeli
        reservations_list = []
        
        # Model z reservations/models.py
        try:
            from reservations.models import Reservation as ReservationsReservation
            reservations_list.extend(
                ReservationsReservation.objects.filter(
                    email=prefs.email,
                    date__gte=week_ago,
                    is_cancelled=False
                )
            )
        except:
            pass
        
        # Model z api/models.py
        try:
            from api.models import Reservation as ApiReservation
            reservations_list.extend(
                ApiReservation.objects.filter(
                    email=prefs.email,
                    date__gte=week_ago_str
                )
            )
        except:
            pass
        
        if reservations_list:
            # Oblicz statystyki
            total = len(reservations_list)
            
            # Znajdź ulubione stanowisko
            desk_counts = {}
            for res in reservations_list:
                desk_label = res.desk.label if hasattr(res, 'desk') else res.seat_id
                desk_counts[desk_label] = desk_counts.get(desk_label, 0) + 1
            
            favorite_desk = max(desk_counts.items(), key=lambda x: x[1])[0] if desk_counts else _('None')
            
            # Znajdź ulubione piętro
            floor_counts = {}
            for res in reservations_list:
                if hasattr(res, 'desk') and hasattr(res.desk, 'floor'):
                    floor_num = res.desk.floor.number
                    floor_counts[floor_num] = floor_counts.get(floor_num, 0) + 1
            favorite_floor = max(floor_counts.items(), key=lambda x: x[1])[0] if floor_counts else _('None')
            
            stats = {
                'total_reservations': total,
                'favorite_desk': favorite_desk,
                'favorite_floor': favorite_floor,
                'avg_duration': 'N/A'  # Można dodać obliczenia
            }
            
            if send_weekly_report(prefs.email, stats):
                sent_count += 1
    
    return sent_count
