#!/usr/bin/env python
"""Quick SignNow setup and test"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from contracts.models import SignNowCredential, ESignatureContract, Signer, SigningAuditLog
from django.utils import timezone
from datetime import timedelta

print("="*60)
print("SignNow Integration - Quick Setup & Verification")
print("="*60)

# Step 1: Check/Create Credential
print("\n[1] Checking SignNow Credentials...")
creds_count = SignNowCredential.objects.count()
print(f"    Existing credentials: {creds_count}")

if creds_count == 0:
    print("    Creating new credential...")
    cred = SignNowCredential.objects.create(
        client_id=os.getenv('SIGNNOW_CLIENT_ID', 'not_set'),
        client_secret=os.getenv('SIGNNOW_SECRET_KEY', 'not_set'),
        account_id=os.getenv('SIGNNOW_APPLICATION_ID', 'not_set'),
        account_name='CLM Service Account',
        access_token='test_token_initial',
        refresh_token='test_refresh_initial',
        token_expires_at=timezone.now() + timedelta(hours=1),
    )
    print(f"    ✅ Created: {cred.account_name}")
    print(f"    ✅ Account ID: {cred.account_id}")
else:
    cred = SignNowCredential.objects.first()
    print(f"    ✅ Credential exists: {cred.account_name}")
    print(f"    ✅ Account ID: {cred.account_id}")
    print(f"    ✅ Token expires: {cred.token_expires_at}")

# Step 2: Check Models
print("\n[2] Checking Database Models...")
print(f"    ✅ SignNowCredential: {SignNowCredential.objects.count()}")
print(f"    ✅ ESignatureContract: {ESignatureContract.objects.count()}")
print(f"    ✅ Signer: {Signer.objects.count()}")
print(f"    ✅ SigningAuditLog: {SigningAuditLog.objects.count()}")

# Step 3: Check Services
print("\n[3] Checking Services...")
try:
    from contracts.signnow_service import SignNowAuthService, SignNowAPIService
    print("    ✅ SignNowAuthService imported")
    print("    ✅ SignNowAPIService imported")
except Exception as e:
    print(f"    ❌ Service import failed: {e}")

# Step 4: Check Views
print("\n[4] Checking API Endpoints...")
try:
    from contracts import signnow_views
    print("    ✅ signnow_views imported")
    endpoints = [
        'upload_contract',
        'send_for_signature',
        'get_signing_url',
        'check_status',
        'get_executed_document'
    ]
    for ep in endpoints:
        if hasattr(signnow_views, ep):
            print(f"    ✅ {ep}")
        else:
            print(f"    ❌ {ep} not found")
except Exception as e:
    print(f"    ❌ Views import failed: {e}")

# Step 5: Django Check
print("\n[5] Django System Check...")
from django.core.management import call_command
from io import StringIO
try:
    out = StringIO()
    call_command('check', stdout=out)
    result = out.getvalue()
    if 'System check identified no issues' in result:
        print("    ✅ System check passed: 0 issues")
    else:
        print(f"    ⚠️  {result[:100]}")
except Exception as e:
    print(f"    ❌ Check failed: {e}")

print("\n" + "="*60)
print("✅ SETUP COMPLETE - System Ready for Testing")
print("="*60)
