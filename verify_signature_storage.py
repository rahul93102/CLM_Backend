import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from contracts.models import ESignatureContract, Signer, SigningAuditLog

print("=" * 80)
print("COMPLETE SIGNATURE DATA VERIFICATION")
print("=" * 80)

contracts = ESignatureContract.objects.filter(status='completed')[:2]

for c in contracts:
    print(f"\n📋 CONTRACT: {c.contract_id}")
    print(f"   Status: {c.status}")
    print(f"   Created: {c.created_at}")
    print(f"   Updated: {c.updated_at}")
    print(f"   SignNow Doc ID: {c.signnow_document_id}")
    
    # Get signers
    signers = Signer.objects.filter(esignature_contract_id=c.id)
    print(f"\n   👥 SIGNERS ({signers.count()}):")
    
    for s in signers:
        print(f"      Name: {s.name}")
        print(f"      Email: {s.email}")
        print(f"      Status: {s.status}")
        print(f"      Has Signed: {s.has_signed}")
        print(f"      Signed At: {s.signed_at}")
        print(f"      Signing Order: {s.signing_order}")
        print(f"      Updated: {s.updated_at}")
        if s.signing_url:
            print(f"      Signing URL: {s.signing_url[:60]}...")
        print()
    
    # Get audit logs
    audits = SigningAuditLog.objects.filter(esignature_contract_id=c.id).order_by('-created_at')
    print(f"   📝 AUDIT LOGS ({audits.count()}):")
    
    for a in audits[:10]:
        print(f"      Event: {a.event}")
        print(f"      Message: {a.message}")
        print(f"      Time: {a.created_at}")
        print()

print("=" * 80)
print("✅ VERIFICATION COMPLETE")
print("=" * 80)
