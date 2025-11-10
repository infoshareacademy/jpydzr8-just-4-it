#!/usr/bin/env python
"""
Naprawa konfiguracji Google OAuth
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.provider import GoogleProvider

def fix_google_oauth():
    """Naprawia konfigurację Google OAuth"""
    
    print("Naprawianie konfiguracji Google OAuth...")
    
    # Usuń istniejące placeholder SocialApp
    SocialApp.objects.filter(provider=GoogleProvider.id).delete()
    print("Usunięto istniejące placeholder konfiguracje")
    
    # Utwórz nową konfigurację z prawidłowymi placeholder wartościami
    social_app = SocialApp.objects.create(
        provider=GoogleProvider.id,
        name='Google',
        client_id='123456789.apps.googleusercontent.com',  # Prawidłowy format
        secret='GOCSPX-placeholder_secret_key_here',
    )
    
    # Dodaj site
    site = Site.objects.get(id=1)
    social_app.sites.add(site)
    
    print("Google OAuth naprawiony!")
    print(f"Provider: {social_app.provider}")
    print(f"Client ID: {social_app.client_id}")
    print(f"Secret: {social_app.secret}")
    print(f"Sites: {[site.domain for site in social_app.sites.all()]}")
    
    print("\n" + "="*60)
    print("UWAGA: To nadal są placeholder wartości!")
    print("Aby Google Login działał, musisz:")
    print("1. Przejść do https://console.cloud.google.com/")
    print("2. Utworzyć prawdziwy OAuth 2.0 Client ID")
    print("3. Zaktualizować wartości w Django Admin:")
    print("   http://127.0.0.1:8000/admin/socialaccount/socialapp/")
    print("="*60)
    
    return True

if __name__ == '__main__':
    fix_google_oauth()



