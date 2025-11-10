#!/usr/bin/env python
"""
Debug wszystkich metod autoryzacji
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

def debug_all_auth_methods():
    """Debug wszystkich metod autoryzacji"""
    
    print("=== DEBUG WSZYSTKICH METOD AUTORYZACJI ===")
    
    email = 'adrian4321@onet.pl'
    password = 'adrian123'
    
    print(f"Testing authentication for: {email}")
    
    # Test 1: Sprawdź czy użytkownik ma 2FA
    print("\n1. Sprawdzanie 2FA...")
    from django_otp.plugins.otp_email.models import EmailDevice
    user = User.objects.get(email=email)
    has_2fa = EmailDevice.objects.filter(user=user, confirmed=True).exists()
    print(f"User has 2FA: {has_2fa}")
    
    # Test 2: Sprawdź wszystkie authentication backends
    print("\n2. Sprawdzanie authentication backends...")
    from django.conf import settings
    print(f"Authentication backends: {settings.AUTHENTICATION_BACKENDS}")
    
    # Test 3: Test każdego backend osobno
    print("\n3. Test każdego backend...")
    
    # Backend 1: EmailBackend
    print("\n3.1. Testing EmailBackend...")
    from api.backends import EmailBackend
    backend = EmailBackend()
    auth_user = backend.authenticate(email=email, password=password)
    
    if auth_user:
        print(f"EmailBackend: OK - {auth_user.email}")
    else:
        print("EmailBackend: FAILED")
    
    # Backend 2: ModelBackend
    print("\n3.2. Testing ModelBackend...")
    from django.contrib.auth.backends import ModelBackend
    backend = ModelBackend()
    auth_user = backend.authenticate(username=email, password=password)
    
    if auth_user:
        print(f"ModelBackend: OK - {auth_user.email}")
    else:
        print("ModelBackend: FAILED")
    
    # Backend 3: allauth
    print("\n3.3. Testing allauth backend...")
    from allauth.account.auth_backends import AuthenticationBackend
    backend = AuthenticationBackend()
    auth_user = backend.authenticate(email=email, password=password)
    
    if auth_user:
        print(f"allauth backend: OK - {auth_user.email}")
    else:
        print("allauth backend: FAILED")
    
    # Test 4: Test Django authenticate() (używa wszystkich backendów)
    print("\n4. Test Django authenticate()...")
    auth_user = authenticate(email=email, password=password)
    
    if auth_user:
        print(f"Django authenticate: OK - {auth_user.email}")
        print("WARNING: Django authenticate bypasses 2FA!")
    else:
        print("Django authenticate: FAILED")
    
    # Test 5: Test czy użytkownik może się zalogować przez Django login()
    print("\n5. Test Django login()...")
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
    
    # Test 6: Sprawdź czy użytkownik jest zalogowany
    print("\n6. Check login status...")
    
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
    
    # Test 7: Test dashboard access
    print("\n7. Test dashboard access...")
    response = client.get('/dashboard')
    print(f"Dashboard status: {response.status_code}")
    
    if response.status_code == 200:
        print("OK: Can access dashboard (logged in)")
    elif response.status_code == 302:
        print(f"Redirect to: {response.url} (not logged in)")
    else:
        print(f"Dashboard error: {response.status_code}")
    
    # Test 8: Sprawdź czy formularz HTML używa Django login
    print("\n8. Check HTML form...")
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
    
    # Test 9: Sprawdź czy JavaScript działa
    print("\n9. Test JavaScript API...")
    response = client.post('/api/auth/login-2fa', {
        'email': email,
        'password': password
    }, content_type='application/json')
    
    print(f"JavaScript API status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"JavaScript API response: {json.dumps(data, indent=2)}")
        
        requires_2fa = data.get('requires_2fa', False)
        print(f"Requires 2FA: {requires_2fa}")
        
        if requires_2fa:
            print("OK: JavaScript API returns requires_2fa=true")
        else:
            print("ERROR: JavaScript API returns requires_2fa=false")
    else:
        print(f"JavaScript API error: {response.status_code}")
        print(f"Response: {response.content.decode()}")

if __name__ == '__main__':
    debug_all_auth_methods()



