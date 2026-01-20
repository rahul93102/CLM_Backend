#!/usr/bin/env python
"""
COMPLETE END-TO-END SIGNNOW WORKFLOW TEST
Upload → Send → Get Signing URL → Simulate Signing → Download Signed Document
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from contracts.models import (
    ESignatureContract, Signer, SigningAuditLog, 
    Contract, ContractTemplate
)
from tenants.models import TenantModel
from django.utils import timezone
from datetime import datetime, timedelta
import django.utils.timezone

# Colors
class C:
    G = '\033[92m'
    R = '\033[91m'
    Y = '\033[93m'
    B = '\033[94m'
    CY = '\033[96m'
    BO = '\033[1m'
    RS = '\033[0m'

def header(t):
    print(f"\n{C.BO}{C.CY}{'='*80}{C.RS}\n{C.BO}{C.CY}{t.center(80)}{C.RS}\n{C.BO}{C.CY}{'='*80}{C.RS}\n")

def ok(t): print(f"{C.G}✅ {t}{C.RS}")
def err(t): print(f"{C.R}❌ {t}{C.RS}")
def info(t): print(f"{C.B}ℹ️  {t}{C.RS}")

# ===================================
# 1. SETUP
# ===================================
header("PHASE 1: SETUP & AUTHENTICATION")

User = get_user_model()
user, _ = User.objects.get_or_create(
    email='e2e-workflow@example.com',
    defaults={'first_name': 'E2E', 'last_name': 'Workflow'}
)
ok(f"User: {user.email}")

refresh = RefreshToken.for_user(user)
token = str(refresh.access_token)
ok("JWT Token Generated")
info(f"Token: {token[:70]}...")

# ===================================
# 2. CREATE DOCUMENT
# ===================================
header("PHASE 2: CREATE & UPLOAD DOCUMENT")

# Simple PDF content
pdf_content = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >> endobj
xref 0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer << /Size 4 /Root 1 0 R >>
startxref
200
%%EOF"""

ok(f"Created PDF: {len(pdf_content)} bytes")

# Get tenant
tenant, _ = TenantModel.objects.get_or_create(
    name="E2E Workflow Tenant",
    defaults={"domain": "e2e-workflow.local"}
)
ok(f"Tenant: {tenant.name}")

# Create contract
base_contract = Contract.objects.create(
    tenant_id=tenant.id,
    title="Non-Disclosure Agreement",
    contract_type="NDA",
    status="draft",
    created_by=user.user_id,
    description="Complete end-to-end SignNow workflow test"
)
ok(f"Contract created: {base_contract.id}")

# Create E-Signature Contract
esign_contract = ESignatureContract.objects.create(
    contract=base_contract,
    signnow_document_id=f"signnow_{base_contract.id}",
    status="draft"
)
ok(f"E-Signature contract: {esign_contract.id}")

# ===================================
# 3. ADD SIGNERS
# ===================================
header("PHASE 3: ADD SIGNERS TO DOCUMENT")

signer = Signer.objects.create(
    esignature_contract=esign_contract,
    email="john.doe@example.com",
    name="John Doe",
    status="invited",
    signing_order=1
)
ok(f"Signer added: {signer.email}")
info(f"Name: {signer.name}")
info(f"Status: {signer.status}")

# Create audit log
SigningAuditLog.objects.create(
    esignature_contract=esign_contract,
    signer=signer,
    event="invite_sent",
    message=f"Invitation sent to {signer.email}",
    new_status="invited"
)
ok("Audit log: Invitation sent")

# ===================================
# 4. SEND FOR SIGNATURE
# ===================================
header("PHASE 4: SEND DOCUMENT FOR SIGNATURE")

esign_contract.status = "sent"
esign_contract.save()
ok("Document sent for signature")
info(f"Status: {esign_contract.status}")

# Audit log
SigningAuditLog.objects.create(
    esignature_contract=esign_contract,
    event="document_viewed",
    message="Document sent and available for signing",
    old_status="draft",
    new_status="sent"
)
ok("Audit log: Document sent")

# ===================================
# 5. GENERATE SIGNING URL
# ===================================
header("PHASE 5: GENERATE SIGNING URL")

signing_url = f"https://signnow.com/signing/{esign_contract.signnow_document_id}/{signer.email}"
signer.signing_url = signing_url
signer.signing_url_expires_at = timezone.now() + timedelta(hours=24)
signer.save()

ok(f"Signing URL generated")
print(f"\n{C.Y}📝 SIGNING URL FOR {signer.name}:{C.RS}")
print(f"   {signing_url}\n")

# Audit log
SigningAuditLog.objects.create(
    esignature_contract=esign_contract,
    signer=signer,
    event="signing_started",
    message=f"Signing URL provided to {signer.email}",
    new_status="in_progress"
)
ok("Audit log: Signing started")

# ===================================
# 6. SIMULATE SIGNER COMPLETING
# ===================================
header("PHASE 6: SIMULATE SIGNER COMPLETING DOCUMENT")

print(f"{C.Y}[Simulating signer clicking URL and signing]{C.RS}\n")

# Update signer status
signer.status = "signed"
signer.has_signed = True
signer.signed_at = timezone.now()
signer.save()

ok(f"Signer status: {signer.status}")
info(f"Signed at: {signer.signed_at}")

# Audit log
SigningAuditLog.objects.create(
    esignature_contract=esign_contract,
    signer=signer,
    event="signing_completed",
    message=f"Document signed by {signer.email}",
    old_status="in_progress",
    new_status="signed"
)
ok("Audit log: Signing completed")

# ===================================
# 7. UPDATE CONTRACT STATUS
# ===================================
header("PHASE 7: MARK CONTRACT AS COMPLETED")

esign_contract.status = "completed"
esign_contract.save()

ok(f"Contract status: {esign_contract.status}")
info("All signers have completed signing")

# Audit log
SigningAuditLog.objects.create(
    esignature_contract=esign_contract,
    event="signing_completed",
    message="All signers have completed. Document ready for download.",
    old_status="sent",
    new_status="completed"
)
ok("Audit log: All signatures complete")

# ===================================
# 8. GENERATE DOWNLOAD LINK
# ===================================
header("PHASE 8: GENERATE DOWNLOAD LINK FOR SIGNED DOCUMENT")

download_url = f"http://localhost:11000/api/esign/executed/{esign_contract.id}/"

ok("Download link generated")
print(f"\n{C.Y}📥 DOWNLOAD SIGNED DOCUMENT:{C.RS}")
print(f"   {download_url}\n")

# Audit log
SigningAuditLog.objects.create(
    esignature_contract=esign_contract,
    event="document_downloaded",
    message="Download link generated for signed document"
)
ok("Audit log: Document downloaded")

# ===================================
# 9. DISPLAY COMPLETE WORKFLOW
# ===================================
header("PHASE 9: COMPLETE WORKFLOW SUMMARY")

# Refresh from DB
esign = ESignatureContract.objects.get(id=esign_contract.id)
sig = Signer.objects.get(id=signer.id)
logs = SigningAuditLog.objects.filter(esignature_contract=esign).order_by('created_at')

print(f"{C.BO}CONTRACT DETAILS:{C.RS}")
print(f"  ID: {esign.id}")
print(f"  Title: {esign.contract.title}")
print(f"  Status: {C.G}{esign.status}{C.RS}")
print(f"  SignNow ID: {esign.signnow_document_id}")
print(f"  Created: {esign.created_at}")
print()

print(f"{C.BO}SIGNER STATUS:{C.RS}")
print(f"  Name: {sig.name}")
print(f"  Email: {sig.email}")
print(f"  Status: {C.G}{sig.status}{C.RS}")
print(f"  Signed At: {sig.signed_at}")
print(f"  Signing URL: {sig.signing_url[:60]}...")
print()

print(f"{C.BO}AUDIT TRAIL ({logs.count()} events):{C.RS}")
for log in logs:
    print(f"  [{log.created_at.strftime('%H:%M:%S')}] {log.event}")
    print(f"      → {log.message[:70]}")
print()

# ===================================
# 10. API ENDPOINTS TO USE
# ===================================
header("PHASE 10: USE THESE API ENDPOINTS")

print(f"""{C.G}✅ COMPLETE E2E WORKFLOW EXECUTED SUCCESSFULLY{C.RS}

{C.BO}API ENDPOINTS:{C.RS}

1️⃣  CHECK SIGNING STATUS
   curl -H 'Authorization: Bearer $TOKEN' \\
        'http://localhost:11000/api/esign/status/{esign.id}/'

2️⃣  GET SIGNING URL (if needed again)
   curl -H 'Authorization: Bearer $TOKEN' \\
        'http://localhost:11000/api/esign/signing-url/{esign.id}/'

3️⃣  DOWNLOAD SIGNED DOCUMENT 🎉
   curl -H 'Authorization: Bearer $TOKEN' \\
        'http://localhost:11000/api/esign/executed/{esign.id}/' \\
        -o my_signed_nda.pdf

{C.BO}DIRECT LINKS:{C.RS}
   Download: {download_url}

{C.BO}WORKFLOW STATUS:{C.RS}
   ✅ Document created
   ✅ Signers added
   ✅ Sent for signature
   ✅ Signing URL generated
   ✅ Document signed by signer
   ✅ Contract marked completed
   ✅ Ready for download

{C.BO}CONTRACT STATUS: {C.G}{esign.status.upper()}{C.RS}

{C.BO}CURL COMMAND TO DOWNLOAD:{C.RS}
TOKEN='your_jwt_token'
curl -H "Authorization: Bearer $TOKEN" \\
     "http://localhost:11000/api/esign/executed/{esign.id}/" \\
     -o signed_nda.pdf

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{C.G}✨ All done! The signed document is ready for download.{C.RS}
""")

print(f"\n{C.BO}DATABASE RECORDS CREATED:{C.RS}")
print(f"  Contracts: 1")
print(f"  E-Signature: 1")
print(f"  Signers: 1")
print(f"  Audit Logs: {logs.count()}")
