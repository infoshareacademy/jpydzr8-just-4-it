from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.user_management import UserRoleManager, UserActivityTracker
from api.models import Reservation

User = get_user_model()

class Command(BaseCommand):
    help = 'Setup user roles and permissions system'

    def add_arguments(self, parser):
        parser.add_argument('--assign-role', type=str, help='Assign role to user (email,role)')
        parser.add_argument('--remove-role', type=str, help='Remove role from user (email,role)')
        parser.add_argument('--list-roles', action='store_true', help='List all available roles')
        parser.add_argument('--create-roles', action='store_true', help='Create all default roles')
        parser.add_argument('--user-activity', type=str, help='Show user activity (email)')
        parser.add_argument('--inactive-users', type=int, default=30, help='Show inactive users (days)')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== USER ROLE MANAGEMENT ===\n'))
        
        if options['create_roles']:
            self.create_roles()
        
        if options['list_roles']:
            self.list_roles()
        
        if options['assign_role']:
            self.assign_role(options['assign_role'])
        
        if options['remove_role']:
            self.remove_role(options['remove_role'])
        
        if options['user_activity']:
            self.show_user_activity(options['user_activity'])
        
        if options['inactive_users']:
            self.show_inactive_users(options['inactive_users'])

    def create_roles(self):
        """Tworzy wszystkie domyślne role"""
        self.stdout.write(self.style.WARNING('Creating user roles...'))
        
        try:
            created_groups = UserRoleManager.create_roles()
            
            if created_groups:
                self.stdout.write(self.style.SUCCESS(f'Created {len(created_groups)} roles:'))
                for group in created_groups:
                    self.stdout.write(f'  - {group.name}')
            else:
                self.stdout.write(self.style.SUCCESS('All roles already exist'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating roles: {e}'))

    def list_roles(self):
        """Wyświetla wszystkie dostępne role"""
        self.stdout.write(self.style.WARNING('Available roles:'))
        
        for role_key, role_data in UserRoleManager.ROLES.items():
            self.stdout.write(f'  {role_key}: {role_data["name"]}')
            self.stdout.write(f'    Description: {role_data["description"]}')
            self.stdout.write(f'    Permissions: {len(role_data["permissions"])} permissions')
            self.stdout.write('')

    def assign_role(self, user_role_str):
        """Przypisuje rolę użytkownikowi"""
        try:
            email, role = user_role_str.split(',')
            email = email.strip().lower()
            
            user = User.objects.get(email=email)
            UserRoleManager.assign_role(user, role.strip())
            
            self.stdout.write(self.style.SUCCESS(f'Role "{role}" assigned to {email}'))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User not found: {email}'))
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error: {e}'))

    def remove_role(self, user_role_str):
        """Usuwa rolę użytkownika"""
        try:
            email, role = user_role_str.split(',')
            email = email.strip().lower()
            
            user = User.objects.get(email=email)
            UserRoleManager.remove_role(user, role.strip())
            
            self.stdout.write(self.style.SUCCESS(f'Role "{role}" removed from {email}'))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User not found: {email}'))
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error: {e}'))

    def show_user_activity(self, email):
        """Pokazuje aktywność użytkownika"""
        try:
            user = User.objects.get(email=email.lower())
            activity = UserActivityTracker.get_user_activity(user)
            
            self.stdout.write(self.style.WARNING(f'User Activity: {email}'))
            self.stdout.write(f'  Full Name: {activity["user"]["full_name"]}')
            self.stdout.write(f'  Active: {activity["user"]["is_active"]}')
            self.stdout.write(f'  Last Login: {activity["user"]["last_login"]}')
            self.stdout.write(f'  Total Reservations: {activity["activity"]["total_reservations"]}')
            self.stdout.write(f'  Unique Seats Used: {activity["activity"]["unique_seats_used"]}')
            self.stdout.write(f'  Last Reservation: {activity["activity"]["last_reservation"]}')
            
            if activity["reservations"]:
                self.stdout.write(self.style.WARNING('\nRecent Reservations:'))
                for res in activity["reservations"][:5]:
                    self.stdout.write(f'  - {res["seat_id"]} on {res["date"]} ({res["created_at"]})')
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User not found: {email}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))

    def show_inactive_users(self, days):
        """Pokazuje nieaktywnych użytkowników"""
        inactive_data = UserActivityTracker.get_inactive_users(days)
        
        self.stdout.write(self.style.WARNING(f'Inactive Users (last {days} days):'))
        
        if inactive_data['inactive_by_login']:
            self.stdout.write(self.style.WARNING('\nInactive by Login:'))
            for user in inactive_data['inactive_by_login'][:10]:
                self.stdout.write(f'  - {user["email"]} (last login: {user["last_login"]})')
        
        if inactive_data['inactive_by_reservations']:
            self.stdout.write(self.style.WARNING('\nNever Made Reservations:'))
            for user in inactive_data['inactive_by_reservations'][:10]:
                self.stdout.write(f'  - {user["email"]} (created: {user["created_at"]})')
        
        if not inactive_data['inactive_by_login'] and not inactive_data['inactive_by_reservations']:
            self.stdout.write(self.style.SUCCESS('No inactive users found'))




