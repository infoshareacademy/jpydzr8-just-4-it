from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from api.models import Reservation
from datetime import datetime, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Display comprehensive admin statistics'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30, help='Number of days to analyze (default: 30)')

    def handle(self, *args, **options):
        days = options['days']
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        self.stdout.write(self.style.SUCCESS(f'=== ADMIN STATISTICS (Last {days} days) ===\n'))
        
        # User Statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        superusers = User.objects.filter(is_superuser=True).count()
        new_users = User.objects.filter(created_at__gte=start_date).count()
        
        self.stdout.write(self.style.WARNING('[USERS] USER STATISTICS:'))
        self.stdout.write(f'  Total Users: {total_users}')
        self.stdout.write(f'  Active Users: {active_users}')
        self.stdout.write(f'  Staff Users: {staff_users}')
        self.stdout.write(f'  Superusers: {superusers}')
        self.stdout.write(f'  New Users ({days}d): {new_users}')
        
        # Reservation Statistics
        total_reservations = Reservation.objects.count()
        recent_reservations = Reservation.objects.filter(created_at__gte=start_date).count()
        
        # Most popular seats
        popular_seats = Reservation.objects.filter(created_at__gte=start_date)\
            .values('seat_id')\
            .annotate(count=Count('seat_id'))\
            .order_by('-count')[:5]
        
        # Most active users
        active_users_data = Reservation.objects.filter(created_at__gte=start_date)\
            .values('email')\
            .annotate(count=Count('email'))\
            .order_by('-count')[:5]
        
        self.stdout.write(self.style.WARNING('\n[RESERVATIONS] RESERVATION STATISTICS:'))
        self.stdout.write(f'  Total Reservations: {total_reservations}')
        self.stdout.write(f'  Recent Reservations ({days}d): {recent_reservations}')
        
        self.stdout.write(self.style.WARNING('\n[TOP] MOST POPULAR SEATS:'))
        for seat in popular_seats:
            self.stdout.write(f'  {seat["seat_id"]}: {seat["count"]} reservations')
        
        self.stdout.write(self.style.WARNING('\n[ACTIVE] MOST ACTIVE USERS:'))
        for user in active_users_data:
            self.stdout.write(f'  {user["email"]}: {user["count"]} reservations')
        
        # System Health
        today = datetime.now().strftime('%Y-%m-%d')
        today_reservations = Reservation.objects.filter(date=today).count()
        
        self.stdout.write(self.style.WARNING('\n[HEALTH] SYSTEM HEALTH:'))
        self.stdout.write(f'  Today\'s Reservations: {today_reservations}')
        self.stdout.write(f'  Database Status: OK')
        self.stdout.write(f'  Admin Panel: http://localhost:8000/admin/')
