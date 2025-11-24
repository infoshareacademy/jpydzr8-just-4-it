"""
Automatic weekly report sending - runs once per week
"""
from django.core.management.base import BaseCommand
from reservations.notification_utils import send_weekly_reports
from datetime import datetime


class Command(BaseCommand):
    help = 'Send weekly reports (run once per week, e.g., Sunday at 20:00)'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(f'📊 Sending weekly reports at {datetime.now()}')
        )
        
        try:
            sent_count = send_weekly_reports()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Sent {sent_count} weekly reports')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {e}')
            )

