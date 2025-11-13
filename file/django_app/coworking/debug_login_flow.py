#!/usr/bin/env python
"""
Debug login flow - sprawdź co się dzieje przy logowaniu
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
import json

User = get_user_model()

def debug_login_flow():
    """Debug login flow"""
    
    print("=== DEBUG LOGIN FLOW ===")
    
    client = Client()
    email = 'adrian4321@onet.pl'
    password = 'adrian123'
    
    print(f"Testing login for: {email}")
    
    # Test 1: Sprawdź czy użytkownik ma 2FA
    print("\n1. Sprawdzanie 2FA status...")
    from django_otp.plugins.otp_email.models import EmailDevice
    user = User.objects.get(email=email)
    has_2fa = EmailDevice.objects.filter(user=user, confirmed=True).exists()
    print(f"User has 2FA: {has_2fa}")
    
    if has_2fa:
        devices = EmailDevice.objects.filter(user=user, confirmed=True)
        for device in devices:
            print(f"  - Device: {device.name} ({device.email})")
    
    # Test 2: Test API endpoint
    print("\n2. Testing API endpoint...")
    response = client.post('/api/auth/login-2fa', {
        'email': email,
        'password': password
    }, content_type='application/json')
    
    print(f"API Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"API Response: {json.dumps(data, indent=2)}")
        
        if data.get('requires_2fa'):
            print("OK: API zwraca requires_2fa=true")
        else:
            print("ERROR: API zwraca requires_2fa=false")
    else:
        print(f"API Error: {response.content.decode()}")
    
    # Test 3: Test Django's built-in login
    print("\n3. Testing Django's built-in login...")
    response = client.post('/accounts/login/', {
        'login': email,
        'password': password
    })
    
    print(f"Django Login Status: {response.status_code}")
    if response.status_code == 302:
        print("Django Login: Redirect (success)")
        print(f"Redirect URL: {response.url}")
    else:
        print(f"Django Login: {response.status_code}")
    
    # Test 4: Test czy użytkownik może się zalogować przez Django
    print("\n4. Testing Django authentication...")
    from django.contrib.auth import authenticate, login
    user = authenticate(email=email, password=password)
    
    if user:
        print(f"OK: Django authentication works for {user.email}")
        
        # Sprawdź czy ma 2FA
        has_2fa = EmailDevice.objects.filter(user=user, confirmed=True).exists()
        print(f"User has 2FA: {has_2fa}")
        
        if has_2fa:
            print("WARNING: User has 2FA but Django authentication bypassed it!")
        else:
            print("OK: User has no 2FA")
    else:
        print("ERROR: Django authentication failed")

if __name__ == '__main__':
    debug_login_flow()



