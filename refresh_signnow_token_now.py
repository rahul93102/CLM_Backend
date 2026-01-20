#!/usr/bin/env python3
"""
Direct SignNow Token Generator
Uses provided credentials to generate fresh OAuth token
"""
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

# Credentials provided by user
CLIENT_ID = "0f6f721511097022932a29e6f3fa3e66"
CLIENT_SECRET = "3814bd35926c2a7b18f53e0bedf87136"
APPLICATION_ID = "a5ca3ac16aff479b8379d163f7ee9f46c241824f"

print("=" * 70)
print("SIGNNOW TOKEN GENERATOR - USING PROVIDED CREDENTIALS")
print("=" * 70)
print(f"\nClient ID: {CLIENT_ID}")
print(f"Application ID: {APPLICATION_ID}")
print(f"Secret Key: {CLIENT_SECRET[:10]}...")

# Get credential from database
cred = SignNowCredential.objects.first()
if not cred:
    print("\n❌ No SignNow credential found in database!")
    sys.exit(1)

print(f"\n✅ Found credential in database: {cred.id}")

# Update credentials if needed
if cred.client_id != CLIENT_ID or cred.client_secret != CLIENT_SECRET:
    print("\n🔄 Updating credentials in database...")
    cred.client_id = CLIENT_ID
    cred.client_secret = CLIENT_SECRET
    cred.save()
    print("   ✅ Credentials updated")

SIGNNOW_TOKEN_URL = "https://api.signnow.com/oauth2/token"

print("\n" + "=" * 70)
print("METHOD 1: Using Username/Password (Basic Auth)")
print("=" * 70)

username = input("\nEnter SignNow username/email: ").strip()
if not username:
    username = "vishaljha2806@gmail.com"
    print(f"Using default: {username}")

password = input("Enter SignNow password: ").strip()

if password:
    print(f"\n🔄 Attempting authentication for: {username}")
    payload = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "*"
    }
    
    try:
        response = requests.post(SIGNNOW_TOKEN_URL, data=payload, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! Token generated")
            print(f"Access token: {data.get('access_token', '')[:40]}...")
            print(f"Refresh token: {data.get('refresh_token', '')[:40]}...")
            print(f"Expires in: {data.get('expires_in')} seconds")
            
            # Update database
            cred.access_token = data.get("access_token")
            cred.refresh_token = data.get("refresh_token", "")
            expires_in = data.get("expires_in", 3600)
            cred.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
            cred.last_refreshed_at = timezone.now()
            cred.save()
            
            print(f"\n✅ Updated database!")
            print(f"Token expires at: {cred.token_expires_at}")
            print("\n" + "=" * 70)
            print("✅ READY FOR REAL-TIME SIGNATURE POLLING!")
            print("=" * 70)
            sys.exit(0)
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            print("\nTrying refresh token method...")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

# Try refresh token if basic auth failed
print("\n" + "=" * 70)
print("METHOD 2: Using Refresh Token")
print("=" * 70)

if cred.refresh_token:
    print(f"\n🔄 Attempting token refresh...")
    print(f"Refresh token: {cred.refresh_token[:20]}...")
    
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": cred.refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    
    try:
        response = requests.post(SIGNNOW_TOKEN_URL, data=payload, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! Token refreshed")
            
            cred.access_token = data.get("access_token")
            cred.refresh_token = data.get("refresh_token", cred.refresh_token)
            expires_in = data.get("expires_in", 3600)
            cred.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
            cred.last_refreshed_at = timezone.now()
            cred.save()
            
            print(f"\n✅ Token refreshed and saved!")
            print(f"Token expires at: {cred.token_expires_at}")
            print("\n" + "=" * 70)
            print("✅ READY FOR REAL-TIME SIGNATURE POLLING!")
            print("=" * 70)
            sys.exit(0)
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

print("\n" + "=" * 70)
print("⚠️  MANUAL TOKEN GENERATION REQUIRED")
print("=" * 70)
print("\nOption 1: Run this script again with valid username/password")
print("Option 2: Get token from SignNow API Console:")
print("         https://signnow.com/api")
print("\nThen update manually:")
print(f"  cred = SignNowCredential.objects.get(id='{cred.id}')")
print("  cred.access_token = 'YOUR_TOKEN'")
print("  cred.refresh_token = 'YOUR_REFRESH_TOKEN'")
print("  cred.save()")
print("=" * 70)
