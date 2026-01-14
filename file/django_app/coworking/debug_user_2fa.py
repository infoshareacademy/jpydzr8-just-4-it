#!/usr/bin/env python
"""
Debug 2FA dla konkretnego użytkownika
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from django.contrib.auth import get_user_model
from django_otp.models import Device
from django_otp.plugins.otp_email.models import EmailDevice

User = get_user_model()

def debug_user_2fa():
    """Debug 2FA dla adrian4321@onet.pl"""
    
    print("=== DEBUG 2FA DLA UZYTKOWNIKA ===")
    
    email = 'adrian4321@onet.pl'
    
    try:
        user = User.objects.get(email=email)
        print(f"Uzytkownik: {user.email}")
        print(f"Active: {user.is_active}")
        print(f"Staff: {user.is_staff}")
        print(f"Superuser: {user.is_superuser}")
        
        # Sprawdź EmailDevice
        print(f"\n=== EMAIL DEVICES ===")
        email_devices = EmailDevice.objects.filter(user=user)
        print(f"Liczba Email Devices: {email_devices.count()}")
        
        for device in email_devices:
            print(f"  - ID: {device.id}")
            print(f"  - Name: {device.name}")
            print(f"  - Email: {device.email}")
            print(f"  - Confirmed: {device.confirmed}")
            print(f"  - Created: {device.created_at}")
            print(f"  - Last used: {device.last_used_at}")
        
        # Sprawdź czy ma confirmed devices
        confirmed_devices = EmailDevice.objects.filter(user=user, confirmed=True)
        print(f"\nConfirmed devices: {confirmed_devices.count()}")
        
        if confirmed_devices.exists():
            print("OK: Uzytkownik ma wlaczone 2FA!")
            for device in confirmed_devices:
                print(f"  - Device: {device.name} ({device.email})")
        else:
            print("ERROR: Uzytkownik nie ma wlaczonego 2FA!")
            
            # Sprawdź czy ma niewlaczone devices
            unconfirmed_devices = EmailDevice.objects.filter(user=user, confirmed=False)
            if unconfirmed_devices.exists():
                print("INFO: Ma niewlaczone devices:")
                for device in unconfirmed_devices:
                    print(f"  - Device: {device.name} (confirmed=False)")
            
            print("\n=== WLACZANIE 2FA ===")
            # Wlacz 2FA
            device, created = EmailDevice.objects.get_or_create(
                user=user,
                name='Email 2FA',
                defaults={
                    'email': user.email,
                    'confirmed': True
                }
            )
            
            if created:
                print(f"OK: Utworzono Email Device dla {user.email}")
            else:
                device.confirmed = True
                device.save()
                print(f"OK: Wlaczono Email Device dla {user.email}")
        
        # Test logowania
        print(f"\n=== TEST LOGOWANIA ===")
        from django.test import Client
        client = Client()
        
        # Sprawdź czy ma hasło
        if user.has_usable_password():
            print("OK: Uzytkownik ma hasło")
        else:
            print("ERROR: Uzytkownik nie ma hasła!")
            user.set_password('test123')
            user.save()
            print("OK: Ustawiono hasło: test123")
        
        # Test API
        response = client.post('/api/auth/login-2fa', {
            'email': user.email,
            'password': 'test123'
        }, content_type='application/json')
        
        print(f"API Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Requires 2FA: {data.get('requires_2fa', 'N/A')}")
            if data.get('requires_2fa'):
                print("OK: 2FA dziala!")
            else:
                print("ERROR: 2FA nie dziala - loguje bez kodu!")
        else:
            print(f"Error: {response.content.decode()}")
            
    except User.DoesNotExist:
        print(f"ERROR: Uzytkownik {email} nie istnieje!")
        
        # Sprawdź wszystkich uzytkownikow
        print("\n=== WSZYSCY UZYTKOWNICY ===")
        all_users = User.objects.all()
        for u in all_users:
            print(f"  - {u.email}")

if __name__ == '__main__':
    debug_user_2fa()



