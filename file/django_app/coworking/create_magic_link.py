#!/usr/bin/env python
"""
Create a real magic link for testing in browser
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.magic_link import MagicLinkService

User = get_user_model()

def create_real_magic_link():
    """Create a real magic link for browser testing"""
    
    print("=== CREATE REAL MAGIC LINK ===")
    
    email = 'test@example.com'
    
    # Get or create user
    try:
        user = User.objects.get(email=email)
        print(f"User found: {user.email}")
    except User.DoesNotExist:
        user = User.objects.create_user(email=email, full_name='Test User')
        print(f"User created: {user.email}")
    
    # Create magic link
    magic_link = MagicLinkService.create_magic_link(user)
    
    # Build the real URL
    magic_url = f"http://127.0.0.1:8000/api/auth/magic-link/{magic_link.token}/"
    
    print(f"\nMAGIC LINK CREATED:")
    print(f"Token: {magic_link.token}")
    print(f"Expires: {magic_link.expires_at}")
    
    print(f"\nREAL MAGIC LINK URL:")
    print(f"{magic_url}")
    
    print(f"\nINSTRUCTIONS:")
    print(f"1. Copy the URL above")
    print(f"2. Paste it in your browser")
    print(f"3. Press Enter")
    print(f"4. You will be automatically logged in!")
    
    print(f"\nNOTE: This link expires in 15 minutes")
    
    return magic_url

if __name__ == '__main__':
    create_real_magic_link()



