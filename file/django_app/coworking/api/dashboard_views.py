from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from datetime import datetime, timedelta
import json

from api.models import Reservation as ApiReservation
from reservations.models import Reservation, GroupReservation, RecurringReservation
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def dashboard(request):
    """Main dashboard view"""
    user = request.user
    context = {
        'user_name': user.full_name or user.email.split('@')[0],
        'user_email': user.email,
        'user_avatar': getattr(user, 'avatar', '👤') or '👤'
    }
    return render(request, 'dashboard/dashboard.html', context)


@require_http_methods(["GET"])
@login_required
def api_reservations_calendar(request):
    """API endpoint for calendar events"""
    try:
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)
        
        user_email = request.user.email if hasattr(request.user, 'email') else None
        reservations = Reservation.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            email=user_email,
            is_cancelled=False
        ).select_related('desk').order_by('date', 'time_from')
        
        api_reservations = ApiReservation.objects.filter(
            date__gte=start_date.strftime('%Y-%m-%d'),
            date__lte=end_date.strftime('%Y-%m-%d'),
            email=user_email
        ).order_by('date')
        
        events = []
        
        for reservation in reservations:
            events.append({
                'id': f"res_{reservation.id}",
                'title': _('Seat %(seat_id)s') % {'seat_id': reservation.desk.label},
                'start': reservation.date.isoformat(),
                'backgroundColor': '#3b82f6',
                'borderColor': '#2563eb',
                'extendedProps': {
                    'seat_id': reservation.desk.label,
                    'name': reservation.name,
                    'email': reservation.email,
                    'time_from': reservation.time_from.strftime('%H:%M') if reservation.time_from else None,
                    'time_to': reservation.time_to.strftime('%H:%M') if reservation.time_to else None,
                    'floor': reservation.desk.floor.number if reservation.desk and reservation.desk.floor else None
                }
            })
        
        for reservation in api_reservations:
            events.append({
                'id': f"api_{reservation.id}",
                'title': _('Seat %(seat_id)s') % {'seat_id': reservation.seat_id},
                'start': reservation.date,
                'backgroundColor': '#3b82f6',
                'borderColor': '#2563eb',
                'extendedProps': {
                    'seat_id': reservation.seat_id,
                    'name': reservation.name,
                    'email': reservation.email
                }
            })
        
        group_reservations = GroupReservation.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            organizer_email=user_email,
            is_cancelled=False
        ).prefetch_related('desks').order_by('date', 'time_from')
        
        for group_res in group_reservations:
            for desk in group_res.desks.all():
                events.append({
                    'id': f"group_{group_res.id}_{desk.id}",
                    'title': f'👥 {_("Group")}: {group_res.group_name} - {desk.label}',
                    'start': group_res.date.isoformat(),
                    'backgroundColor': '#8b5cf6',
                    'borderColor': '#7c3aed',
                    'extendedProps': {
                        'type': 'group',
                        'group_name': group_res.group_name,
                        'seat_id': desk.label,
                        'name': group_res.group_name,
                        'email': group_res.organizer_email,
                        'time_from': group_res.time_from.strftime('%H:%M') if group_res.time_from else None,
                        'time_to': group_res.time_to.strftime('%H:%M') if group_res.time_to else None,
                        'floor': desk.floor.number if desk and desk.floor else None,
                        'purpose': group_res.purpose,
                        'desks_count': group_res.desks.count()
                    }
                })
        
        recurring_reservations = RecurringReservation.objects.filter(
            start_date__lte=end_date,
            email=user_email,
            is_active=True
        ).select_related('desk').order_by('start_date')
        
        from reservations.recurring_utils import get_recurring_dates
        
        for recurring in recurring_reservations:
            if recurring.end_date and recurring.end_date < start_date:
                continue
            
            pattern_start = max(recurring.start_date, start_date) if recurring.start_date < start_date else recurring.start_date
            pattern_end = min(recurring.end_date, end_date) if recurring.end_date else end_date
            
            recurring_dates = get_recurring_dates(
                pattern_start,
                pattern_end,
                recurring.frequency,
                recurring.days_of_week
            )
            
            # Dodaj wydarzenie dla każdej daty z wzorca
            for rec_date in recurring_dates:
                # Sprawdź czy nie pokrywa się już z normalną rezerwacją
                existing = False
                for event in events:
                    if (event.get('start') == rec_date.isoformat() and 
                        event.get('extendedProps', {}).get('seat_id') == recurring.desk.label):
                        # Oznacz istniejące wydarzenie jako cykliczne
                        if 'type' not in event.get('extendedProps', {}):
                            event['title'] = f'🔄 {_("Recurring")}: {event["title"]}'
                            event['extendedProps']['type'] = 'recurring'
                            event['extendedProps']['recurring_id'] = recurring.id
                            event['backgroundColor'] = '#10b981'  # Green for recurring
                            event['borderColor'] = '#059669'
                        existing = True
                        break
                
                if not existing:
                    # Dodaj nowe wydarzenie dla wzorca cyklicznego
                    frequency_label = dict(RecurringReservation.FREQUENCY_CHOICES).get(recurring.frequency, recurring.frequency)
                    events.append({
                        'id': f"recurring_{recurring.id}_{rec_date.isoformat()}",
                        'title': f'🔄 {_("Recurring")}: {recurring.desk.label} ({frequency_label})',
                        'start': rec_date.isoformat(),
                        'backgroundColor': '#10b981',  # Green color for recurring reservations
                        'borderColor': '#059669',
                        'extendedProps': {
                            'type': 'recurring',
                            'recurring_id': recurring.id,
                            'seat_id': recurring.desk.label,
                            'name': recurring.name,
                            'email': recurring.email,
                            'time_from': recurring.time_from.strftime('%H:%M') if recurring.time_from else None,
                            'time_to': recurring.time_to.strftime('%H:%M') if recurring.time_to else None,
                            'floor': recurring.desk.floor.number if recurring.desk and recurring.desk.floor else None,
                            'frequency': recurring.frequency,
                            'frequency_label': frequency_label,
                            'days_of_week': recurring.days_of_week
                        }
                    })
        
        return JsonResponse(events, safe=False)
    
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@require_http_methods(["GET"])
@login_required
def api_reservations_summary(request):
    """API endpoint for dashboard summary"""
    try:
        today = timezone.now().date()
        
        # Get user's email
        user_email = request.user.email if hasattr(request.user, 'email') else None
        
        if not user_email:
            return JsonResponse({'error': 'User email not found'}, status=400)
        
        # Get reservations from new model (reservations.models.Reservation)
        reservations_qs = Reservation.objects.filter(
            email=user_email,
            is_cancelled=False
        ).select_related('desk', 'desk__floor')
        
        # Also get from old model (api.models.Reservation) for compatibility
        api_reservations_qs = ApiReservation.objects.filter(
            email=user_email
        )
        
        # Initialize variables
        next_reservation_text = None
        next_reservation_id = None
        next_reservation_seat = None
        next_reservation_time = None
        next_reservation_datetime = None
        
        # Next reservation (new model)
        next_reservation = reservations_qs.filter(
            date__gte=today
        ).order_by('date', 'time_from').first()
        
        # Next reservation (old model) - fallback
        if not next_reservation:
            api_next = api_reservations_qs.filter(
                date__gte=today.strftime('%Y-%m-%d')
            ).order_by('date').first()
            if api_next:
                next_reservation_text = api_next.date
                next_reservation_id = f"api_{api_next.id}"
                next_reservation_seat = api_next.seat_id if hasattr(api_next, 'seat_id') else None
                next_reservation_time = None
                next_reservation_datetime = f"{next_reservation_text}T09:00:00"  # Default 9 AM for old model
        else:
            next_reservation_text = next_reservation.date.strftime('%Y-%m-%d')
            next_reservation_id = f"res_{next_reservation.id}"
            next_reservation_seat = next_reservation.desk.label if next_reservation.desk else None
            # Get time_from for accurate reminders
            if next_reservation.time_from:
                next_reservation_time = next_reservation.time_from.strftime('%H:%M')
                # Combine date and time for accurate reminder calculation
                next_reservation_datetime = f"{next_reservation_text}T{next_reservation_time}:00"
            else:
                next_reservation_time = None
                next_reservation_datetime = f"{next_reservation_text}T09:00:00"  # Default 9 AM
        
        # Last reservation (new model)
        last_reservation = reservations_qs.filter(
            date__lt=today
        ).order_by('-date', '-time_from').first()
        
        # Last reservation (old model) - fallback
        if not last_reservation:
            api_last = api_reservations_qs.filter(
                date__lt=today.strftime('%Y-%m-%d')
            ).order_by('-date').first()
            if api_last:
                last_reservation_text = api_last.date
            else:
                last_reservation_text = None
        else:
            last_reservation_text = last_reservation.date.strftime('%Y-%m-%d')
        
        # Upcoming count (next 30 days) - combine both models
        end_date = today + timedelta(days=30)
        upcoming_reservations = reservations_qs.filter(
            date__gte=today,
            date__lte=end_date
        ).values_list('date', flat=True).distinct()
        
        # Get unique dates from old model
        api_upcoming_dates = api_reservations_qs.filter(
            date__gte=today.strftime('%Y-%m-%d'),
            date__lte=end_date.strftime('%Y-%m-%d')
        ).values_list('date', flat=True).distinct()
        
        # Convert old model dates to date objects
        from datetime import datetime as dt
        api_upcoming_dates_converted = []
        for date_str in api_upcoming_dates:
            try:
                if isinstance(date_str, str):
                    api_upcoming_dates_converted.append(dt.strptime(date_str, '%Y-%m-%d').date())
                else:
                    api_upcoming_dates_converted.append(date_str)
            except:
                pass
        
        # Combine unique dates
        unique_dates = set(list(upcoming_reservations) + api_upcoming_dates_converted)
        upcoming_count = len(unique_dates)  # Liczba dni z rezerwacjami
        
        # Total reservations - combine both models
        total_reservations = reservations_qs.count() + api_reservations_qs.count()
        
        # Get favorite seats (most used) - combine both models
        from django.db.models import Count
        favorite_seats_new = reservations_qs.values('desk__label').annotate(
            count=Count('id')
        ).order_by('-count')[:3]
        favorite_seats_old = api_reservations_qs.values('seat_id').annotate(
            count=Count('id')
        ).order_by('-count')[:3]
        favorite_desks_count = len(favorite_seats_new) + len(favorite_seats_old)
        
        # Calculate efficiency - procent dni z rezerwacjami w nadchodzących 30 dniach
        # Wydajność = ile procent z najbliższych 30 dni ma już zaplanowane rezerwacje
        # Proste: 15 dni z rezerwacjami / 30 dni = 50% wydajności
        days_ahead = 30
        if upcoming_count > 0:
            efficiency = round((upcoming_count / days_ahead) * 100)
            efficiency = min(100, max(0, efficiency))  # Ograniczenie do 0-100%
        else:
            efficiency = 0
        
        # Calculate hero stats - combine both models
        today_count = reservations_qs.filter(date=today).count()
        today_count += api_reservations_qs.filter(date=today.strftime('%Y-%m-%d')).count()
        
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        week_count = reservations_qs.filter(
            date__gte=week_start,
            date__lte=week_end
        ).count()
        week_count += api_reservations_qs.filter(
            date__gte=week_start.strftime('%Y-%m-%d'),
            date__lte=week_end.strftime('%Y-%m-%d')
        ).count()
        
        month_start = today.replace(day=1)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
        
        month_count = reservations_qs.filter(
            date__gte=month_start,
            date__lte=month_end
        ).count()
        month_count += api_reservations_qs.filter(
            date__gte=month_start.strftime('%Y-%m-%d'),
            date__lte=month_end.strftime('%Y-%m-%d')
        ).count()
        
        response_data = {
            'next_reservation': next_reservation_text,
            'next_reservation_text': next_reservation_text,  # Alias for compatibility
            'next_reservation_id': next_reservation_id,
            'next_reservation_seat': next_reservation_seat,
            'last_reservation': last_reservation_text,
            'upcoming_count': upcoming_count,
            'total_reservations': total_reservations,
            'favorite_desks': favorite_desks_count,
            'efficiency': f"{efficiency}%",
            'today_count': today_count,
            'week_count': week_count,
            'month_count': month_count
        }
        
        # Add datetime for accurate reminder calculation if available
        if next_reservation_datetime:
            response_data['next_reservation_datetime'] = next_reservation_datetime
        if next_reservation_time:
            response_data['next_reservation_time'] = next_reservation_time
            
        return JsonResponse(response_data)
    
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def api_quick_reserve(request):
    """API endpoint for quick reservation creation"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['date', 'desk', 'name', 'email']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': _('Missing required field: %(field)s') % {'field': field}}, status=400)
        
        # Validate date is not in the past
        from datetime import datetime
        today = timezone.now().date()
        try:
            reservation_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            if reservation_date < today:
                return JsonResponse({'error': _('Cannot reserve dates in the past')}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({'error': _('Invalid date format')}, status=400)
        
        # Validate time range
        time_from = data.get('time_from')
        time_to = data.get('time_to')
        if time_from and time_to:
            try:
                from datetime import time as time_obj
                time_from_obj = datetime.strptime(time_from, '%H:%M').time()
                time_to_obj = datetime.strptime(time_to, '%H:%M').time()
                if time_from_obj >= time_to_obj:
                    return JsonResponse({'error': _('Start time must be before end time')}, status=400)
            except (ValueError, TypeError):
                return JsonResponse({'error': _('Invalid time format')}, status=400)
        
        # Build notes from optional fields
        notes_parts = []
        if data.get('floor'):
            notes_parts.append(_('Floor: %(floor)s') % {'floor': data['floor']})
        if data.get('time_from'):
            notes_parts.append(_('From: %(time)s') % {'time': data['time_from']})
        if data.get('time_to'):
            notes_parts.append(_('To: %(time)s') % {'time': data['time_to']})
        notes = '; '.join(notes_parts) if notes_parts else ''
        
        # Create reservation
        seat_id = data.get('desk', data.get('seat_id', ''))
        reservation_id = f"{seat_id}_{data['date']}"
        
        # Check if reservation already exists in old model
        if ApiReservation.objects.filter(id=reservation_id).exists():
            return JsonResponse({'error': _('Reservation already exists for this seat and date')}, status=400)
        
        reservation = ApiReservation.objects.create(
            id=reservation_id,
            seat_id=seat_id,
            date=data['date'],
            name=data['name'],
            email=data['email'],
            notes=notes
        )
        
        # Wyślij email potwierdzający rezerwację
        try:
            from reservations.notification_utils import send_reservation_confirmation
            # Utwórz obiekt podobny do Reservation z reservations/models.py dla kompatybilności
            class ReservationWrapper:
                def __init__(self, res):
                    self.seat_id = res.seat_id
                    self.date = res.date
                    self.email = res.email
                    self.name = res.name
            send_reservation_confirmation(ReservationWrapper(reservation))
        except Exception as e:
            print(f"⚠️ Could not send reservation confirmation email: {e}")
        
        return JsonResponse({
            'success': True,
            'reservation_id': str(reservation.id),
            'message': _('Reservation created successfully')
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': _('Invalid JSON data')}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required
def api_notifications(request):
    """API endpoint for notifications"""
    try:
        # For now, return empty notifications
        # You can integrate with your notification system later
        return JsonResponse({
            'notifications': [],
            'unread_count': 0
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@login_required
def api_mark_notification_read(request, notification_id):
    """API endpoint to mark notification as read"""
    try:
        # For now, just return success
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

