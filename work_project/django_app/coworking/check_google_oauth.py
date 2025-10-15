#!/usr/bin/env python
"""
Sprawdza konfigurację Google OAuth
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.provider import GoogleProvider

def check_google_oauth():
    """Sprawdza konfigurację Google OAuth"""
    
    print("=== SPRAWDZANIE GOOGLE OAUTH ===")
    
    try:
        social_app = SocialApp.objects.get(provider=GoogleProvider.id)
        print(f"Google Social App znaleziony:")
        print(f"  Provider: {social_app.provider}")
        print(f"  Name: {social_app.name}")
        print(f"  Client ID: {social_app.client_id}")
        print(f"  Secret: {social_app.secret}")
        print(f"  Sites: {[site.domain for site in social_app.sites.all()]}")
        
        # Sprawdź czy to placeholder wartości
        if social_app.client_id == '123456789.apps.googleusercontent.com':
            print("\n⚠️  UWAGA: To są placeholder wartości!")
            print("Aby Google Login działał, musisz skonfigurować prawdziwe klucze.")
            print("Przejdź do: http://127.0.0.1:8000/admin/socialaccount/socialapp/")
        elif 'placeholder' in social_app.client_id.lower():
            print("\n⚠️  UWAGA: To są placeholder wartości!")
            print("Aby Google Login działał, musisz skonfigurować prawdziwe klucze.")
        else:
            print("\nOK Konfiguracja wyglada na prawdziwa")
            
    except SocialApp.DoesNotExist:
        print("ERROR Google Social App nie istnieje!")
        print("Utworze podstawowa konfiguracje...")
        
        # Utwórz podstawową konfigurację
        from django.contrib.sites.models import Site
        site = Site.objects.get(id=1)
        
        social_app = SocialApp.objects.create(
            provider=GoogleProvider.id,
            name='Google',
            client_id='123456789.apps.googleusercontent.com',
            secret='GOCSPX-placeholder_secret_key_here',
        )
        social_app.sites.add(site)
        
        print("OK Utworzono podstawowa konfiguracje z placeholder wartosciami")

if __name__ == '__main__':
    check_google_oauth()
