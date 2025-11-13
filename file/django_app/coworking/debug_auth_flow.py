#!/usr/bin/env python
"""
Debug autoryzacji - sprawdź jak użytkownik się loguje
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.sessions.models import Session
import json

User = get_user_model()

def debug_auth_flow():
    """Debug autoryzacji"""
    
    print("=== DEBUG AUTORYZACJI ===")
    
    email = 'adrian4321@onet.pl'
    password = 'adrian123'
    
    print(f"Testing authentication for: {email}")
    
    # Test 1: Sprawdź czy użytkownik ma 2FA
    print("\n1. Sprawdzanie 2FA...")
    from django_otp.plugins.otp_email.models import EmailDevice
    user = User.objects.get(email=email)
    has_2fa = EmailDevice.objects.filter(user=user, confirmed=True).exists()
    print(f"User has 2FA: {has_2fa}")
    
    # Test 2: Test Django authentication (bez 2FA)
    print("\n2. Test Django authentication...")
    auth_user = authenticate(email=email, password=password)
    
    if auth_user:
        print(f"OK: Django authentication works: {auth_user.email}")
        print("WARNING: Django authentication bypasses 2FA!")
    else:
        print("ERROR: Django authentication failed")
    
    # Test 3: Test czy Django login() działa
    print("\n3. Test Django login()...")
    client = Client()
    
    # Symuluj Django login
    response = client.post('/accounts/login/', {
        'login': email,
        'password': password
    })
    
    print(f"Django login status: {response.status_code}")
    
    if response.status_code == 302:
        print(f"Redirect to: {response.url}")
        print("WARNING: Django login bypasses 2FA!")
    
    # Test 4: Sprawdź czy użytkownik jest zalogowany
    print("\n4. Check login status...")
    
    # Sprawdź sesję
    session_key = client.cookies.get('sessionid')
    if session_key:
        print(f"Session exists: {session_key.value[:20]}...")
        
        # Sprawdź co jest w sesji
        try:
            session = Session.objects.get(session_key=session_key.value)
            session_data = session.get_decoded()
            print(f"Session data: {session_data}")
            
            if '_auth_user_id' in session_data:
                user_id = session_data['_auth_user_id']
                print(f"Logged in user ID: {user_id}")
                
                if user_id == str(user.id):
                    print("WARNING: User is logged in via Django auth!")
                else:
                    print("Different user logged in")
            
            if 'pending_user_id' in session_data:
                pending_id = session_data['pending_user_id']
                print(f"Pending user ID: {pending_id}")
                
                if pending_id == user.id:
                    print("User is pending 2FA verification")
                else:
                    print("Different user pending")
                    
        except Session.DoesNotExist:
            print("Session not found in database")
    else:
        print("No session found")
    
    # Test 5: Test dashboard access
    print("\n5. Test dashboard access...")
    response = client.get('/dashboard')
    print(f"Dashboard status: {response.status_code}")
    
    if response.status_code == 200:
        print("OK: Can access dashboard (logged in)")
    elif response.status_code == 302:
        print(f"Redirect to: {response.url} (not logged in)")
    else:
        print(f"Dashboard error: {response.status_code}")
    
    # Test 6: Sprawdź czy formularz HTML używa Django login
    print("\n6. Check HTML form...")
    response = client.get('/login')
    
    if response.status_code == 200:
        content = response.content.decode()
        
        # Sprawdź czy formularz ma action
        if 'action=' in content:
            print("Form has action attribute")
        else:
            print("Form has no action (uses JavaScript)")
        
        # Sprawdź czy używa Django login
        if 'accounts/login/' in content:
            print("WARNING: Form uses Django login!")
        else:
            print("Form uses custom JavaScript API")
        
        # Sprawdź czy ma JavaScript
        if 'login-2fa' in content:
            print("OK: Contains login-2fa API call")
        else:
            print("ERROR: Missing login-2fa API call")

if __name__ == '__main__':
    debug_auth_flow()



