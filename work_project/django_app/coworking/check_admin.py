#!/usr/bin/env python
"""
Sprawdza czy istnieje super user
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def check_admin():
    """Sprawdza czy istnieje super user"""
    try:
        admin = User.objects.get(email='admin@example.com')
        if admin.is_superuser:
            print("OK Super user juz istnieje!")
            print(f"Email: {admin.email}")
            print(f"Super user: {admin.is_superuser}")
            print(f"Staff: {admin.is_staff}")
            print("\nMozesz sie zalogowac do Django Admin:")
            print("URL: http://127.0.0.1:8000/admin")
            print("Email: admin@example.com")
            print("Haslo: (to co ustawiles)")
        else:
            print("UWAGA: Uzytkownik istnieje ale nie jest super userem")
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
            print("OK Naprawiono - teraz jest super userem!")
    except User.DoesNotExist:
        print("ERROR Super user nie istnieje")
        print("\nAby utworzyc super usera, uruchom:")
        print("python set_admin_password.py")

if __name__ == '__main__':
    check_admin()
