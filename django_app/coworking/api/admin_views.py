from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.http import HttpResponse
from .models import Reservation
from .permissions import IsSuperUser
from datetime import datetime, timedelta
import csv
import json

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsSuperUser])
def admin_dashboard_stats(request):
    """Get comprehensive dashboard statistics for superuser"""
    
    # Basic counts
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    total_reservations = Reservation.objects.count()
    
    # Recent activity (last 30 days)
    last_30_days = datetime.now() - timedelta(days=30)
    new_users = User.objects.filter(created_at__gte=last_30_days).count()
    recent_reservations = Reservation.objects.filter(created_at__gte=last_30_days).count()
    
    # Today's activity
    today = datetime.now().strftime('%Y-%m-%d')
    today_reservations = Reservation.objects.filter(date=today).count()
    
    # Most popular seats
    popular_seats = Reservation.objects.values('seat_id')\
        .annotate(count=Count('seat_id'))\
        .order_by('-count')[:5]
    
    # Most active users
    active_users_data = Reservation.objects.values('email')\
        .annotate(count=Count('email'))\
        .order_by('-count')[:5]
    
    # Recent reservations
    recent_reservations_list = Reservation.objects.order_by('-created_at')[:10]
    
    return Response({
        'overview': {
            'total_users': total_users,
            'active_users': active_users,
            'staff_users': staff_users,
            'total_reservations': total_reservations,
            'new_users_30d': new_users,
            'recent_reservations_30d': recent_reservations,
            'today_reservations': today_reservations,
        },
        'popular_seats': list(popular_seats),
        'active_users': list(active_users_data),
        'recent_reservations': [
            {
                'id': res.id,
                'seat_id': res.seat_id,
                'date': res.date,
                'name': res.name,
                'email': res.email,
                'created_at': res.created_at
            } for res in recent_reservations_list
        ]
    })

@api_view(['POST'])
@permission_classes([IsSuperUser])
def bulk_user_operations(request):
    """Perform bulk operations on users"""
    action = request.data.get('action')
    user_ids = request.data.get('user_ids', [])
    
    if not action or not user_ids:
        return Response({'error': 'Action and user_ids required'}, status=400)
    
    users = User.objects.filter(id__in=user_ids)
    
    if action == 'activate':
        count = users.update(is_active=True)
        return Response({'message': f'{count} users activated'})
    
    elif action == 'deactivate':
        count = users.update(is_active=False)
        return Response({'message': f'{count} users deactivated'})
    
    elif action == 'make_staff':
        count = users.update(is_staff=True)
        return Response({'message': f'{count} users promoted to staff'})
    
    elif action == 'remove_staff':
        # Don't allow removing staff from superusers
        count = users.exclude(is_superuser=True).update(is_staff=False)
        return Response({'message': f'{count} users removed from staff'})
    
    else:
        return Response({'error': 'Invalid action'}, status=400)

@api_view(['POST'])
@permission_classes([IsSuperUser])
def bulk_reservation_operations(request):
    """Perform bulk operations on reservations"""
    action = request.data.get('action')
    reservation_ids = request.data.get('reservation_ids', [])
    
    if not action or not reservation_ids:
        return Response({'error': 'Action and reservation_ids required'}, status=400)
    
    reservations = Reservation.objects.filter(id__in=reservation_ids)
    
    if action == 'cancel':
        count = reservations.count()
        reservations.delete()
        return Response({'message': f'{count} reservations cancelled'})
    
    elif action == 'export':
        # Return reservation data for export
        data = [
            {
                'id': res.id,
                'seat_id': res.seat_id,
                'date': res.date,
                'name': res.name,
                'email': res.email,
                'notes': res.notes,
                'created_at': res.created_at.isoformat()
            } for res in reservations
        ]
        return Response({'data': data, 'count': len(data)})
    
    else:
        return Response({'error': 'Invalid action'}, status=400)

@api_view(['GET'])
@permission_classes([IsSuperUser])
def export_reservations_csv(request):
    """Export reservations to CSV"""
    # Get date range from query parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    queryset = Reservation.objects.all()
    
    if date_from:
        queryset = queryset.filter(date__gte=date_from)
    if date_to:
        queryset = queryset.filter(date__lte=date_to)
    
    queryset = queryset.order_by('date', 'seat_id')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reservations_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Seat ID', 'Date', 'Name', 'Email', 'Notes', 'Created At'])
    
    for reservation in queryset:
        writer.writerow([
            reservation.id,
            reservation.seat_id,
            reservation.date,
            reservation.name,
            reservation.email,
            reservation.notes,
            reservation.created_at
        ])
    
    return response

@api_view(['GET'])
@permission_classes([IsSuperUser])
def export_users_csv(request):
    """Export users to CSV"""
    queryset = User.objects.all().order_by('email')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="users_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Email', 'Full Name', 'Is Active', 'Is Staff', 'Is Superuser', 'Created At', 'Last Login'])
    
    for user in queryset:
        writer.writerow([
            user.email,
            user.full_name,
            user.is_active,
            user.is_staff,
            user.is_superuser,
            user.created_at,
            user.last_login
        ])
    
    return response

@api_view(['GET'])
@permission_classes([IsSuperUser])
def system_health_check(request):
    """Check system health and performance"""
    
    # Database connectivity
    try:
        User.objects.count()
        db_status = 'OK'
    except Exception as e:
        db_status = f'ERROR: {str(e)}'
    
    # Recent errors (if logging is set up)
    # This is a placeholder - in real implementation you'd check logs
    
    # Disk space (simplified check)
    import os
    try:
        statvfs = os.statvfs('.')
        free_space_gb = (statvfs.f_frsize * statvfs.f_bavail) / (1024**3)
        disk_status = f'{free_space_gb:.2f} GB free'
    except:
        disk_status = 'Unknown'
    
    # Active sessions (approximation)
    active_sessions = User.objects.filter(last_login__gte=datetime.now() - timedelta(hours=24)).count()
    
    return Response({
        'database': db_status,
        'disk_space': disk_status,
        'active_users_24h': active_sessions,
        'timestamp': datetime.now().isoformat(),
        'status': 'healthy' if db_status == 'OK' else 'warning'
    })
