#!/usr/bin/env python
"""
Debug Google Login
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.provider import GoogleProvider

User = get_user_model()

def debug_google_login():
    """Debug Google Login"""
    
    print("=== DEBUG GOOGLE LOGIN ===")
    
    # Sprawdź konfigurację
    try:
        social_app = SocialApp.objects.get(provider=GoogleProvider.id)
        print(f"Social App: {social_app.name}")
        print(f"Client ID: {social_app.client_id[:20]}...")
        print(f"Secret: {social_app.secret[:10]}...")
        
        # Sprawdź czy Client ID wygląda na prawdziwy
        if social_app.client_id.endswith('.apps.googleusercontent.com'):
            print("OK Client ID ma prawidlowy format")
        else:
            print("ERROR Client ID ma nieprawidlowy format")
            
    except SocialApp.DoesNotExist:
        print("ERROR Brak Social App dla Google")
        return
    
    # Test bezpośredniego URL
    client = Client()
    
    print("\n=== TEST BEZPOŚREDNIEGO URL ===")
    
    # Test 1: Sprawdź czy URL działa
    response = client.get('/accounts/google/login/')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode()
        print(f"Content length: {len(content)}")
        
        # Sprawdź czy jest błąd w treści
        if 'error' in content.lower():
            print("ERROR Znaleziono blad w tresci")
            # Znajdź linię z błędem
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'error' in line.lower():
                    print(f"Line {i}: {line.strip()}")
        else:
            print("OK Brak bledow w tresci")
            
        # Sprawdź czy jest link do Google
        if 'google' in content.lower():
            print("OK Znaleziono Google w tresci")
        else:
            print("ERROR Brak Google w tresci")
            
        # Sprawdź czy jest formularz
        if '<form' in content:
            print("OK Znaleziono formularz")
        else:
            print("ERROR Brak formularza")
            
    elif response.status_code == 302:
        print(f"OK Przekierowanie do: {response.url}")
    else:
        print(f"ERROR Nieoczekiwany status: {response.status_code}")

if __name__ == '__main__':
    debug_google_login()
