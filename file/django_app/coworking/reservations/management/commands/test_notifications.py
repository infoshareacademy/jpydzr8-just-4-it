from django.core.management.base import BaseCommand
from reservations.notification_utils import send_notification_email, send_daily_summaries, send_weekly_reports, check_and_send_reminders

class Command(BaseCommand):
    help = 'Test systemu powiadomień'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email do testowania')
        parser.add_argument('--type', type=str, choices=['email', 'daily', 'weekly', 'reminder'], 
                          default='email', help='Typ testu')

    def handle(self, *args, **options):
        email = options['email']
        test_type = options['type']
        
        if not email:
            self.stdout.write(
                self.style.ERROR('Podaj email: --email test@example.com')
            )
            return
        
        if test_type == 'email':
            success = send_notification_email(
                email, 
                'Test powiadomienia', 
                'To jest test powiadomienia z systemu rezerwacji stanowisk.',
                'CONFIRMATION'
            )
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'Test email wysłany do {email}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Błąd wysyłania emaila do {email}')
                )
        
        elif test_type == 'daily':
            sent_count = send_daily_summaries()
            self.stdout.write(
                self.style.SUCCESS(f'Wysłano {sent_count} dziennych podsumowań')
            )
        
        elif test_type == 'weekly':
            sent_count = send_weekly_reports()
            self.stdout.write(
                self.style.SUCCESS(f'Wysłano {sent_count} tygodniowych raportów')
            )
        
        elif test_type == 'reminder':
            sent_count = check_and_send_reminders()
            self.stdout.write(
                self.style.SUCCESS(f'Wysłano {sent_count} przypomnień')
            )

