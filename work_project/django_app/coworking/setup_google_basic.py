#!/usr/bin/env python
"""
Podstawowa konfiguracja Google OAuth z placeholder wartościami
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

def setup_basic_google_oauth():
    """Konfiguruje podstawowy Google OAuth z placeholder wartościami"""
    
    print("Konfiguracja podstawowego Google OAuth...")
    
    # Ustaw domenę dla development
    site, created = Site.objects.get_or_create(
        id=1,
        defaults={
            'domain': '127.0.0.1:8000',
            'name': 'Coworking App (Development)'
        }
    )
    
    if not created:
        site.domain = '127.0.0.1:8000'
        site.name = 'Coworking App (Development)'
        site.save()
    
    print(f"Site: {site.domain}")
    
    # Utwórz Google Social App z placeholder wartościami
    social_app, created = SocialApp.objects.get_or_create(
        provider=GoogleProvider.id,
        defaults={
            'name': 'Google',
            'client_id': 'PLACEHOLDER_CLIENT_ID',
            'secret': 'PLACEHOLDER_CLIENT_SECRET',
        }
    )
    
    if not created:
        social_app.client_id = 'PLACEHOLDER_CLIENT_ID'
        social_app.secret = 'PLACEHOLDER_CLIENT_SECRET'
        social_app.save()
    
    # Dodaj site do social app
    if site not in social_app.sites.all():
        social_app.sites.add(site)
    
    print("Google OAuth skonfigurowany z placeholder wartościami!")
    print(f"Provider: {social_app.provider}")
    print(f"Client ID: {social_app.client_id}")
    print(f"Secret: {social_app.secret}")
    print(f"Sites: {[site.domain for site in social_app.sites.all()]}")
    
    print("\n" + "="*60)
    print("UWAGA: To są placeholder wartości!")
    print("Aby Google Login działał, musisz:")
    print("1. Przejść do https://console.cloud.google.com/")
    print("2. Utworzyć projekt")
    print("3. Włączyć Google+ API")
    print("4. Utworzyć OAuth 2.0 Client ID")
    print("5. Dodać redirect URI: http://127.0.0.1:8000/accounts/google/login/callback/")
    print("6. Zastąpić placeholder wartości w Django Admin:")
    print("   http://127.0.0.1:8000/admin/socialaccount/socialapp/")
    print("="*60)
    
    return True

if __name__ == '__main__':
    setup_basic_google_oauth()



