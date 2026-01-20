#!/usr/bin/env python3
"""
Get JWT Token for API Testing
"""

import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from authentication.models import User

# Try to get or create test user
try:
    user = User.objects.get(email='testuser@example.com')
    print(f"✅ Found existing test user: {user.email}")
except User.DoesNotExist:
    user = User.objects.create_user(email='testuser@example.com', password='testpass123', first_name='Test', last_name='User')
    print(f"✅ Created test user: {user.email}")

# Generate tokens
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)
refresh_token = str(refresh)

print(f"\n🔐 JWT Tokens Generated:")
print(f"\n📝 Access Token (use in Authorization header):")
print(f"   {access_token}")
print(f"\n📝 Refresh Token:")
print(f"   {refresh_token}")

print(f"\n💡 Usage Example:")
print(f"   python3 generate_pdf_with_token.py aae65358-f709-4994-ab28-f4e2874c35e3 '{access_token}'")
