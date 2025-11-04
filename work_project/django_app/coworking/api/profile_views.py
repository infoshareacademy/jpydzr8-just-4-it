from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.utils.translation import gettext as _
from datetime import timedelta
from django.utils import timezone
import json

from api.models import Reservation

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get user profile information"""
    try:
        user = request.user
        
        # Get user statistics
        total_reservations = Reservation.objects.filter(email=user.email).count()
        today = timezone.now().date().strftime('%Y-%m-%d')
        today_reservations = Reservation.objects.filter(email=user.email, date=today).count()
        
        # Get favorite seats
        favorite_seats = Reservation.objects.filter(email=user.email).values('seat_id').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Get account age
        account_age_days = (timezone.now().date() - user.created_at.date()).days if user.created_at else 0
        
        return Response({
            'email': user.email,
            'full_name': user.full_name or '',
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'avatar': getattr(user, 'avatar', '👤') or '👤',
            'statistics': {
                'total_reservations': total_reservations,
                'today_reservations': today_reservations,
                'favorite_seats': list(favorite_seats),
                'account_age_days': account_age_days
            }
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """Update user profile information"""
    try:
        user = request.user
        data = request.data
        
        # Update full name
        if 'full_name' in data:
            user.full_name = data['full_name']
        
        # Update avatar
        if 'avatar' in data:
            user.avatar = data['avatar'][:10]  # Limit to 10 characters
        
        user.save()
        
        return Response({
            'success': True,
            'message': _('Profile updated successfully'),
            'user': {
                'email': user.email,
                'full_name': user.full_name,
            }
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password"""
    try:
        user = request.user
        data = request.data
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if not old_password or not new_password or not confirm_password:
            return Response({
                'error': _('All password fields are required')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check old password
        if not user.check_password(old_password):
            return Response({
                'error': _('Current password is incorrect')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if new passwords match
        if new_password != confirm_password:
            return Response({
                'error': _('New passwords do not match')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate new password
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response({
                'error': '; '.join(e.messages)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        return Response({
            'success': True,
            'message': _('Password changed successfully')
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_statistics(request):
    """Get detailed user statistics"""
    try:
        user = request.user
        
        # Get reservation statistics
        total = Reservation.objects.filter(email=user.email).count()
        today = timezone.now().date().strftime('%Y-%m-%d')
        today_count = Reservation.objects.filter(email=user.email, date=today).count()
        
        # Last 7 days
        week_start = (timezone.now().date() - timedelta(days=7)).strftime('%Y-%m-%d')
        week_count = Reservation.objects.filter(
            email=user.email,
            date__gte=week_start
        ).count()
        
        # Last 30 days
        month_start = (timezone.now().date() - timedelta(days=30)).strftime('%Y-%m-%d')
        month_count = Reservation.objects.filter(
            email=user.email,
            date__gte=month_start
        ).count()
        
        # Most used seats
        favorite_seats = Reservation.objects.filter(email=user.email).values('seat_id').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Recent activity
        recent_reservations = Reservation.objects.filter(
            email=user.email
        ).order_by('-created_at')[:5]
        
        return Response({
            'total_reservations': total,
            'today_reservations': today_count,
            'week_reservations': week_count,
            'month_reservations': month_count,
            'favorite_seats': list(favorite_seats),
            'recent_reservations': [
                {
                    'id': str(r.id),
                    'seat_id': r.seat_id,
                    'date': r.date,
                    'created_at': r.created_at.isoformat() if r.created_at else None
                } for r in recent_reservations
            ]
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

