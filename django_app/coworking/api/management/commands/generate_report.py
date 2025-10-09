from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from api.analytics import AnalyticsEngine
from api.models import User, Reservation
import json
import os

class Command(BaseCommand):
    help = 'Generate comprehensive reports for superuser'

    def add_arguments(self, parser):
        parser.add_argument('--type', choices=['weekly', 'monthly', 'custom'], default='weekly', help='Report type')
        parser.add_argument('--days', type=int, help='Number of days for custom report')
        parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Output format')
        parser.add_argument('--output', type=str, help='Output file path')

    def handle(self, *args, **options):
        report_type = options['type']
        output_format = options['format']
        output_file = options['output']
        
        self.stdout.write(self.style.SUCCESS(f'=== GENERATING {report_type.upper()} REPORT ===\n'))
        
        if report_type == 'weekly':
            report_data = AnalyticsEngine.generate_weekly_report()
        elif report_type == 'monthly':
            report_data = AnalyticsEngine.get_dashboard_data(30)
        else:  # custom
            days = options['days'] or 30
            report_data = AnalyticsEngine.get_dashboard_data(days)
        
        # Dodaj dodatkowe metryki
        report_data['performance_metrics'] = AnalyticsEngine.get_performance_metrics()
        report_data['usage_heatmap'] = AnalyticsEngine.get_usage_heatmap(7)
        
        # Generuj raport
        if output_format == 'json':
            report_content = json.dumps(report_data, indent=2, default=str)
            file_extension = 'json'
        else:  # csv
            report_content = self._generate_csv_report(report_data)
            file_extension = 'csv'
        
        # Zapisz do pliku lub wyświetl
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            self.stdout.write(self.style.SUCCESS(f'Report saved to: {output_file}'))
        else:
            # Domyślna nazwa pliku
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f'coworking_report_{report_type}_{timestamp}.{file_extension}'
            
            with open(default_filename, 'w', encoding='utf-8') as f:
                f.write(report_content)
            self.stdout.write(self.style.SUCCESS(f'Report saved to: {default_filename}'))
        
        # Wyświetl podsumowanie
        self._display_summary(report_data)

    def _generate_csv_report(self, data):
        """Generuje raport w formacie CSV"""
        csv_lines = []
        
        # Nagłówek
        csv_lines.append('Report Type,Value,Details')
        
        # Podstawowe statystyki
        if 'overview' in data:
            csv_lines.append(f'Total Users,{data["overview"].get("total_users", 0)},')
            csv_lines.append(f'Active Users,{data["overview"].get("active_users", 0)},')
            csv_lines.append(f'Total Reservations,{data["overview"].get("total_reservations", 0)},')
        
        # Popularne miejsca
        if 'trends' in data and 'seat_popularity' in data['trends']:
            for seat in data['trends']['seat_popularity']:
                csv_lines.append(f'Popular Seat,{seat["seat_id"]},{seat["count"]} reservations')
        
        # Metryki wydajności
        if 'performance_metrics' in data:
            metrics = data['performance_metrics']
            csv_lines.append(f'Avg Response Time,{metrics.get("avg_response_time", 0)}ms,')
            csv_lines.append(f'Database Size,{metrics.get("db_size_mb", 0)}MB,')
            csv_lines.append(f'Active Sessions,{metrics.get("active_sessions", 0)},')
            csv_lines.append(f'Error Rate,{metrics.get("error_rate", 0)}%,')
        
        return '\n'.join(csv_lines)

    def _display_summary(self, data):
        """Wyświetla podsumowanie raportu"""
        self.stdout.write(self.style.WARNING('\n=== REPORT SUMMARY ==='))
        
        if 'overview' in data:
            overview = data['overview']
            self.stdout.write(f'Total Users: {overview.get("total_users", 0)}')
            self.stdout.write(f'Active Users: {overview.get("active_users", 0)}')
            self.stdout.write(f'Total Reservations: {overview.get("total_reservations", 0)}')
        
        if 'performance_metrics' in data:
            metrics = data['performance_metrics']
            self.stdout.write(f'Avg Response Time: {metrics.get("avg_response_time", 0)}ms')
            self.stdout.write(f'Database Size: {metrics.get("db_size_mb", 0)}MB')
            self.stdout.write(f'Active Sessions: {metrics.get("active_sessions", 0)}')
            self.stdout.write(f'Uptime: {metrics.get("uptime_percentage", 0)}%')
