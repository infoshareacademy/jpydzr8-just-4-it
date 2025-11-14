#!/usr/bin/env python
"""
Sprawdź hasło dla admin@coworking.com
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def get_admin_password():
    """Sprawdź hasło dla admin@coworking.com"""
    
    print("=== SPRAWDZANIE HASŁA ADMIN ===")
    
    try:
        admin = User.objects.get(email='admin@coworking.com')
        print(f"Użytkownik: {admin.email}")
        print(f"Super user: {admin.is_superuser}")
        print(f"Staff: {admin.is_staff}")
        print(f"Active: {admin.is_active}")
        print(f"Last login: {admin.last_login}")
        
        # Sprawdź czy hasło jest ustawione
        if admin.has_usable_password():
            print("OK: Hasło jest ustawione")
        else:
            print("ERROR: Brak hasła")
        
        print("\n=== USTAWIANIE NOWEGO HASŁA ===")
        admin.set_password('admin123')
        admin.save()
        print("OK: Hasło ustawione na: admin123")
        
        print("\n=== DANE LOGOWANIA ===")
        print("URL: http://127.0.0.1:8000/admin")
        print("Email: admin@coworking.com")
        print("Hasło: admin123")
        
    except User.DoesNotExist:
        print("ERROR: Użytkownik admin@coworking.com nie istnieje")
        print("Tworzę nowego admina...")
        
        admin = User.objects.create_user(
            email='admin@coworking.com',
            password='admin123'
        )
        admin.is_superuser = True
        admin.is_staff = True
        admin.is_active = True
        admin.save()
        
        print("OK: Admin utworzony!")
        print("URL: http://127.0.0.1:8000/admin")
        print("Email: admin@coworking.com")
        print("Hasło: admin123")

if __name__ == '__main__':
    get_admin_password()
