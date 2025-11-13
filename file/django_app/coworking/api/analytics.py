from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from api.models import User, Reservation
import json

class AnalyticsEngine:
    """Silnik analityczny dla dashboardu superusera"""
    
    @staticmethod
    def get_dashboard_data(days=30):
        """Główne dane dla dashboardu"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Podstawowe statystyki
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        total_reservations = Reservation.objects.count()
        
        # Trendy w czasie
        daily_reservations = Reservation.objects.filter(
            created_at__gte=start_date
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        # Popularność miejsc
        seat_popularity = Reservation.objects.values('seat_id').annotate(
            count=Count('seat_id')
        ).order_by('-count')[:10]
        
        # Aktywność użytkowników
        user_activity = Reservation.objects.values('email').annotate(
            count=Count('email')
        ).order_by('-count')[:10]
        
        # Wykorzystanie w czasie (heatmapa)
        occupancy_by_date = Reservation.objects.filter(
            created_at__gte=start_date
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        return {
            'overview': {
                'total_users': total_users,
                'active_users': active_users,
                'total_reservations': total_reservations,
                'period_days': days
            },
            'trends': {
                'daily_reservations': list(daily_reservations),
                'seat_popularity': list(seat_popularity),
                'user_activity': list(user_activity),
                'occupancy_by_date': list(occupancy_by_date)
            }
        }
    
    @staticmethod
    def get_usage_heatmap(days=7):
        """Generuje dane dla heatmapy wykorzystania miejsc"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Pobierz wszystkie unikalne miejsca i daty
        reservations = Reservation.objects.filter(
            created_at__gte=start_date
        ).values('seat_id', 'date').annotate(
            count=Count('id')
        ).order_by('seat_id', 'date')
        
        # Organizuj dane w formacie heatmapy
        heatmap_data = {}
        for res in reservations:
            seat_id = res['seat_id']
            date = res['date']
            count = res['count']
            
            if seat_id not in heatmap_data:
                heatmap_data[seat_id] = {}
            heatmap_data[seat_id][date] = count
        
        return heatmap_data
    
    @staticmethod
    def get_performance_metrics():
        """Metryki wydajności systemu"""
        # Średni czas odpowiedzi (symulacja)
        avg_response_time = 120  # ms
        
        # Wykorzystanie bazy danych
        db_size_mb = 2.5  # MB
        
        # Aktywne sesje
        active_sessions = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        # Błędy systemu (symulacja)
        error_rate = 0.02  # 2%
        
        return {
            'avg_response_time': avg_response_time,
            'db_size_mb': db_size_mb,
            'active_sessions': active_sessions,
            'error_rate': error_rate,
            'uptime_percentage': 99.8
        }
    
    @staticmethod
    def generate_weekly_report():
        """Generuje raport tygodniowy"""
        week_start = timezone.now() - timedelta(days=7)
        
        # Nowi użytkownicy
        new_users = User.objects.filter(created_at__gte=week_start).count()
        
        # Nowe rezerwacje
        new_reservations = Reservation.objects.filter(created_at__gte=week_start).count()
        
        # Najpopularniejsze miejsca
        top_seats = Reservation.objects.filter(
            created_at__gte=week_start
        ).values('seat_id').annotate(
            count=Count('seat_id')
        ).order_by('-count')[:5]
        
        # Najaktywniejsze dni
        daily_stats = Reservation.objects.filter(
            created_at__gte=week_start
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return {
            'period': 'Last 7 days',
            'new_users': new_users,
            'new_reservations': new_reservations,
            'top_seats': list(top_seats),
            'daily_stats': list(daily_stats),
            'generated_at': timezone.now().isoformat()
        }




