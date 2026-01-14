#!/usr/bin/env python
"""
Ustaw hasło dla użytkownika adrian4321@onet.pl
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def fix_user_password():
    """Ustaw hasło dla adrian4321@onet.pl"""
    
    print("=== USTAWIANIE HASŁA ===")
    
    email = 'adrian4321@onet.pl'
    
    try:
        user = User.objects.get(email=email)
        print(f"Użytkownik: {user.email}")
        
        # Sprawdź czy ma hasło
        if user.has_usable_password():
            print("OK: Użytkownik ma hasło")
        else:
            print("ERROR: Użytkownik nie ma hasła!")
        
        # Ustaw nowe hasło
        user.set_password('adrian123')
        user.save()
        print("OK: Ustawiono hasło: adrian123")
        
        print("\n=== DANE LOGOWANIA ===")
        print("Email: adrian4321@onet.pl")
        print("Hasło: adrian123")
        print("2FA: WŁĄCZONE")
        
        print("\n=== INSTRUKCJE ===")
        print("1. Idź na: http://127.0.0.1:8000/login")
        print("2. Wprowadź email i hasło")
        print("3. Sprawdź terminal - zobaczysz email z kodem 2FA")
        print("4. Wprowadź kod i zaloguj się")
        
    except User.DoesNotExist:
        print(f"ERROR: Użytkownik {email} nie istnieje!")

if __name__ == '__main__':
    fix_user_password()



