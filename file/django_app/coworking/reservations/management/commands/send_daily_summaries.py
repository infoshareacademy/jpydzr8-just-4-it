from django.core.management.base import BaseCommand
from reservations.notification_utils import send_daily_summaries

class Command(BaseCommand):
    help = 'Wysyła dzienne podsumowania rezerwacji'

    def handle(self, *args, **options):
        sent_count = send_daily_summaries()
        self.stdout.write(
            self.style.SUCCESS(f'Wysłano {sent_count} dziennych podsumowań')
        )

