from django.core.management.base import BaseCommand
from reservations.notification_utils import send_weekly_reports

class Command(BaseCommand):
    help = 'Wysyła tygodniowe raporty rezerwacji'

    def handle(self, *args, **options):
        sent_count = send_weekly_reports()
        self.stdout.write(
            self.style.SUCCESS(f'Wysłano {sent_count} tygodniowych raportów')
        )

