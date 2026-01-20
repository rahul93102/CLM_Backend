#!/usr/bin/env python3
"""Check and fix SignNow credentials"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from contracts.models import SignNowCredential
from django.utils import timezone
from datetime import timedelta

print("\n" + "="*70)
print("CHECKING SIGNNOW CREDENTIALS")
print("="*70)

# Check existing credentials
creds = SignNowCredential.objects.all()
print(f"\n✅ Total credentials: {creds.count()}")

for cred in creds:
    print(f"\n📋 Credential ID: {cred.id}")
    print(f"   Account: {cred.account_name}")
    print(f"   Client ID: {cred.client_id[:20]}...")
    print(f"   Has access_token: {bool(cred.access_token)}")
    print(f"   Has refresh_token: {bool(cred.refresh_token)}")
    print(f"   Token expires: {cred.token_expires_at}")
    print(f"   Last refreshed: {cred.last_refreshed_at}")
    
    # Check if token is expired
    if cred.token_expires_at:
        if cred.token_expires_at < timezone.now():
            print(f"   ⚠️  Token EXPIRED!")
        else:
            print(f"   ✓ Token still valid")

if creds.count() == 0:
    print("\n⚠️  No SignNow credentials found!")
    print("\nCreating mock credential for testing...")
    
    # Create a mock credential that will allow the system to work
    # In production, this should have real SignNow OAuth tokens
    cred = SignNowCredential.objects.create(
        access_token="mock_access_token_for_testing",
        refresh_token="mock_refresh_token_for_testing",
        token_expires_at=timezone.now() + timedelta(days=30),
        client_id="mock_client_id",
        client_secret="mock_client_secret",
        account_name="Test Service Account",
        account_id="test_account_123",
        last_refreshed_at=timezone.now()
    )
    print(f"✅ Created credential: {cred.id}")
    print(f"   This allows the API to return database data without SignNow errors")

print("\n" + "="*70)
print("NOTE: System will return database signature data (cached)")
print("For REAL-TIME SignNow data, configure actual OAuth credentials")
print("="*70)
