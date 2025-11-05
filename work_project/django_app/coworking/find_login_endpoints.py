#!/usr/bin/env python
"""
Znajdź wszystkie endpointy logowania
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.conf import settings
import json

def find_login_endpoints():
    """Znajdź wszystkie endpointy logowania"""
    
    print("=== WSZYSTKIE ENDPOINTY LOGOWANIA ===")
    
    client = Client()
    email = 'adrian4321@onet.pl'
    password = 'adrian123'
    
    # Lista wszystkich możliwych endpointów logowania
    login_endpoints = [
        '/login',
        '/accounts/login/',
        '/admin/login/',
        '/api/auth/login/',
        '/api/auth/login-2fa',
        '/accounts/signup/',
        '/register',
        '/signup',
    ]
    
    print(f"Testing login endpoints for: {email}")
    
    for endpoint in login_endpoints:
        print(f"\n--- Testing {endpoint} ---")
        
        # Test GET
        try:
            response = client.get(endpoint)
            print(f"GET {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                content = response.content.decode()
                
                # Sprawdź czy to strona logowania
                if 'email' in content.lower() and 'password' in content.lower():
                    print("  -> Login page detected")
                elif 'login' in content.lower():
                    print("  -> Contains 'login'")
                else:
                    print("  -> Not a login page")
            
        except Exception as e:
            print(f"GET {endpoint}: ERROR - {e}")
        
        # Test POST (jeśli to endpoint logowania)
        if 'login' in endpoint:
            try:
                response = client.post(endpoint, {
                    'email': email,
                    'password': password,
                    'login': email,  # dla allauth
                    'username': email,  # dla standardowego Django
                })
                print(f"POST {endpoint}: {response.status_code}")
                
                if response.status_code == 302:
                    print(f"  -> Redirect to: {response.url}")
                elif response.status_code == 200:
                    print("  -> Returns 200 (might be success)")
                else:
                    print(f"  -> Error: {response.status_code}")
                    
            except Exception as e:
                print(f"POST {endpoint}: ERROR - {e}")
    
    # Sprawdź wszystkie URL patterns
    print(f"\n=== URL PATTERNS ===")
    from django.urls import get_resolver
    resolver = get_resolver()
    
    def print_urls(patterns, prefix=''):
        for pattern in patterns:
            if hasattr(pattern, 'url_patterns'):
                print_urls(pattern.url_patterns, prefix + str(pattern.pattern))
            else:
                url = prefix + str(pattern.pattern)
                if 'login' in url.lower() or 'auth' in url.lower():
                    print(f"  {url} -> {pattern.name}")
    
    print_urls(resolver.url_patterns)
    
    # Sprawdź czy użytkownik jest zalogowany
    print(f"\n=== CHECK LOGIN STATUS ===")
    response = client.get('/dashboard')
    print(f"Dashboard access: {response.status_code}")
    
    if response.status_code == 200:
        print("WARNING: User is logged in!")
        
        # Sprawdź sesję
        session_key = client.cookies.get('sessionid')
        if session_key:
            print(f"Session: {session_key.value[:20]}...")
        else:
            print("No session cookie")
    else:
        print("User is not logged in")

if __name__ == '__main__':
    find_login_endpoints()



