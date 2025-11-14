#!/usr/bin/env python
"""
Ustawia hasło dla admin@coworking.com
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def set_coworking_admin_password():
    """Ustawia hasło dla admin@coworking.com"""
    try:
        admin = User.objects.get(email='admin@coworking.com')
        admin.set_password('admin123')  # Możesz zmienić hasło
        admin.save()
        print("Haslo dla admin@coworking.com ustawione na: admin123")
        print("Mozesz sie teraz zalogowac do Django Admin:")
        print("URL: http://127.0.0.1:8000/admin")
        print("Email: admin@coworking.com")
        print("Haslo: admin123")
    except User.DoesNotExist:
        print("Uzytkownik admin@coworking.com nie istnieje")

if __name__ == '__main__':
    set_coworking_admin_password()



