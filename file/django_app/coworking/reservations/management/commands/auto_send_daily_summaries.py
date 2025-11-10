"""
Automatic daily summary sending - runs once per day
"""
from django.core.management.base import BaseCommand
from reservations.notification_utils import send_daily_summaries
from datetime import datetime


class Command(BaseCommand):
    help = 'Send daily summaries (run once per day, e.g., at 20:00)'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(f'📧 Sending daily summaries at {datetime.now()}')
        )
        
        try:
            sent_count = send_daily_summaries()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Sent {sent_count} daily summaries')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {e}')
            )

