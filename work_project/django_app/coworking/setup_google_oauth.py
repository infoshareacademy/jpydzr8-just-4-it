#!/usr/bin/env python
"""
Skrypt do automatycznej konfiguracji Google OAuth w Django
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

def setup_google_oauth():
    """Konfiguruje Google OAuth w Django"""
    
    # Pobierz dane z zmiennych środowiskowych
    client_id = os.getenv('GOOGLE_OAUTH2_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_OAUTH2_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Brak GOOGLE_OAUTH2_CLIENT_ID lub GOOGLE_OAUTH2_SECRET w zmiennych środowiskowych")
        print("📝 Ustaw te zmienne w pliku .env lub jako zmienne środowiskowe")
        return False
    
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
    
    # Utwórz lub zaktualizuj Google Social App
    social_app, created = SocialApp.objects.get_or_create(
        provider=GoogleProvider.id,
        defaults={
            'name': 'Google',
            'client_id': client_id,
            'secret': client_secret,
        }
    )
    
    if not created:
        social_app.client_id = client_id
        social_app.secret = client_secret
        social_app.save()
    
    # Dodaj site do social app
    if site not in social_app.sites.all():
        social_app.sites.add(site)
    
    print("Google OAuth skonfigurowany pomyślnie!")
    print(f"Domena: {site.domain}")
    print(f"Client ID: {client_id[:20]}...")
    print(f"Secret: {'*' * len(client_secret)}")
    print(f"Provider: {social_app.provider}")
    
    return True

def check_configuration():
    """Sprawdza konfigurację"""
    print("Sprawdzanie konfiguracji...")
    
    # Sprawdź zmienne środowiskowe
    client_id = os.getenv('GOOGLE_OAUTH2_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_OAUTH2_SECRET')
    
    print(f"GOOGLE_OAUTH2_CLIENT_ID: {'OK' if client_id else 'BRAK'}")
    print(f"GOOGLE_OAUTH2_SECRET: {'OK' if client_secret else 'BRAK'}")
    
    # Sprawdź Social App
    try:
        social_app = SocialApp.objects.get(provider=GoogleProvider.id)
        print(f"Google Social App: OK (ID: {social_app.id})")
        print(f"Sites: {[site.domain for site in social_app.sites.all()]}")
    except SocialApp.DoesNotExist:
        print("Google Social App: BRAK")
    
    return bool(client_id and client_secret)

if __name__ == '__main__':
    print("Konfiguracja Google OAuth dla Django")
    print("=" * 50)
    
    if check_configuration():
        setup_google_oauth()
    else:
        print("\nAby skonfigurować Google OAuth:")
        print("1. Przejdź do https://console.cloud.google.com/")
        print("2. Utwórz projekt lub wybierz istniejący")
        print("3. Włącz Google+ API")
        print("4. Utwórz OAuth 2.0 Client ID")
        print("5. Dodaj redirect URI: http://127.0.0.1:8000/accounts/google/login/callback/")
        print("6. Ustaw zmienne środowiskowe GOOGLE_OAUTH2_CLIENT_ID i GOOGLE_OAUTH2_SECRET")
        print("7. Uruchom ponownie ten skrypt")
    
    print("\nSerwer powinien być uruchomiony na: http://127.0.0.1:8000")
    print("Admin panel: http://127.0.0.1:8000/admin")
    print("Login: admin@example.com")
    print("Hasło: (nie ustawione - użyj Django shell do resetu)")
