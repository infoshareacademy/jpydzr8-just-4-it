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
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)

def send_templated_email(template_prefix, context, to_email, fallback_subject, notification_type='CONFIRMATION'):
    """
    Wyślij email na podstawie szablonów:
      templates/emails/{template_prefix}_subject.txt
      templates/emails/{template_prefix}_body.txt
      templates/emails/{template_prefix}_body.html
    """
    try:
        # Renderuj tematy i treści
        try:
            subject = render_to_string(f'emails/{template_prefix}_subject.txt', context).strip()
            if not subject:
                subject = fallback_subject
        except Exception:
            subject = fallback_subject
        try:
            body_txt = render_to_string(f'emails/{template_prefix}_body.txt', context)
        except Exception:
            body_txt = context.get('message', '') or fallback_subject
        try:
            body_html = render_to_string(f'emails/{template_prefix}_body.html', context)
        except Exception:
            body_html = None
        
        # Wyślij EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject=subject,
            body=body_txt,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        if body_html:
            email.attach_alternative(body_html, "text/html")
        email.send(fail_silently=False)
        
        # Zapisz w Notification (jeśli model istnieje)
        try:
            Notification.objects.create(
                email=to_email,
                type=notification_type,
                title=subject,
                message=body_txt,
                is_sent=True,
                sent_at=timezone.now()
            )
        except Exception:
            pass
        
        # Web Push, jeśli skonfigurowane
        if is_webpush_enabled():
            send_push_notification(
                to_email,
                subject,
                body_txt,
                data={'notification_type': notification_type, 'generated_at': timezone.now().isoformat()},
                tag=notification_type.lower(),
            )
        return True
    except Exception as e:
        logger.exception("Błąd wysyłania templated email: {0}".format(e))
        return False

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
    
    desk_label = getattr(getattr(reservation, 'desk', None), 'label', None) or getattr(reservation, 'seat_id', '')
    floor_number = getattr(getattr(getattr(reservation, 'desk', None), 'floor', None), 'number', None)
    date_str = reservation.date.strftime('%Y-%m-%d') if hasattr(reservation, 'date') and hasattr(reservation.date, 'strftime') else str(getattr(reservation, 'date', ''))
    time_from = getattr(reservation, 'time_from', None)
    time_to = getattr(reservation, 'time_to', None)
    fallback_subject = _("Przypomnienie: %(desk)s za %(minutes)d min") % {'desk': desk_label, 'minutes': minutes_before}
    context = {
        'desk_label': desk_label,
        'floor_number': floor_number,
        'date_str': date_str,
        'time_from': time_from,
        'time_to': time_to,
        'minutes_before': minutes_before,
        'system_name': 'Just 4 IT Coworking',
    }
    return send_templated_email('reservation_reminder', context, reservation.email, fallback_subject, 'REMINDER')

def send_waitlist_notification(waitlist_entry):
    """Wyślij powiadomienie z waitlist"""
    from django.utils.translation import gettext as _
    
    desk_label = getattr(waitlist_entry.desk, 'label', '')
    floor_number = getattr(getattr(waitlist_entry.desk, 'floor', None), 'number', None)
    date_str = waitlist_entry.preferred_date.strftime('%Y-%m-%d') if hasattr(waitlist_entry, 'preferred_date') and hasattr(waitlist_entry.preferred_date, 'strftime') else str(waitlist_entry.preferred_date)
    time_from = getattr(waitlist_entry, 'time_from', None)
    time_to = getattr(waitlist_entry, 'time_to', None)
    fallback_subject = f"Stanowisko {desk_label} jest dostępne!"
    context = {
        'desk_label': desk_label,
        'floor_number': floor_number,
        'date_str': date_str,
        'time_from': time_from,
        'time_to': time_to,
    }
    return send_templated_email('waitlist_notification', context, waitlist_entry.email, fallback_subject, 'WAITLIST')

def send_daily_summary(email, reservations):
    """Wyślij dzienne podsumowanie"""
    from django.utils.translation import gettext as _
    
    if not reservations:
        return False
    
    first_res = reservations[0]
    date_str = first_res.date.strftime('%Y-%m-%d') if hasattr(first_res, 'date') and hasattr(first_res.date, 'strftime') else str(getattr(first_res, 'date', ''))
    items = []
    for res in reservations:
        desk_label = getattr(getattr(res, 'desk', None), 'label', None) or getattr(res, 'seat_id', '')
        floor_number = getattr(getattr(getattr(res, 'desk', None), 'floor', None), 'number', None)
        time_from = getattr(res, 'time_from', None)
        time_to = getattr(res, 'time_to', None)
        items.append({
            'desk_label': desk_label,
            'floor_number': floor_number,
            'time_from': time_from,
            'time_to': time_to
        })
    fallback_subject = _("Podsumowanie rezerwacji na %(date)s") % {'date': date_str}
    context = {
        'date_str': date_str,
        'count': len(reservations),
        'items': items,
        'system_name': 'Just 4 IT Coworking',
    }
    return send_templated_email('daily_summary', context, email, fallback_subject, 'DAILY_SUMMARY')

def send_weekly_report(email, stats):
    """Wyślij tygodniowy raport"""
    from django.utils.translation import gettext as _
    
    fallback_subject = _("Tygodniowy raport rezerwacji")
    context = {
        'total': stats.get('total_reservations', 0),
        'favorite_desk': stats.get('favorite_desk', _("None")),
        'favorite_floor': stats.get('favorite_floor', _("None")),
        'avg_duration': stats.get('avg_duration', 'N/A'),
        'system_name': 'Just 4 IT Coworking',
    }
    return send_templated_email('weekly_report', context, email, fallback_subject, 'WEEKLY_REPORT')

def send_reservation_confirmation(reservation):
    """Wyślij email potwierdzający utworzenie rezerwacji"""
    from django.utils.translation import gettext as _
    
    # Kontekst do szablonu
    has_times = hasattr(reservation, 'time_from') and getattr(reservation, 'time_from', None)
    date_str = reservation.date.strftime('%Y-%m-%d') if hasattr(reservation, 'date') and hasattr(reservation.date, 'strftime') else str(getattr(reservation, 'date', ''))
    time_from = getattr(reservation, 'time_from', None)
    time_to = getattr(reservation, 'time_to', None)
    floor_num = getattr(getattr(getattr(reservation, 'desk', None), 'floor', None), 'number', None)
    desk_label = getattr(getattr(reservation, 'desk', None), 'label', None) or getattr(reservation, 'seat_id', '')
    fallback_subject = _("Potwierdzenie rezerwacji: %(desk)s") % {'desk': desk_label}
    context = {
        'desk_label': desk_label,
        'floor_number': floor_num,
        'date_str': date_str,
        'time_from': time_from,
        'time_to': time_to,
        'has_times': bool(has_times),
        'user_name': getattr(reservation, 'name', ''),
        'system_name': 'Just 4 IT Coworking',
    }
    return send_templated_email('reservation_confirmation', context, reservation.email, fallback_subject, 'CONFIRMATION')

def send_cancellation_notification(reservation):
    """Wyślij powiadomienie o anulowaniu"""
    from django.utils.translation import gettext as _
    
    desk_label = getattr(getattr(reservation, 'desk', None), 'label', None) or getattr(reservation, 'seat_id', '')
    floor_num = getattr(getattr(getattr(reservation, 'desk', None), 'floor', None), 'number', None)
    date_str = reservation.date.strftime('%Y-%m-%d') if hasattr(reservation, 'date') and hasattr(reservation.date, 'strftime') else str(getattr(reservation, 'date', ''))
    time_from = getattr(reservation, 'time_from', None)
    time_to = getattr(reservation, 'time_to', None)
    fallback_subject = _("Anulowano rezerwację: %(desk)s") % {'desk': desk_label}
    context = {
        'desk_label': desk_label,
        'floor_number': floor_num,
        'date_str': date_str,
        'time_from': time_from,
        'time_to': time_to,
        'system_name': 'Just 4 IT Coworking',
    }
    return send_templated_email('cancellation_notification', context, reservation.email, fallback_subject, 'CANCELLATION')

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

def send_group_reservation_confirmation(group_reservation):
    """Wyślij email z potwierdzeniem rezerwacji grupowej do organizatora"""
    from django.utils.translation import gettext as _
    
    try:
        desks = list(group_reservation.desks.select_related('floor').all())
        date_str = group_reservation.date.strftime('%Y-%m-%d') if hasattr(group_reservation, 'date') and hasattr(group_reservation.date, 'strftime') else str(group_reservation.date)
        fallback_subject = _("Potwierdzenie rezerwacji grupowej: %(group)s") % {'group': group_reservation.group_name}
        context = {
            'group_name': group_reservation.group_name,
            'organizer_email': group_reservation.organizer_email,
            'date_str': date_str,
            'time_from': getattr(group_reservation, 'time_from', None),
            'time_to': getattr(group_reservation, 'time_to', None),
            'purpose': getattr(group_reservation, 'purpose', ''),
            'desks': desks,
        }
        return send_templated_email('group_reservation_confirmation', context, group_reservation.organizer_email, fallback_subject, 'CONFIRMATION')
    except Exception as e:
        logger.exception("Błąd wysyłania potwierdzenia rezerwacji grupowej: {0}".format(e))
        return False

def send_recurring_setup_confirmation(recurring_reservation, first_created_reservation=None):
    """Wyślij email z potwierdzeniem skonfigurowania rezerwacji cyklicznej"""
    from django.utils.translation import gettext as _
    
    try:
        # Dane do kontekstu
        start_date_str = recurring_reservation.start_date.strftime('%Y-%m-%d') if hasattr(recurring_reservation, 'start_date') and hasattr(recurring_reservation.start_date, 'strftime') else str(recurring_reservation.start_date)
        end_date_str = recurring_reservation.end_date.strftime('%Y-%m-%d') if getattr(recurring_reservation, 'end_date', None) and hasattr(recurring_reservation.end_date, 'strftime') else _("brak (bez końca)")
        time_from_str = recurring_reservation.time_from.strftime('%H:%M') if hasattr(recurring_reservation, 'time_from') and hasattr(recurring_reservation.time_from, 'strftime') else str(recurring_reservation.time_from)
        time_to_str = recurring_reservation.time_to.strftime('%H:%M') if hasattr(recurring_reservation, 'time_to') and hasattr(recurring_reservation.time_to, 'strftime') else str(recurring_reservation.time_to)
        days_map = ['Pon', 'Wt', 'Śr', 'Czw', 'Pt', 'Sob', 'Nd']
        try:
            flags = list(recurring_reservation.days_of_week)
            days_enabled = [days_map[i] for i, f in enumerate(flags) if f == '1']
            days_str = ', '.join(days_enabled) if days_enabled else _("brak")
        except Exception:
            days_str = str(recurring_reservation.days_of_week)
        first_date = None
        first_from = None
        first_to = None
        if first_created_reservation:
            first_date = first_created_reservation.date
            first_from = getattr(first_created_reservation, 'time_from', None)
            first_to = getattr(first_created_reservation, 'time_to', None)
        fallback_subject = _("Cykliczna rezerwacja: %(desk)s") % {'desk': recurring_reservation.desk.label}
        context = {
            'desk_label': recurring_reservation.desk.label,
            'floor_number': getattr(recurring_reservation.desk.floor, 'number', 'N/A'),
            'start_date': start_date_str,
            'end_date': end_date_str,
            'time_from': time_from_str,
            'time_to': time_to_str,
            'frequency': recurring_reservation.frequency,
            'days_str': days_str,
            'first_date': first_date,
            'first_from': first_from,
            'first_to': first_to,
        }
        return send_templated_email('recurring_setup_confirmation', context, recurring_reservation.email, fallback_subject, 'CONFIRMATION')
    except Exception as e:
        logger.exception("Błąd wysyłania potwierdzenia cyklicznej rezerwacji: {0}".format(e))
        return False

def send_conference_reservation_confirmation(conference_reservation):
    """Wyślij email z potwierdzeniem rezerwacji sali konferencyjnej"""
    from django.utils.translation import gettext as _
    
    try:
        room = conference_reservation.conference_room
        date_str = conference_reservation.date.strftime('%Y-%m-%d') if hasattr(conference_reservation, 'date') and hasattr(conference_reservation.date, 'strftime') else str(conference_reservation.date)
        time_from_str = conference_reservation.time_from.strftime('%H:%M') if hasattr(conference_reservation, 'time_from') and hasattr(conference_reservation.time_from, 'strftime') else str(conference_reservation.time_from)
        time_to_str = conference_reservation.time_to.strftime('%H:%M') if hasattr(conference_reservation, 'time_to') and hasattr(conference_reservation.time_to, 'strftime') else str(conference_reservation.time_to)
        fallback_subject = _("Rezerwacja sali: %(room)s") % {'room': room.name}
        context = {
            'room_name': room.name,
            'floor_number': getattr(room.floor, 'number', 'N/A'),
            'team_name': getattr(conference_reservation, 'team_name', ''),
            'contact_email': getattr(conference_reservation, 'contact_email', ''),
            'date_str': date_str,
            'time_from': time_from_str,
            'time_to': time_to_str,
            'attendees_count': getattr(conference_reservation, 'attendees_count', 1),
            'purpose': getattr(conference_reservation, 'purpose', ''),
        }
        return send_templated_email('conference_reservation_confirmation', context, conference_reservation.contact_email, fallback_subject, 'CONFIRMATION')
    except Exception as e:
        logger.exception("Błąd wysyłania potwierdzenia rezerwacji sali konferencyjnej: {0}".format(e))
        return False

def send_recurring_cancellation(recurring_reservation, end_date=None):
    """Wyślij email o anulowaniu rezerwacji cyklicznej (natychmiast lub od wskazanej daty)"""
    from django.utils.translation import gettext as _
    try:
        start_date_str = recurring_reservation.start_date.strftime('%Y-%m-%d') if hasattr(recurring_reservation, 'start_date') and hasattr(recurring_reservation.start_date, 'strftime') else str(recurring_reservation.start_date)
        was_end = getattr(recurring_reservation, 'end_date', None)
        end_date_effective = end_date or was_end
        end_date_str = end_date_effective.strftime('%Y-%m-%d') if end_date_effective and hasattr(end_date_effective, 'strftime') else (_("bez końca") if not end_date_effective else str(end_date_effective))
        time_from_str = recurring_reservation.time_from.strftime('%H:%M') if hasattr(recurring_reservation, 'time_from') and hasattr(recurring_reservation.time_from, 'strftime') else str(recurring_reservation.time_from)
        time_to_str = recurring_reservation.time_to.strftime('%H:%M') if hasattr(recurring_reservation, 'time_to') and hasattr(recurring_reservation.time_to, 'strftime') else str(recurring_reservation.time_to)
        fallback_subject = _("Anulowano cykliczną rezerwację: %(desk)s") % {'desk': recurring_reservation.desk.label}
        context = {
            'desk_label': recurring_reservation.desk.label,
            'floor_number': getattr(recurring_reservation.desk.floor, 'number', 'N/A'),
            'start_date': start_date_str,
            'end_date': end_date_str,
            'time_from': time_from_str,
            'time_to': time_to_str,
            'frequency': recurring_reservation.frequency,
            'cancel_from': end_date.strftime('%Y-%m-%d') if end_date and hasattr(end_date, 'strftime') else None,
        }
        return send_templated_email('recurring_cancellation', context, recurring_reservation.email, fallback_subject, 'CANCELLATION')
    except Exception as e:
        logger.exception("Błąd wysyłania powiadomienia anulowania cyklicznej rezerwacji: {0}".format(e))
        return False
