from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from api.smart_reservations import SmartReservationManager, WaitlistManager, RecurringReservationManager
from api.models import Reservation

class Command(BaseCommand):
    help = 'Smart reservation management tools'

    def add_arguments(self, parser):
        parser.add_argument('--cleanup-expired', action='store_true', help='Clean up expired reservations')
        parser.add_argument('--days-threshold', type=int, default=1, help='Days threshold for cleanup')
        parser.add_argument('--detect-conflicts', action='store_true', help='Detect reservation conflicts')
        parser.add_argument('--suggest-alternatives', type=str, help='Suggest alternative seats (seat_id,date)')
        parser.add_argument('--usage-patterns', type=int, default=30, help='Analyze usage patterns (days)')
        parser.add_argument('--create-recurring', action='store_true', help='Create recurring reservation')
        parser.add_argument('--frequency', choices=['daily', 'weekly', 'monthly'], default='weekly', help='Recurring frequency')
        parser.add_argument('--end-date', type=str, help='End date for recurring (YYYY-MM-DD)')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== SMART RESERVATION MANAGEMENT ===\n'))
        
        if options['cleanup_expired']:
            self.cleanup_expired(options['days_threshold'])
        
        if options['detect_conflicts']:
            self.detect_conflicts()
        
        if options['suggest_alternatives']:
            self.suggest_alternatives(options['suggest_alternatives'])
        
        if options['usage_patterns']:
            self.analyze_usage_patterns(options['usage_patterns'])
        
        if options['create_recurring']:
            self.create_recurring(options['frequency'], options['end_date'])

    def cleanup_expired(self, days_threshold):
        """Czyści wygasłe rezerwacje"""
        self.stdout.write(self.style.WARNING('Cleaning up expired reservations...'))
        
        result = SmartReservationManager.auto_cleanup_expired_reservations(days_threshold)
        
        self.stdout.write(self.style.SUCCESS(f'Cleaned up {result["cleaned_count"]} expired reservations'))
        self.stdout.write(f'Cutoff date: {result["cutoff_date"]}')
        self.stdout.write(f'Threshold: {result["threshold_days"]} days')

    def detect_conflicts(self):
        """Wykrywa konflikty rezerwacji"""
        self.stdout.write(self.style.WARNING('Detecting reservation conflicts...'))
        
        conflicts = SmartReservationManager.detect_conflicts()
        
        if conflicts:
            self.stdout.write(self.style.ERROR(f'Found {len(conflicts)} conflicts:'))
            for conflict in conflicts:
                self.stdout.write(f'  Seat: {conflict["seat_id"]}, Date: {conflict["date"]}')
                self.stdout.write(f'  Type: {conflict["type"]}, Count: {conflict["count"]}')
                for res in conflict['reservations']:
                    self.stdout.write(f'    - {res["name"]} ({res["email"]}) - {res["created_at"]}')
                self.stdout.write('')
        else:
            self.stdout.write(self.style.SUCCESS('No conflicts found'))

    def suggest_alternatives(self, seat_date_str):
        """Sugeruje alternatywne miejsca"""
        try:
            seat_id, date = seat_date_str.split(',')
            seat_id = seat_id.strip()
            date = date.strip()
            
            self.stdout.write(self.style.WARNING(f'Suggesting alternatives for {seat_id} on {date}...'))
            
            result = SmartReservationManager.suggest_alternative_seats(seat_id, date)
            
            if result['available']:
                self.stdout.write(self.style.SUCCESS(f'Seat {seat_id} is available!'))
            else:
                self.stdout.write(self.style.WARNING(f'Seat {seat_id} is not available'))
                if result['alternatives']:
                    self.stdout.write('Alternative seats:')
                    for alt_seat in result['alternatives']:
                        self.stdout.write(f'  - {alt_seat}')
                else:
                    self.stdout.write('No alternatives found')
            
            self.stdout.write(f'Message: {result["message"]}')
            
        except ValueError:
            self.stdout.write(self.style.ERROR('Invalid format. Use: seat_id,date (e.g., A1,2024-01-15)'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))

    def analyze_usage_patterns(self, days):
        """Analizuje wzorce wykorzystania"""
        self.stdout.write(self.style.WARNING(f'Analyzing usage patterns (last {days} days)...'))
        
        patterns = SmartReservationManager.get_usage_patterns(days)
        
        self.stdout.write(f'Total reservations: {patterns["total_reservations"]}')
        
        if patterns['seat_usage']:
            self.stdout.write(self.style.WARNING('\nMost popular seats:'))
            for seat in patterns['seat_usage'][:10]:
                self.stdout.write(f'  {seat["seat_id"]}: {seat["total_bookings"]} bookings, {seat["unique_users"]} users')
        
        self.stdout.write(self.style.WARNING('\nWeekday patterns:'))
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i, count in patterns['weekday_patterns'].items():
            if count > 0:
                self.stdout.write(f'  {weekdays[i]}: {count} reservations')

    def create_recurring(self, frequency, end_date):
        """Tworzy cykliczną rezerwację"""
        self.stdout.write(self.style.WARNING('Creating recurring reservation...'))
        
        # Przykładowa rezerwacja bazowa
        base_reservation = {
            'seat_id': 'A1',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'name': 'Recurring User',
            'email': 'recurring@example.com'
        }
        
        result = RecurringReservationManager.create_recurring_reservation(
            base_reservation, frequency, end_date
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created {result["created_count"]} recurring reservations'))
        self.stdout.write(f'Frequency: {result["frequency"]}')
        self.stdout.write(f'Base date: {result["base_date"]}')
        self.stdout.write(f'End date: {result["end_date"]}')
        
        if result['reservations']:
            self.stdout.write('Created reservations:')
            for res in result['reservations'][:5]:  # Show first 5
                self.stdout.write(f'  - {res["seat_id"]} on {res["date"]}')
            if len(result['reservations']) > 5:
                self.stdout.write(f'  ... and {len(result["reservations"]) - 5} more')
