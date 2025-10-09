from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone
from api.models import User, Reservation
from datetime import datetime, timedelta
import csv
import json

class UserRoleManager:
    """Menadżer ról i uprawnień użytkowników"""
    
    ROLES = {
        'admin': {
            'name': 'Administrator',
            'description': 'Pełny dostęp do systemu',
            'permissions': ['all']
        },
        'manager': {
            'name': 'Manager',
            'description': 'Zarządzanie rezerwacjami i użytkownikami',
            'permissions': ['view_user', 'change_user', 'view_reservation', 'add_reservation', 'change_reservation', 'delete_reservation']
        },
        'hr': {
            'name': 'HR',
            'description': 'Zarządzanie użytkownikami',
            'permissions': ['view_user', 'add_user', 'change_user']
        },
        'regular': {
            'name': 'Regular User',
            'description': 'Podstawowe funkcje użytkownika',
            'permissions': ['view_reservation', 'add_reservation']
        }
    }
    
    @classmethod
    def create_roles(cls):
        """Tworzy role i grupy użytkowników"""
        created_groups = []
        
        for role_key, role_data in cls.ROLES.items():
            group, created = Group.objects.get_or_create(name=role_data['name'])
            
            if created:
                # Przypisz uprawnienia do grupy
                if role_data['permissions'] == ['all']:
                    # Administrator - wszystkie uprawnienia
                    all_permissions = Permission.objects.all()
                    group.permissions.set(all_permissions)
                else:
                    # Inne role - określone uprawnienia
                    permissions = []
                    for perm_codename in role_data['permissions']:
                        try:
                            if '.' in perm_codename:
                                app_label, codename = perm_codename.split('.')
                                perm = Permission.objects.get(content_type__app_label=app_label, codename=codename)
                            else:
                                # Dla uprawnień modeli API
                                perm = Permission.objects.filter(codename__contains=perm_codename).first()
                            
                            if perm:
                                permissions.append(perm)
                        except Permission.DoesNotExist:
                            continue
                    
                    group.permissions.set(permissions)
                
                created_groups.append(group)
        
        return created_groups
    
    @classmethod
    def assign_role(cls, user, role_key):
        """Przypisuje rolę użytkownikowi"""
        if role_key not in cls.ROLES:
            raise ValueError(f"Unknown role: {role_key}")
        
        role_data = cls.ROLES[role_key]
        group = Group.objects.get(name=role_data['name'])
        user.groups.add(group)
        
        # Dodatkowe ustawienia dla ról
        if role_key == 'admin':
            user.is_staff = True
            user.is_superuser = True
        elif role_key == 'manager':
            user.is_staff = True
        elif role_key == 'hr':
            user.is_staff = True
        
        user.save()
        return group
    
    @classmethod
    def remove_role(cls, user, role_key):
        """Usuwa rolę użytkownika"""
        if role_key not in cls.ROLES:
            raise ValueError(f"Unknown role: {role_key}")
        
        role_data = cls.ROLES[role_key]
        group = Group.objects.get(name=role_data['name'])
        user.groups.remove(group)
        
        # Reset uprawnień jeśli nie ma innych ról
        if user.groups.count() == 0:
            user.is_staff = False
            user.is_superuser = False
            user.save()
    
    @classmethod
    def get_user_roles(cls, user):
        """Pobiera role użytkownika"""
        return user.groups.all()

class UserActivityTracker:
    """Śledzenie aktywności użytkowników"""
    
    @staticmethod
    def get_user_activity(user, days=30):
        """Pobiera aktywność użytkownika"""
        start_date = timezone.now() - timedelta(days=days)
        
        # Rezerwacje użytkownika
        reservations = Reservation.objects.filter(
            email=user.email,
            created_at__gte=start_date
        ).order_by('-created_at')
        
        # Statystyki
        total_reservations = reservations.count()
        unique_seats = reservations.values('seat_id').distinct().count()
        
        # Ostatnia aktywność
        last_reservation = reservations.first()
        last_login = user.last_login
        
        return {
            'user': {
                'email': user.email,
                'full_name': user.full_name,
                'is_active': user.is_active,
                'last_login': last_login
            },
            'activity': {
                'total_reservations': total_reservations,
                'unique_seats_used': unique_seats,
                'last_reservation': last_reservation.created_at if last_reservation else None,
                'period_days': days
            },
            'reservations': [
                {
                    'id': res.id,
                    'seat_id': res.seat_id,
                    'date': res.date,
                    'created_at': res.created_at
                } for res in reservations[:10]  # Ostatnie 10 rezerwacji
            ]
        }
    
    @staticmethod
    def get_inactive_users(days=30):
        """Znajduje nieaktywnych użytkowników"""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Użytkownicy bez logowania
        inactive_by_login = User.objects.filter(
            last_login__lt=cutoff_date,
            is_active=True
        ).exclude(is_superuser=True)
        
        # Użytkownicy bez rezerwacji
        users_with_reservations = Reservation.objects.values_list('email', flat=True).distinct()
        inactive_by_reservations = User.objects.filter(
            is_active=True
        ).exclude(email__in=users_with_reservations).exclude(is_superuser=True)
        
        return {
            'inactive_by_login': list(inactive_by_login.values('email', 'full_name', 'last_login')),
            'inactive_by_reservations': list(inactive_by_reservations.values('email', 'full_name', 'created_at')),
            'period_days': days
        }

class BulkUserManager:
    """Masowe zarządzanie użytkownikami"""
    
    @staticmethod
    def bulk_create_users(users_data, default_role='regular'):
        """Masowe tworzenie użytkowników"""
        created_users = []
        errors = []
        
        with transaction.atomic():
            for user_data in users_data:
                try:
                    email = user_data.get('email', '').strip().lower()
                    full_name = user_data.get('full_name', '')
                    password = user_data.get('password', 'defaultpassword123')
                    
                    if not email:
                        errors.append(f"Missing email for user: {user_data}")
                        continue
                    
                    if User.objects.filter(email=email).exists():
                        errors.append(f"User already exists: {email}")
                        continue
                    
                    # Utwórz użytkownika
                    user = User.objects.create_user(
                        email=email,
                        password=password,
                        full_name=full_name
                    )
                    
                    # Przypisz rolę
                    UserRoleManager.assign_role(user, default_role)
                    
                    created_users.append(user)
                    
                except Exception as e:
                    errors.append(f"Error creating user {user_data.get('email', 'unknown')}: {str(e)}")
        
        return {
            'created_users': len(created_users),
            'errors': errors,
            'users': [{'email': u.email, 'full_name': u.full_name} for u in created_users]
        }
    
    @staticmethod
    def bulk_import_from_csv(csv_file_path, default_role='regular'):
        """Import użytkowników z pliku CSV"""
        users_data = []
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    users_data.append({
                        'email': row.get('email', ''),
                        'full_name': row.get('full_name', ''),
                        'password': row.get('password', 'defaultpassword123')
                    })
            
            return BulkUserManager.bulk_create_users(users_data, default_role)
            
        except Exception as e:
            return {
                'created_users': 0,
                'errors': [f"CSV import error: {str(e)}"],
                'users': []
            }
