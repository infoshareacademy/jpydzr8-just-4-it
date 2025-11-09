from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from api.models import Reservation
from datetime import datetime, timedelta
import csv
import json

User = get_user_model()

class Command(BaseCommand):
    help = 'Bulk operations for users and reservations'

    def add_arguments(self, parser):
        parser.add_argument('--bulk-import-users', type=str, help='Import users from CSV file')
        parser.add_argument('--bulk-import-reservations', type=str, help='Import reservations from CSV file')
        parser.add_argument('--bulk-export-users', type=str, help='Export users to CSV file')
        parser.add_argument('--bulk-export-reservations', type=str, help='Export reservations to CSV file')
        parser.add_argument('--bulk-delete-reservations', type=str, help='Delete reservations by date range (format: YYYY-MM-DD,YYYY-MM-DD)')
        parser.add_argument('--bulk-update-users', action='store_true', help='Bulk update user permissions')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be done without actually doing it')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== BULK OPERATIONS TOOL ===\n'))
        
        if options['bulk_import_users']:
            self.bulk_import_users(options['bulk_import_users'], options['dry_run'])
        
        if options['bulk_import_reservations']:
            self.bulk_import_reservations(options['bulk_import_reservations'], options['dry_run'])
        
        if options['bulk_export_users']:
            self.bulk_export_users(options['bulk_export_users'])
        
        if options['bulk_export_reservations']:
            self.bulk_export_reservations(options['bulk_export_reservations'])
        
        if options['bulk_delete_reservations']:
            self.bulk_delete_reservations(options['bulk_delete_reservations'], options['dry_run'])
        
        if options['bulk_update_users']:
            self.bulk_update_users(options['dry_run'])

    def bulk_import_users(self, csv_file, dry_run):
        """Import users from CSV file"""
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                users_data = list(reader)
            
            if dry_run:
                self.stdout.write(self.style.WARNING(f'[DRY RUN] Would import {len(users_data)} users'))
                for user_data in users_data[:3]:
                    self.stdout.write(f'  - {user_data.get("email", "N/A")}: {user_data.get("full_name", "N/A")}')
                return
            
            imported_count = 0
            with transaction.atomic():
                for user_data in users_data:
                    email = user_data.get('email', '').strip().lower()
                    full_name = user_data.get('full_name', '')
                    password = user_data.get('password', 'defaultpassword123')
                    is_staff = user_data.get('is_staff', '').lower() == 'true'
                    
                    if email:
                        user, created = User.objects.get_or_create(
                            email=email,
                            defaults={
                                'full_name': full_name,
                                'is_staff': is_staff,
                                'is_active': True
                            }
                        )
                        if created:
                            user.set_password(password)
                            user.save()
                            imported_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'✅ Imported {imported_count} new users'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Import failed: {e}'))

    def bulk_import_reservations(self, csv_file, dry_run):
        """Import reservations from CSV file"""
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                reservations_data = list(reader)
            
            if dry_run:
                self.stdout.write(self.style.WARNING(f'[DRY RUN] Would import {len(reservations_data)} reservations'))
                for res_data in reservations_data[:3]:
                    self.stdout.write(f'  - {res_data.get("seat_id", "N/A")} on {res_data.get("date", "N/A")}')
                return
            
            imported_count = 0
            with transaction.atomic():
                for res_data in reservations_data:
                    reservation_id = res_data.get('id', f"import_{datetime.now().timestamp()}")
                    seat_id = res_data.get('seat_id', '')
                    date = res_data.get('date', '')
                    name = res_data.get('name', '')
                    email = res_data.get('email', '')
                    notes = res_data.get('notes', '')
                    
                    if seat_id and date:
                        reservation, created = Reservation.objects.get_or_create(
                            id=reservation_id,
                            defaults={
                                'seat_id': seat_id,
                                'date': date,
                                'name': name,
                                'email': email,
                                'notes': notes
                            }
                        )
                        if created:
                            imported_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'✅ Imported {imported_count} new reservations'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Import failed: {e}'))

    def bulk_export_users(self, output_file):
        """Export users to CSV file"""
        try:
            users = User.objects.all()
            
            with open(output_file, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['email', 'full_name', 'is_active', 'is_staff', 'is_superuser', 'created_at', 'last_login']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                for user in users:
                    writer.writerow({
                        'email': user.email,
                        'full_name': user.full_name,
                        'is_active': user.is_active,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser,
                        'created_at': user.created_at,
                        'last_login': user.last_login
                    })
            
            self.stdout.write(self.style.SUCCESS(f'✅ Exported {users.count()} users to {output_file}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Export failed: {e}'))

    def bulk_export_reservations(self, output_file):
        """Export reservations to CSV file"""
        try:
            reservations = Reservation.objects.all()
            
            with open(output_file, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['id', 'seat_id', 'date', 'name', 'email', 'notes', 'created_at']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                for reservation in reservations:
                    writer.writerow({
                        'id': reservation.id,
                        'seat_id': reservation.seat_id,
                        'date': reservation.date,
                        'name': reservation.name,
                        'email': reservation.email,
                        'notes': reservation.notes,
                        'created_at': reservation.created_at
                    })
            
            self.stdout.write(self.style.SUCCESS(f'✅ Exported {reservations.count()} reservations to {output_file}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Export failed: {e}'))

    def bulk_delete_reservations(self, date_range, dry_run):
        """Delete reservations by date range"""
        try:
            start_date, end_date = date_range.split(',')
            reservations = Reservation.objects.filter(date__gte=start_date, date__lte=end_date)
            count = reservations.count()
            
            if dry_run:
                self.stdout.write(self.style.WARNING(f'[DRY RUN] Would delete {count} reservations between {start_date} and {end_date}'))
                for res in reservations[:5]:
                    self.stdout.write(f'  - {res.id}: {res.seat_id} on {res.date}')
                return
            
            if count > 0:
                with transaction.atomic():
                    reservations.delete()
                self.stdout.write(self.style.SUCCESS(f'✅ Deleted {count} reservations'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ No reservations found in date range'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Delete failed: {e}'))

    def bulk_update_users(self, dry_run):
        """Bulk update user permissions (example: make all users staff)"""
        if dry_run:
            self.stdout.write(self.style.WARNING('[DRY RUN] Would update user permissions'))
            return
        
        # Example: Make all active users staff members
        users = User.objects.filter(is_active=True, is_staff=False)
        count = users.count()
        
        if count > 0:
            with transaction.atomic():
                users.update(is_staff=True)
            self.stdout.write(self.style.SUCCESS(f'✅ Updated {count} users to staff status'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ No users to update'))




