from django.core.management.base import BaseCommand
from reservations.recurring_utils import generate_recurring_reservations, check_waitlist_availability

class Command(BaseCommand):
    help = 'Generuje recurring reservations i sprawdza waitlist'

    def handle(self, *args, **options):
        # Generuj recurring reservations
        created_count = generate_recurring_reservations()
        self.stdout.write(
            self.style.SUCCESS(f'Utworzono {created_count} recurring reservations')
        )
        
        # Sprawdź waitlist
        notified_count = check_waitlist_availability()
        self.stdout.write(
            self.style.SUCCESS(f'Powiadomiono {notified_count} osób z waitlist')
        )

