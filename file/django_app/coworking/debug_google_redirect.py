#!/usr/bin/env python
"""
Debug Google redirect problem
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from django.test import Client
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.provider import GoogleProvider
from django.contrib.sites.models import Site

def debug_google_redirect():
    """Debug Google redirect problem"""
    
    print("=== DEBUG GOOGLE REDIRECT ===")
    
    # Sprawdź konfigurację
    try:
        social_app = SocialApp.objects.get(provider=GoogleProvider.id)
        print(f"Social App: {social_app.name}")
        print(f"Provider: {social_app.provider}")
        print(f"Client ID: {social_app.client_id[:30]}...")
        print(f"Secret: {social_app.secret[:10]}...")
        print(f"Sites: {[site.domain for site in social_app.sites.all()]}")
        
        # Sprawdź czy site jest poprawny
        site = Site.objects.get(id=1)
        print(f"Site: {site.domain}")
        
    except SocialApp.DoesNotExist:
        print("ERROR Brak Social App dla Google")
        return
    
    # Test bezpośredniego URL
    client = Client()
    
    print("\n=== TEST URL ===")
    
    # Test 1: Sprawdź czy URL działa
    response = client.get('/accounts/google/login/')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("ERROR: Zwraca 200 zamiast przekierowania!")
        print("To oznacza, że Django renderuje szablon zamiast przekierowywać")
        
        # Sprawdź czy to domyślny szablon allauth
        content = response.content.decode()
        if 'allauth' in content.lower():
            print("INFO: To wygląda na domyślny szablon allauth")
        else:
            print("INFO: To wygląda na niestandardowy szablon")
            
    elif response.status_code == 302:
        print(f"OK: Przekierowanie do: {response.url}")
        if 'google' in response.url:
            print("OK: Przekierowanie do Google!")
        else:
            print("ERROR: Przekierowanie nie do Google!")
    else:
        print(f"ERROR: Nieoczekiwany status: {response.status_code}")
    
    # Test 2: Sprawdź czy problem jest w konfiguracji
    print("\n=== SPRAWDZANIE KONFIGURACJI ===")
    
    # Sprawdź czy Google OAuth jest włączony
    from django.conf import settings
    print(f"INSTALLED_APPS zawiera allauth: {'allauth' in settings.INSTALLED_APPS}")
    print(f"INSTALLED_APPS zawiera google provider: {'allauth.socialaccount.providers.google' in settings.INSTALLED_APPS}")
    print(f"SITE_ID: {settings.SITE_ID}")
    
    # Sprawdź czy są ustawienia SOCIALACCOUNT
    if hasattr(settings, 'SOCIALACCOUNT_PROVIDERS'):
        print(f"SOCIALACCOUNT_PROVIDERS: {settings.SOCIALACCOUNT_PROVIDERS}")
    else:
        print("ERROR: Brak SOCIALACCOUNT_PROVIDERS w settings")

if __name__ == '__main__':
    debug_google_redirect()



