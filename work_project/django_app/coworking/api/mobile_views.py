from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSuperUser
from .analytics import AnalyticsEngine
from .smart_reservations import SmartReservationManager
from .user_management import UserActivityTracker
import json

@staff_member_required
def mobile_dashboard(request):
    """Mobile-responsive admin dashboard"""
    return render(request, 'admin/mobile_dashboard.html')

@api_view(['GET'])
@permission_classes([IsSuperUser])
def mobile_api_stats(request):
    """Mobile API endpoint for dashboard stats"""
    try:
        days = int(request.GET.get('days', 7))
        data = AnalyticsEngine.get_dashboard_data(days)
        
        # Dodaj dane specyficzne dla mobile
        mobile_data = {
            'overview': data['overview'],
            'recent_reservations': data['trends'].get('recent_reservations', []),
            'performance': AnalyticsEngine.get_performance_metrics(),
            'mobile_optimized': True,
            'timestamp': timezone.now().isoformat()
        }
        
        return JsonResponse(mobile_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsSuperUser])
@csrf_exempt
def mobile_quick_action(request):
    """Mobile quick actions endpoint"""
    try:
        action = request.data.get('action')
        
        if action == 'cleanup':
            result = SmartReservationManager.auto_cleanup_expired_reservations()
            return JsonResponse({
                'success': True,
                'message': f'Cleaned up {result["cleaned_count"]} expired reservations',
                'data': result
            })
        
        elif action == 'generate_report':
            # Generowanie rzeczywistego raportu
            from .analytics import AnalyticsEngine
            import os
            
            try:
                # Generuj dane raportu
                report_data = AnalyticsEngine.generate_weekly_report()
                report_data['performance_metrics'] = AnalyticsEngine.get_performance_metrics()
                
                # Zapisz raport do pliku
                timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                filename = f'coworking_report_weekly_{timestamp}.json'
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2, default=str)
                
                return JsonResponse({
                    'success': True,
                    'message': f'Report generated successfully: {filename}',
                    'data': {
                        'filename': filename,
                        'report_data': report_data,
                        'file_size': os.path.getsize(filename)
                    }
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error generating report: {str(e)}'
                }, status=500)
        
        elif action == 'health_check':
            health_data = AnalyticsEngine.get_performance_metrics()
            return JsonResponse({
                'success': True,
                'message': 'Health check completed',
                'data': health_data
            })
        
        else:
            return JsonResponse({'error': 'Unknown action'}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsSuperUser])
def mobile_user_activity(request):
    """Mobile endpoint for user activity"""
    try:
        email = request.GET.get('email')
        days = int(request.GET.get('days', 30))
        
        if email:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(email=email)
            activity = UserActivityTracker.get_user_activity(user, days)
            return JsonResponse(activity)
        else:
            # Lista aktywnych użytkowników
            inactive_data = UserActivityTracker.get_inactive_users(days)
            return JsonResponse(inactive_data)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsSuperUser])
def mobile_reservation_insights(request):
    """Mobile endpoint for reservation insights"""
    try:
        days = int(request.GET.get('days', 7))
        
        # Wzorce wykorzystania
        usage_patterns = SmartReservationManager.get_usage_patterns(days)
        
        # Konflikty
        conflicts = SmartReservationManager.detect_conflicts()
        
        # Heatmapa
        heatmap = AnalyticsEngine.get_usage_heatmap(days)
        
        insights = {
            'usage_patterns': usage_patterns,
            'conflicts': conflicts,
            'heatmap': heatmap,
            'period_days': days,
            'mobile_optimized': True
        }
        
        return JsonResponse(insights)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsSuperUser])
def mobile_bulk_operation(request):
    """Mobile bulk operations endpoint"""
    try:
        operation = request.data.get('operation')
        target_ids = request.data.get('ids', [])
        
        if operation == 'activate_users':
            from django.contrib.auth import get_user_model
            User = get_user_model()
            count = User.objects.filter(id__in=target_ids).update(is_active=True)
            return JsonResponse({
                'success': True,
                'message': f'Activated {count} users',
                'count': count
            })
        
        elif operation == 'deactivate_users':
            from django.contrib.auth import get_user_model
            User = get_user_model()
            count = User.objects.filter(id__in=target_ids).update(is_active=False)
            return JsonResponse({
                'success': True,
                'message': f'Deactivated {count} users',
                'count': count
            })
        
        elif operation == 'cancel_reservations':
            from api.models import Reservation
            count = Reservation.objects.filter(id__in=target_ids).count()
            Reservation.objects.filter(id__in=target_ids).delete()
            return JsonResponse({
                'success': True,
                'message': f'Cancelled {count} reservations',
                'count': count
            })
        
        else:
            return JsonResponse({'error': 'Unknown operation'}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsSuperUser])
def mobile_notifications(request):
    """Mobile notifications endpoint"""
    try:
        # Symulacja powiadomień
        notifications = [
            {
                'id': 1,
                'type': 'warning',
                'title': 'System Maintenance',
                'message': 'Scheduled maintenance in 2 hours',
                'timestamp': timezone.now().isoformat(),
                'read': False
            },
            {
                'id': 2,
                'type': 'info',
                'title': 'New User Registration',
                'message': '5 new users registered today',
                'timestamp': (timezone.now() - timedelta(hours=1)).isoformat(),
                'read': False
            },
            {
                'id': 3,
                'type': 'success',
                'title': 'Backup Completed',
                'message': 'Daily backup completed successfully',
                'timestamp': (timezone.now() - timedelta(hours=3)).isoformat(),
                'read': True
            }
        ]
        
        return JsonResponse({
            'notifications': notifications,
            'unread_count': len([n for n in notifications if not n['read']])
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
