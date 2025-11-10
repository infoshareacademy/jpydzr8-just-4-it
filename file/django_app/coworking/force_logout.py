#!/usr/bin/env python
"""
Wymuś wylogowanie wszystkich użytkowników
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model

User = get_user_model()

def force_logout():
    """Wymuś wylogowanie wszystkich użytkowników"""
    
    print("=== WYMUSZANIE WYLOGOWANIA ===")
    
    # Usuń wszystkie sesje
    sessions = Session.objects.all()
    total_sessions = sessions.count()
    
    print(f"Total sessions: {total_sessions}")
    
    deleted_count = 0
    for session in sessions:
        try:
            session_data = session.get_decoded()
            
            # Sprawdź czy sesja zawiera dane logowania
            if '_auth_user_id' in session_data or 'pending_user_id' in session_data:
                print(f"Deleting session: {session.session_key[:20]}...")
                session.delete()
                deleted_count += 1
        except Exception as e:
            # Ignore corrupted sessions
            pass
    
    print(f"Deleted {deleted_count} active sessions")
    
    # Usuń wszystkie sesje (nuclear option)
    print("\nNuclear option: Deleting ALL sessions...")
    Session.objects.all().delete()
    print("All sessions deleted!")
    
    print("\nNow try logging in again:")
    print("1. Go to: http://127.0.0.1:8000/login")
    print("2. Enter: adrian4321@onet.pl / adrian123")
    print("3. You should see 2FA section!")

if __name__ == '__main__':
    force_logout()



