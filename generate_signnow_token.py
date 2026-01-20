import os
import sys
import django
import requests
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.utils import timezone
from contracts.models import SignNowCredential

print("=" * 70)
print("SIGNNOW BASIC AUTH TOKEN GENERATION")
print("=" * 70)

# Get credential
cred = SignNowCredential.objects.first()
if not cred:
    print("❌ No SignNow credential found!")
    sys.exit(1)

print(f"\n✅ Found credential: {cred.id}")
print(f"   Client ID: {cred.client_id}")
print(f"   Client Secret: {cred.client_secret[:10]}...")

# SignNow Basic Auth Token API
# Docs: https://docs.signnow.com/reference/gettokenwithbasiccreds
SIGNNOW_TOKEN_URL = "https://api.signnow.com/oauth2/token"

print("\n" + "=" * 70)
print("TESTING BASIC AUTH (username + password)")
print("=" * 70)

# Get username and password from environment or ask user
username = "vishaljha2806@gmail.com"  # Default from context
password_input = input("\nEnter SignNow password (or press Enter to skip): ").strip()

if not password_input:
    print("\n⚠️  Skipping basic auth test - no password provided")
    print("\nTo get a new token, either:")
    print("1. Run this script and provide password")
    print("2. Use SignNow OAuth 2.0 authorization code flow")
    print("3. Get token from SignNow API UI: https://signnow.com/api")
    sys.exit(0)

# Try basic auth
print(f"\n🔄 Attempting basic auth for user: {username}")
payload = {
    "grant_type": "password",
    "username": username,
    "password": password_input,
    "client_id": cred.client_id,
    "client_secret": cred.client_secret,
    "scope": "*"
}

try:
    response = requests.post(
        SIGNNOW_TOKEN_URL,
        data=payload,
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✅ SUCCESS!")
        data = response.json()
        print(f"   Access token: {data.get('access_token', '')[:30]}...")
        print(f"   Refresh token: {data.get('refresh_token', '')[:20]}...")
        print(f"   Expires in: {data.get('expires_in')} seconds")
        
        # Update credential
        cred.access_token = data.get("access_token")
        cred.refresh_token = data.get("refresh_token", "")
        expires_in = data.get("expires_in", 3600)
        cred.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
        cred.last_refreshed_at = timezone.now()
        cred.save()
        print(f"\n   ✅ Updated credential in database!")
        print(f"   Token will expire at: {cred.token_expires_at}")
        
    else:
        print(f"   ❌ FAILED: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

print("\n" + "=" * 70)
