#!/usr/bin/env python
"""
Debug template rendering
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

from django.template.loader import get_template
from django.http import HttpRequest
from django.contrib.auth import get_user_model

User = get_user_model()

def debug_template():
    """Debug template rendering"""
    
    print("Test szablonów...")
    
    # Test czy szablon istnieje
    template_paths = [
        'account/profile.html',
        'profile/index.html', 
        'profile.html'
    ]
    
    for template_path in template_paths:
        try:
            template = get_template(template_path)
            print(f"OK Szablon {template_path} istnieje")
        except Exception as e:
            print(f"ERROR Szablon {template_path} nie istnieje: {e}")
    
    # Test renderowania
    try:
        template = get_template('account/profile.html')
        request = HttpRequest()
        request.user = User.objects.first()
        context = {'user': request.user}
        content = template.render(context, request)
        print(f"OK Szablon renderuje się poprawnie (długość: {len(content)} znaków)")
    except Exception as e:
        print(f"ERROR Błąd renderowania: {e}")

if __name__ == '__main__':
    debug_template()



