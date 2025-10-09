from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from api.models import Reservation
from datetime import datetime, timedelta
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'System cleanup and maintenance tools'

    def add_arguments(self, parser):
        parser.add_argument('--clean-old-reservations', action='store_true', help='Remove reservations older than specified days')
        parser.add_argument('--days', type=int, default=365, help='Days threshold for cleanup (default: 365)')
        parser.add_argument('--clean-inactive-users', action='store_true', help='Deactivate users inactive for specified days')
        parser.add_argument('--user-days', type=int, default=180, help='Days threshold for inactive users (default: 180)')
        parser.add_argument('--backup-db', action='store_true', help='Create database backup')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== SYSTEM CLEANUP TOOL ===\n'))
        
        if options['clean_old_reservations']:
            self.cleanup_old_reservations(options['days'], options['dry_run'])
        
        if options['clean_inactive_users']:
            self.cleanup_inactive_users(options['user_days'], options['dry_run'])
        
        if options['backup_db']:
            self.backup_database()

    def cleanup_old_reservations(self, days, dry_run):
        """Remove reservations older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        old_reservations = Reservation.objects.filter(created_at__lt=cutoff_date)
        
        count = old_reservations.count()
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'[DRY RUN] Would delete {count} reservations older than {days} days'))
            if count > 0:
                self.stdout.write('Sample reservations to be deleted:')
                for res in old_reservations[:5]:
                    self.stdout.write(f'  - {res.id}: {res.seat_id} on {res.date}')
        else:
            if count > 0:
                with transaction.atomic():
                    old_reservations.delete()
                self.stdout.write(self.style.SUCCESS(f'✅ Deleted {count} old reservations'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ No old reservations to clean up'))

    def cleanup_inactive_users(self, days, dry_run):
        """Deactivate users who haven't logged in for specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Find users who haven't logged in recently and are not staff/superuser
        inactive_users = User.objects.filter(
            last_login__lt=cutoff_date,
            is_staff=False,
            is_superuser=False,
            is_active=True
        )
        
        count = inactive_users.count()
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'[DRY RUN] Would deactivate {count} inactive users'))
            if count > 0:
                self.stdout.write('Sample users to be deactivated:')
                for user in inactive_users[:5]:
                    self.stdout.write(f'  - {user.email} (last login: {user.last_login})')
        else:
            if count > 0:
                with transaction.atomic():
                    inactive_users.update(is_active=False)
                self.stdout.write(self.style.SUCCESS(f'✅ Deactivated {count} inactive users'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ No inactive users to clean up'))

    def backup_database(self):
        """Create a backup of the SQLite database"""
        try:
            from django.conf import settings
            db_path = settings.DATABASES['default']['NAME']
            
            if os.path.exists(db_path):
                import shutil
                from datetime import datetime
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f'{db_path}.backup_{timestamp}'
                
                shutil.copy2(db_path, backup_path)
                self.stdout.write(self.style.SUCCESS(f'✅ Database backed up to: {backup_path}'))
            else:
                self.stdout.write(self.style.ERROR('❌ Database file not found'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Backup failed: {e}'))
