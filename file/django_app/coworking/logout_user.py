#!/usr/bin/env python
"""
Wyloguj użytkownika adrian4321@onet.pl
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session

User = get_user_model()

def logout_user():
    """Wyloguj użytkownika adrian4321@onet.pl"""
    
    print("=== WYLOGOWYWANIE UŻYTKOWNIKA ===")
    
    email = 'adrian4321@onet.pl'
    
    try:
        user = User.objects.get(email=email)
        print(f"User found: {user.email}")
        
        # Usuń wszystkie sesje dla tego użytkownika
        sessions = Session.objects.all()
        deleted_sessions = 0
        
        for session in sessions:
            try:
                session_data = session.get_decoded()
                if 'pending_user_id' in session_data:
                    if session_data['pending_user_id'] == user.id:
                        session.delete()
                        deleted_sessions += 1
                        print(f"Deleted pending session: {session.session_key}")
                elif '_auth_user_id' in session_data:
                    if session_data['_auth_user_id'] == str(user.id):
                        session.delete()
                        deleted_sessions += 1
                        print(f"Deleted user session: {session.session_key}")
            except Exception as e:
                # Ignore corrupted sessions
                pass
        
        print(f"Deleted {deleted_sessions} sessions")
        
        if deleted_sessions > 0:
            print("OK: User logged out successfully")
        else:
            print("INFO: No active sessions found")
        
        print("\nNow try logging in again:")
        print("1. Go to: http://127.0.0.1:8000/login")
        print("2. Enter: adrian4321@onet.pl / adrian123")
        print("3. You should see 2FA section!")
        
    except User.DoesNotExist:
        print(f"ERROR: User {email} not found!")

if __name__ == '__main__':
    logout_user()



