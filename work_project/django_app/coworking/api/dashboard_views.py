from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from datetime import datetime, timedelta
import json

from api.models import Reservation
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
        # Get reservations for the next 30 days
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)
        
        # Get user's reservations
        reservations = Reservation.objects.filter(
            date__gte=start_date.strftime('%Y-%m-%d'),
            date__lte=end_date.strftime('%Y-%m-%d')
        ).order_by('date')
        
        events = []
        for reservation in reservations:
            events.append({
                'id': str(reservation.id),
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
        
        return JsonResponse(events, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required
def api_reservations_summary(request):
    """API endpoint for dashboard summary"""
    try:
        today = timezone.now().date()
        today_str = today.strftime('%Y-%m-%d')
        
        # Get user's email
        user_email = request.user.email if hasattr(request.user, 'email') else None
        
        # Next reservation
        next_reservation = Reservation.objects.filter(
            date__gte=today_str,
            email=user_email
        ).order_by('date').first()
        
        next_reservation_text = None
        next_reservation_id = None
        if next_reservation:
            next_reservation_text = f"{next_reservation.date}"
            next_reservation_id = str(next_reservation.id)
        
        # Last reservation
        last_reservation = Reservation.objects.filter(
            date__lt=today_str,
            email=user_email
        ).order_by('-date').first()
        
        last_reservation_text = None
        if last_reservation:
            last_reservation_text = f"{last_reservation.date}"
        
        # Upcoming count (next 30 days)
        end_date = (today + timedelta(days=30)).strftime('%Y-%m-%d')
        upcoming_count = Reservation.objects.filter(
            date__gte=today_str,
            date__lte=end_date,
            email=user_email
        ).count()
        
        # Calculate additional stats
        total_reservations = Reservation.objects.filter(
            email=user_email
        ).count()
        
        # Get favorite seats (most used)
        from django.db.models import Count
        favorite_seats = Reservation.objects.filter(
            email=user_email
        ).values('seat_id').annotate(count=Count('id')).order_by('-count')[:3]
        
        # Calculate efficiency (simplified)
        efficiency = min(95, max(60, 95 - (upcoming_count * 2)))
        
        # Calculate hero stats
        today_count = Reservation.objects.filter(
            date=today_str,
            email=user_email
        ).count()
        
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        week_count = Reservation.objects.filter(
            date__gte=week_start.strftime('%Y-%m-%d'),
            date__lte=week_end.strftime('%Y-%m-%d'),
            email=user_email
        ).count()
        
        month_start = today.replace(day=1)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
        
        month_count = Reservation.objects.filter(
            date__gte=month_start.strftime('%Y-%m-%d'),
            date__lte=month_end.strftime('%Y-%m-%d'),
            email=user_email
        ).count()
        
        return JsonResponse({
            'next_reservation': next_reservation_text,
            'next_reservation_id': next_reservation_id,
            'last_reservation': last_reservation_text,
            'upcoming_count': upcoming_count,
            'total_reservations': total_reservations,
            'favorite_desks': len(favorite_seats),
            'efficiency': f"{efficiency}%",
            'today_count': today_count,
            'week_count': week_count,
            'month_count': month_count
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


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
        
        # Check if reservation already exists
        if Reservation.objects.filter(id=reservation_id).exists():
            return JsonResponse({'error': _('Reservation already exists for this seat and date')}, status=400)
        
        reservation = Reservation.objects.create(
            id=reservation_id,
            seat_id=seat_id,
            date=data['date'],
            name=data['name'],
            email=data['email'],
            notes=notes
        )
        
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

