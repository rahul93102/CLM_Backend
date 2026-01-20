#!/usr/bin/env python3
"""
QUICK TEST - Verify contract generation works (HTTP 201)
"""
import os
import sys
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def quick_test():
    """Quick verification that system works"""
    
    # Setup
    user, _ = User.objects.get_or_create(
        email='quick_test@example.com',
        defaults={'first_name': 'Quick', 'last_name': 'Test'}
    )
    token = str(RefreshToken.for_user(user).access_token)
    
    # Test 1: Get templates
    r = requests.get(
        'http://127.0.0.1:11000/api/v1/templates/',
        headers={'Authorization': f'Bearer {token}'}
    )
    print(f"✓ GET /templates/ → {r.status_code}")
    
    # Test 2: Create NDA (HTTP 201)
    r = requests.post(
        'http://127.0.0.1:11000/api/v1/create/',
        json={
            "contract_type": "nda",
            "data": {
                "date": "2026-01-20",
                "1st_party_name": "Company A",
                "2nd_party_name": "Company B",
                "agreement_type": "Mutual",
                "1st_party_relationship": "Vendor",
                "2nd_party_relationship": "Client",
                "governing_law": "NY",
                "1st_party_printed_name": "Alice",
                "2nd_party_printed_name": "Bob"
            }
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if r.status_code == 201:
        data = r.json()
        file_path = data.get('file_path', '')
        if os.path.exists(file_path):
            size = os.path.getsize(file_path) / 1024
            print(f"✓ POST /create/ → {r.status_code} ✓ PDF: {size:.0f} KB")
            return True
    
    print(f"✗ POST /create/ → {r.status_code}")
    return False

if __name__ == '__main__':
    success = quick_test()
    sys.exit(0 if success else 1)
