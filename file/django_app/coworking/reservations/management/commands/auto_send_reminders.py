"""
Automatic reminder sending command - can be run continuously
"""
from django.core.management.base import BaseCommand
from reservations.notification_utils import check_and_send_reminders
import time
from datetime import datetime


class Command(BaseCommand):
    help = 'Automatically sends reservation reminders every 5 minutes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=300,  # 5 minutes
            help='Interval in seconds between checks (default: 300 = 5 minutes)',
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run once and exit (instead of continuous)',
        )

    def handle(self, *args, **options):
        interval = options['interval']
        run_once = options.get('once', False)
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Starting automatic reminder system (interval: {interval}s)')
        )
        self.stdout.write('   Press Ctrl+C to stop')
        
        try:
            while True:
                try:
                    sent_count = check_and_send_reminders()
                    if sent_count > 0:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'[{datetime.now().strftime("%H:%M:%S")}] Sent {sent_count} reminder(s)'
                            )
                        )
                    else:
                        self.stdout.write(
                            f'[{datetime.now().strftime("%H:%M:%S")}] No reminders to send'
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error sending reminders: {e}')
                    )
                
                if run_once:
                    break
                
                # Wait before next check
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.SUCCESS('\n✅ Automatic reminder system stopped')
            )

