from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSuperUser
from .analytics import AnalyticsEngine
import json
import os
from datetime import datetime

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
