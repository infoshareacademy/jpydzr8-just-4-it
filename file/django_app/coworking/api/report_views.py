from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSuperUser
from .analytics import AnalyticsEngine
from reservations.models import Reservation
import json
import os
from datetime import datetime, timedelta

@api_view(['POST'])
@permission_classes([IsSuperUser])
@csrf_exempt
def generate_report_api(request):
    """API endpoint do generowania raportów"""
    try:
        # Pobierz parametry z request
        report_type = request.data.get('type', 'weekly')
        format_type = request.data.get('format', 'json')
        
        # Generuj dane raportu
        if report_type == 'weekly':
            report_data = AnalyticsEngine.generate_weekly_report()
        elif report_type == 'monthly':
            report_data = AnalyticsEngine.get_dashboard_data(30)
        else:
            days = int(request.data.get('days', 30))
            report_data = AnalyticsEngine.get_dashboard_data(days)
        
        # Dodaj metryki wydajności
        report_data['performance_metrics'] = AnalyticsEngine.get_performance_metrics()
        report_data['usage_heatmap'] = AnalyticsEngine.get_usage_heatmap(7)
        
        # Zapisz raport do pliku
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'coworking_report_{report_type}_{timestamp}.{format_type}'
        
        if format_type == 'json':
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
        elif format_type == 'csv':
            # Konwersja do CSV (uproszczona)
            csv_content = "Metric,Value\n"
            csv_content += f"Total Users,{report_data.get('overview', {}).get('total_users', 0)}\n"
            csv_content += f"Active Users,{report_data.get('overview', {}).get('active_users', 0)}\n"
            csv_content += f"Total Reservations,{report_data.get('overview', {}).get('total_reservations', 0)}\n"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(csv_content)
        
        file_size = os.path.getsize(filename)
        
        return JsonResponse({
            'success': True,
            'message': f'Report generated successfully',
            'data': {
                'filename': filename,
                'file_size': file_size,
                'format': format_type,
                'type': report_type,
                'generated_at': datetime.now().isoformat(),
                'report_data': report_data
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error generating report: {str(e)}'
        }, status=500)

@api_view(['POST'])
@permission_classes([IsSuperUser])
@csrf_exempt
def generate_user_report_api(request):
    """Generate detailed user activity report"""
    try:
        User = get_user_model()
        now = timezone.now()
        days = int(request.data.get('days', 30))
        since = now - timedelta(days=days)

        users_qs = User.objects.all()
        active_users = users_qs.filter(is_active=True)
        staff_users = users_qs.filter(is_staff=True)

        join_field = 'date_joined' if hasattr(User, 'date_joined') else 'created_at'
        join_filter = {f'{join_field}__gte': since}
        new_users = users_qs.filter(**join_filter)
        recently_logged_in = users_qs.filter(last_login__gte=since)

        reservation_counts = Reservation.objects.filter(
            date__gte=since.date(), is_cancelled=False
        ).values('email').annotate(total=models.Count('id')).order_by('-total')[:10]

        report_data = {
            'generated_at': now.isoformat(),
            'range_days': days,
            'overview': {
                'total_users': users_qs.count(),
                'active_users': active_users.count(),
                'staff_users': staff_users.count(),
                'new_users': new_users.count(),
                'recent_logins': recently_logged_in.count(),
            },
            'new_users': [
                {
                    'email': user.email,
                    'date_joined': getattr(user, join_field).isoformat() if getattr(user, join_field, None) else None,
                    'is_active': user.is_active,
                } for user in new_users.order_by(f'-{join_field}')[:50]
            ],
            'recent_logins': [
                {
                    'email': user.email,
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'is_staff': user.is_staff,
                } for user in recently_logged_in.order_by('-last_login')[:50]
            ],
            'top_reservation_emails': list(reservation_counts),
        }

        reports_dir = str(getattr(settings, 'REPORTS_DIR', settings.BASE_DIR))
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        os.makedirs(reports_dir, exist_ok=True)
        filename = os.path.join(reports_dir, f'user_report_{timestamp}.json')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)

        return JsonResponse({
            'success': True,
            'message': 'User report generated successfully',
            'data': {
                'filename': filename,
                'generated_at': now.isoformat(),
                'report_data': report_data,
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error generating user report: {str(e)}'
        }, status=500)

@api_view(['GET'])
@permission_classes([IsSuperUser])
def download_report(request):
    """Endpoint do pobierania wygenerowanych raportów"""
    try:
        filename = request.GET.get('filename')
        if not filename:
            return JsonResponse({'error': 'Filename parameter required'}, status=400)
        
        if not os.path.exists(filename):
            return JsonResponse({'error': 'File not found'}, status=404)
        
        # Określ content type
        if filename.endswith('.json'):
            content_type = 'application/json'
        elif filename.endswith('.csv'):
            content_type = 'text/csv'
        else:
            content_type = 'application/octet-stream'
        
        # Zwróć plik
        with open(filename, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsSuperUser])
def list_reports(request):
    """Lista dostępnych raportów"""
    try:
        # Znajdź wszystkie pliki raportów
        import glob
        report_files = glob.glob('coworking_report_*.json') + glob.glob('coworking_report_*.csv')
        
        reports = []
        for file in report_files:
            if os.path.exists(file):
                stat = os.stat(file)
                reports.append({
                    'filename': file,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Sortuj według daty utworzenia (najnowsze pierwsze)
        reports.sort(key=lambda x: x['created'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'reports': reports,
            'count': len(reports)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




