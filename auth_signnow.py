import os
import sys
import django
import requests
from datetime import timedelta
from getpass import getpass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.utils import timezone
from contracts.models import SignNowCredential

CLIENT_ID = '5f2b0125c6437bf6a3db5d0802dc804d'
CLIENT_SECRET = 'dc2f8d0ffbbb26cc13d8cd503e3cd249'

print("=" * 70)
print("SIGNNOW TOKEN GENERATOR - Username & Password")
print("=" * 70)

username = input("\nEnter your SignNow email/username: ").strip()
password = getpass("Enter your SignNow password: ")

if not username or not password:
    print("❌ Email and password required!")
    sys.exit(1)

print(f"\nAuthenticating as: {username}")
print("Exchanging credentials for access token...")

payload = {
    "grant_type": "password",
    "username": username,
    "password": password,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "scope": "*"
}

response = requests.post("https://api.signnow.com/oauth2/token", data=payload, timeout=10)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token", "")
    expires_in = data.get("expires_in", 3600)
    
    print(f"\n✅ SUCCESS!")
    print(f"Access token: {access_token[:40]}...")
    print(f"Refresh token: {refresh_token[:40]}...")
    print(f"Expires in: {expires_in} seconds ({expires_in/3600:.1f} hours)")
    
    cred = SignNowCredential.objects.first()
    cred.access_token = access_token
    cred.refresh_token = refresh_token
    cred.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
    cred.last_refreshed_at = timezone.now()
    cred.save()
    
    print(f"\n✅ Database updated!")
    print(f"Token expires at: {cred.token_expires_at}")
    print("\n" + "=" * 70)
    print("✅ READY FOR REAL-TIME SIGNATURE POLLING!")
    print("=" * 70)
    
else:
    print(f"❌ Failed: {response.status_code}")
    print(f"Response: {response.text}")
    print("\nMake sure your email and password are correct!")
