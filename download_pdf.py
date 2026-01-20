#!/usr/bin/env python3
import os
import django
import requests

os.environ['DJANGO_SETTINGS_MODULE'] = 'clm_backend.settings'
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

# Get user and token
User = get_user_model()
user = User.objects.filter(email='e2e-workflow@example.com').first()

if not user:
    print("❌ User not found")
    exit(1)

token = str(RefreshToken.for_user(user).access_token)
contract_id = 'aae65358-f709-4994-ab28-f4e2874c35e3'

# Download PDF
url = f"http://localhost:11000/api/esign/executed/{contract_id}/"
headers = {"Authorization": f"Bearer {token}"}

print(f"Downloading from: {url}")
response = requests.get(url, headers=headers, timeout=10)

print(f"Status Code: {response.status_code}")
print(f"Content-Type: {response.headers.get('content-type')}")
print(f"Content Size: {len(response.content)} bytes")

if response.status_code == 200:
    if response.headers.get('content-type', '').startswith('application/pdf'):
        with open('signed_nda.pdf', 'wb') as f:
            f.write(response.content)
        print("✅ PDF Downloaded Successfully to: signed_nda.pdf")
    else:
        print(f"❌ Wrong content type. Response: {response.text[:100]}")
else:
    print(f"❌ Error: {response.text}")
