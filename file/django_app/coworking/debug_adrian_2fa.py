#!/usr/bin/env python
"""
Debug 2FA dla adrian4321@onet.pl
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from django.contrib.auth import get_user_model
from django_otp.plugins.otp_email.models import EmailDevice
from django.test import Client
import json

User = get_user_model()

def debug_adrian_2fa():
    """Debug 2FA dla adrian4321@onet.pl"""
    
    print("=== DEBUG ADRIAN 2FA ===")
    
    email = 'adrian4321@onet.pl'
    password = 'adrian123'
    
    print(f"Email: {email}")
    print(f"Password: {password}")
    
    # Sprawdź użytkownika
    try:
        user = User.objects.get(email=email)
        print(f"\nUser found: {user.email}")
        print(f"Active: {user.is_active}")
        print(f"Has usable password: {user.has_usable_password()}")
        
        # Sprawdź hasło
        if user.check_password(password):
            print("Password check: OK")
        else:
            print("Password check: FAILED")
            return
            
    except User.DoesNotExist:
        print(f"ERROR: User {email} not found!")
        return
    
    # Sprawdź EmailDevice
    print(f"\n=== EMAIL DEVICES ===")
    devices = EmailDevice.objects.filter(user=user)
    print(f"Total devices: {devices.count()}")
    
    for device in devices:
        print(f"  - ID: {device.id}")
        print(f"  - Name: {device.name}")
        print(f"  - Email: {device.email}")
        print(f"  - Confirmed: {device.confirmed}")
        print(f"  - Created: {device.created_at}")
        print(f"  - Last used: {device.last_used_at}")
    
    # Sprawdź confirmed devices
    confirmed_devices = EmailDevice.objects.filter(user=user, confirmed=True)
    print(f"\nConfirmed devices: {confirmed_devices.count()}")
    
    if confirmed_devices.exists():
        print("User has 2FA enabled!")
    else:
        print("User does NOT have 2FA enabled!")
        
        # Włącz 2FA
        print("\nEnabling 2FA...")
        device, created = EmailDevice.objects.get_or_create(
            user=user,
            name='Email 2FA',
            defaults={
                'email': user.email,
                'confirmed': True
            }
        )
        
        if created:
            print("Created new EmailDevice")
        else:
            device.confirmed = True
            device.save()
            print("Updated existing EmailDevice")
    
    # Test API
    print(f"\n=== TESTING API ===")
    client = Client()
    
    response = client.post('/api/auth/login-2fa', {
        'email': email,
        'password': password
    }, content_type='application/json')
    
    print(f"API Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"API Response: {json.dumps(data, indent=2)}")
        
        requires_2fa = data.get('requires_2fa', False)
        print(f"\nRequires 2FA: {requires_2fa}")
        
        if requires_2fa:
            print("OK: 2FA is working!")
        else:
            print("ERROR: 2FA is NOT working!")
            
            # Sprawdź dlaczego
            print("\nDebugging why 2FA is not working...")
            confirmed_devices = EmailDevice.objects.filter(user=user, confirmed=True)
            print(f"Confirmed devices after API call: {confirmed_devices.count()}")
            
            for device in confirmed_devices:
                print(f"  - Device: {device.name} (confirmed={device.confirmed})")
    else:
        print(f"API Error: {response.content.decode()}")
    
    # Test authentication
    print(f"\n=== TESTING AUTHENTICATION ===")
    from django.contrib.auth import authenticate
    auth_user = authenticate(email=email, password=password)
    
    if auth_user:
        print(f"Authentication works: {auth_user.email}")
        
        # Sprawdź czy ma 2FA
        has_2fa = EmailDevice.objects.filter(user=auth_user, confirmed=True).exists()
        print(f"Authenticated user has 2FA: {has_2fa}")
        
        if has_2fa:
            print("WARNING: User has 2FA but authentication bypassed it!")
        else:
            print("OK: User has no 2FA")
    else:
        print("Authentication failed!")

if __name__ == '__main__':
    debug_adrian_2fa()



