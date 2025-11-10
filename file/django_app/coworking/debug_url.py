#!/usr/bin/env python
"""
Debug URL routing
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking.settings')
django.setup()

def debug_url_key():
    """Debug jak wygląda klucz URL"""
    
    test_urls = [
        '/accounts/profile/',
        '/accounts/profile',
        '/profile/',
        '/profile'
    ]
    
    for url in test_urls:
        tpl_path = url.strip('/')
        key = tpl_path.replace(' ', '').lower()
        print(f"URL: {url}")
        print(f"tpl_path: '{tpl_path}'")
        print(f"key: '{key}'")
        print(f"key in {{'profile', 'accounts/profile'}}: {key in {'profile', 'accounts/profile'}}")
        print("-" * 40)

if __name__ == '__main__':
    debug_url_key()



