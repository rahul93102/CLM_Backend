#!/usr/bin/env python3
"""Check what ESignature contracts exist in database"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from contracts.models import ESignatureContract, Contract, Signer

print("\n" + "="*70)
print("📋 CHECKING DATABASE FOR ESIGNATURE CONTRACTS")
print("="*70)

# Check contracts
contracts = Contract.objects.all()
print(f"\n✅ Total Contracts: {contracts.count()}")
for c in contracts[:5]:
    print(f"   - {c.id}: {c.title} (Status: {c.status})")

# Check ESignature contracts
esign_contracts = ESignatureContract.objects.all()
print(f"\n✅ Total ESignature Contracts: {esign_contracts.count()}")
for e in esign_contracts[:5]:
    print(f"   - {e.contract_id}: {e.status} (SignNow ID: {e.signnow_document_id})")
    
    # Check signers
    signers = Signer.objects.filter(esignature_contract=e)
    print(f"     Signers: {signers.count()}")
    for s in signers:
        print(f"       - {s.email}: {s.status} (Signed: {s.signed_at})")

if esign_contracts.count() == 0:
    print("\n⚠️  No ESignature contracts found!")
    print("   To test, you need to:")
    print("   1. Create a contract")
    print("   2. Upload it to SignNow")
    print("   3. Add signers")
    print("   4. Use the contract ID for PDF generation")
