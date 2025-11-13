#!/usr/bin/env python
"""
Skrypt do ustawienia hasła dla admin
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def set_admin_password():
    """Ustawia hasło dla admin"""
    try:
        admin = User.objects.get(email='admin@example.com')
        admin.set_password('admin123')  # Możesz zmienić hasło
        admin.save()
        print("Hasło dla admin ustawione na: admin123")
        print("Możesz się teraz zalogować do Django Admin")
    except User.DoesNotExist:
        print("Użytkownik admin@example.com nie istnieje")
        print("Tworzę nowego admin...")
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='admin123'
        )
        print("Admin utworzony z hasłem: admin123")

if __name__ == '__main__':
    set_admin_password()



