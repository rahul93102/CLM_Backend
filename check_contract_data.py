#!/usr/bin/env python3
import os
import django
import json
from datetime import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = 'clm_backend.settings'
django.setup()

from contracts.models import ESignatureContract, Signer, SigningAuditLog

# Get contract and details
contract_id = 'aae65358-f709-4994-ab28-f4e2874c35e3'
contract = ESignatureContract.objects.get(id=contract_id)

print("╔════════════════════════════════════════════════════════════════╗")
print("║                    CONTRACT DATA RETRIEVED                      ║")
print("╚════════════════════════════════════════════════════════════════╝")
print()

print("📄 CONTRACT DETAILS:")
print(f"   ID:                {contract.id}")
print(f"   Title:             {contract.title}")
print(f"   Status:            {contract.status}")
print(f"   Version:           {contract.current_version}")
print(f"   Created:           {contract.created_at}")
print(f"   Completed:         {contract.completed_at}")
print(f"   SignNow Doc ID:    {contract.signnow_document_id}")
print()

print("🔏 SIGNERS:")
signers = list(contract.signers.all())
for signer in signers:
    print(f"   Email:    {signer.email}")
    print(f"   Status:   {signer.status}")
    print(f"   Signed:   {signer.signed_at}")
print()

print("📋 AUDIT TRAIL:")
logs = list(SigningAuditLog.objects.filter(esignature_contract=contract).order_by('created_at'))
for log in logs:
    print(f"   [{log.event}] {log.message} → {log.new_status}")
    print(f"      Time: {log.created_at}")
print()

# Save for PDF generation
import pickle
with open('/tmp/contract_data.pkl', 'wb') as f:
    pickle.dump({
        'contract': contract,
        'signers': signers,
        'logs': logs
    }, f)

print("✅ Data saved for PDF generation")
