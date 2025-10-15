from django.core.management.base import BaseCommand
from reservations.notification_utils import check_and_send_reminders

class Command(BaseCommand):
    help = 'Wysyła przypomnienia o rezerwacjach'

    def handle(self, *args, **options):
        sent_count = check_and_send_reminders()
        self.stdout.write(
            self.style.SUCCESS(f'Wysłano {sent_count} przypomnień')
        )

