#!/usr/bin/env python
"""
Sprawdza wszystkich super userow
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def check_all_admins():
    """Sprawdza wszystkich super userow"""
    
    print("=== SPRAWDZANIE WSZYSTKICH SUPER USEROW ===")
    
    # Wszyscy super userzy
    superusers = User.objects.filter(is_superuser=True)
    
    if superusers.exists():
        print(f"Znaleziono {superusers.count()} super userow:")
        print("-" * 50)
        
        for admin in superusers:
            print(f"Email: {admin.email}")
            print(f"Super user: {admin.is_superuser}")
            print(f"Staff: {admin.is_staff}")
            print(f"Active: {admin.is_active}")
            # print(f"Data utworzenia: {admin.date_joined}")  # Pole nie istnieje w tym modelu
            print("-" * 30)
    else:
        print("Brak super userow!")
    
    # Sprawdz konkretnie admin@coworking.com
    print("\n=== SPRAWDZANIE admin@coworking.com ===")
    try:
        admin_coworking = User.objects.get(email='admin@coworking.com')
        print("OK admin@coworking.com istnieje!")
        print(f"Super user: {admin_coworking.is_superuser}")
        print(f"Staff: {admin_coworking.is_staff}")
        print(f"Active: {admin_coworking.is_active}")
        
        if not admin_coworking.is_superuser:
            print("UWAGA: Nie jest super userem - naprawiam...")
            admin_coworking.is_superuser = True
            admin_coworking.is_staff = True
            admin_coworking.save()
            print("OK Naprawiono!")
            
    except User.DoesNotExist:
        print("ERROR admin@coworking.com nie istnieje")
    
    # Sprawdz admin@example.com
    print("\n=== SPRAWDZANIE admin@example.com ===")
    try:
        admin_example = User.objects.get(email='admin@example.com')
        print("OK admin@example.com istnieje!")
        print(f"Super user: {admin_example.is_superuser}")
        print(f"Staff: {admin_example.is_staff}")
        print(f"Active: {admin_example.is_active}")
    except User.DoesNotExist:
        print("ERROR admin@example.com nie istnieje")

if __name__ == '__main__':
    check_all_admins()
