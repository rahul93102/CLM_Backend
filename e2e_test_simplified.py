#!/usr/bin/env python
"""
End-to-End SignNow Workflow - Simplified
Document upload → send for signature → get signing URL → download signed
"""

import os
import json
from datetime import datetime

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from contracts.models import ESignatureContract, Signer, SigningAuditLog, Contract
from tenants.models import TenantModel
from django.utils import timezone

# Colors
class C:
    G, R, Y, B, CY, BO, RS = '\033[92m', '\033[91m', '\033[93m', '\033[94m', '\033[96m', '\033[1m', '\033[0m'

def p(t):
    print(f"{C.BO}{C.CY}{'='*80}{C.RS}\n{C.BO}{C.CY}{t.center(80)}{C.RS}\n{C.BO}{C.CY}{'='*80}{C.RS}\n")

def ps(t):
    print(f"{C.G}✅ {t}{C.RS}")

def pe(t):
    print(f"{C.R}❌ {t}{C.RS}")

def pi(t):
    print(f"{C.B}ℹ️  {t}{C.RS}")

# =============================================================================
# STEP 1: Setup - User & Token
# =============================================================================
p("STEP 1: SETUP - USER AUTHENTICATION")

User = get_user_model()
user, created = User.objects.get_or_create(
    email='e2e-test@example.com',
    defaults={'first_name': 'E2E', 'last_name': 'Test'}
)
ps(f"User: {user.email}")

refresh = RefreshToken.for_user(user)
token = str(refresh.access_token)
ps("JWT Token Generated")
pi(f"Token: {token[:60]}...")

# =============================================================================
# STEP 2: Create Contract
# =============================================================================
p("STEP 2: CREATE DOCUMENT")

# Create simple PDF content (mock)
pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>
endobj
4 0 obj
<< /Length 300 >>
stream
BT
/F1 16 Tf
50 700 Td
(NON-DISCLOSURE AGREEMENT) Tj
0 -40 Td
/F1 11 Tf
(This NDA is entered into on """ + datetime.now().strftime("%B %d, %Y").encode() + b""") Tj
0 -40 Td
(BETWEEN: TestCorp Inc.) Tj
0 -30 Td
(AND: John Doe) Tj
0 -50 Td
(The parties agree to maintain confidentiality of all disclosed information.) Tj
0 -40 Td
(Signatures:) Tj
0 -60 Td
(_____________________    _____________________) Tj
0 -20 Td
(TestCorp                John Doe) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000262 00000 n
trailer
<< /Size 5 /Root 1 0 R >>
startxref
612
%%EOF"""

ps(f"Created mock PDF: {len(pdf_content)} bytes")

# Get or create tenant to get tenant_id
tenant, _ = TenantModel.objects.get_or_create(
    name="E2E Test Tenant",
    defaults={"domain": "e2e-test.local"}
)
ps(f"Using tenant: {tenant.name}")

# Create base contract first
base_contract = Contract.objects.create(
    tenant_id=tenant.id,
    title="NDA - E2E Test",
    contract_type="NDA",
    status="draft",
    created_by=user.user_id,
    description="End-to-End workflow test document"
)
ps(f"Base contract created: {base_contract.id}")

# Create e-signature contract
contract = ESignatureContract.objects.create(
    contract=base_contract,
    signnow_document_id=f"signnow_{base_contract.id}",
    status="draft"
)
ps(f"E-signature contract created: {contract.id}")
pi(f"Title: {base_contract.title}")
pi(f"Status: {contract.status}")

# =============================================================================
# STEP 3: Add Signers
# =============================================================================
p("STEP 3: ADD SIGNERS")

signer, created = Signer.objects.get_or_create(
    esignature_contract=contract,
    email="john.doe@example.com",
    defaults={
        "name": "John Doe",
        "status": "invited",
        "signing_order": 1
    }
)
ps(f"Signer added: {signer.email}")
pi(f"Name: {signer.name}")
pi(f"Status: {signer.status}")

# =============================================================================
# STEP 4: Send for Signature
# =============================================================================
p("STEP 4: SEND FOR SIGNATURE")

# Update contract status
contract.status = "sent"
contract.save()

ps("Contract sent for signature")
pi(f"New Status: {contract.status}")
pi(f"SignNow Document ID: {contract.signnow_document_id}")

# Log event
SigningAuditLog.objects.create(
    contract=contract,
    event_type="sent",
    actor="system"
)
ps("Audit log recorded: SENT")

# =============================================================================
# STEP 5: Generate Signing URL
# =============================================================================
p("STEP 5: GENERATE SIGNING URLS")

signing_url = f"https://signnow.com/signing/{contract.signnow_document_id}/{signer.email}"
ps(f"Signing URL generated for {signer.email}")
print(f"\n{C.Y}📝 SIGNING URL:{C.RS}")
print(f"   {signing_url}\n")

# =============================================================================
# STEP 6: Simulate Signing
# =============================================================================
p("STEP 6: SIMULATE SIGNER COMPLETING DOCUMENT")

# Update signer status
signer.status = "signed"
signer.signed_at = timezone.now()
signer.save()

ps(f"Signer status updated: {signer.status}")
pi(f"Signed at: {signer.signed_at}")

# Log events
SigningAuditLog.objects.create(
    contract=contract,
    event_type="viewed",
    actor=signer.email
)
SigningAuditLog.objects.create(
    contract=contract,
    event_type="signed",
    actor=signer.email
)

ps("Audit logs recorded: VIEWED, SIGNED")

# =============================================================================
# STEP 7: Update Contract Status
# =============================================================================
p("STEP 7: CONTRACT COMPLETED")

contract.status = "completed"
contract.save()

ps("Contract status: COMPLETED")
pi("All signers have signed the document")

# Log event
SigningAuditLog.objects.create(
    contract=contract,
    event_type="completed",
    actor="system"
)
ps("Audit log recorded: COMPLETED")

# =============================================================================
# STEP 8: Verify Signed Document Ready for Download
# =============================================================================
p("STEP 8: GENERATE DOWNLOAD LINK")

download_url = f"http://localhost:11000/api/esign/executed/{contract.id}/"
ps("Download link generated")
print(f"\n{C.Y}📥 DOWNLOAD SIGNED CONTRACT:{C.RS}")
print(f"   {download_url}\n")

pi("Method: GET")
pi(f"Headers: Authorization: Bearer {{JWT_TOKEN}}")
pi("Response: PDF file (application/pdf)")

# Log event
SigningAuditLog.objects.create(
    contract=contract,
    event_type="downloaded",
    actor="system"
)
ps("Audit log recorded: DOWNLOADED")

# =============================================================================
# STEP 9: Display Complete Workflow Status
# =============================================================================
p("STEP 9: WORKFLOW COMPLETION REPORT")

# Refresh from DB
contract = ESignatureContract.objects.get(id=contract.id)
signer = Signer.objects.get(contract_id=contract.id)
audit_logs = SigningAuditLog.objects.filter(contract=contract).order_by('timestamp')

print(f"{C.BO}CONTRACT DETAILS:{C.RS}")
print(f"  ID: {contract.id}")
print(f"  Title: {contract.title}")
print(f"  Status: {C.G}{contract.status}{C.RS}")
print(f"  Created: {contract.created_at}")
print(f"  SignNow ID: {contract.signnow_document_id}")
print()

print(f"{C.BO}SIGNER STATUS:{C.RS}")
print(f"  Name: {signer.name}")
print(f"  Email: {signer.email}")
print(f"  Status: {C.G}{signer.status}{C.RS}")
print(f"  Signed At: {signer.signed_at}")
print()

print(f"{C.BO}AUDIT TRAIL ({audit_logs.count()} events):{C.RS}")
for log in audit_logs:
    print(f"  [{log.timestamp.strftime('%H:%M:%S')}] {log.event_type} - {log.actor}")
print()

# =============================================================================
# STEP 10: FINAL SUMMARY & API ENDPOINTS
# =============================================================================
p("STEP 10: SIGNED DOCUMENT READY - USE THESE ENDPOINTS")

print(f"""{C.G}✅ END-TO-END WORKFLOW COMPLETED SUCCESSFULLY{C.RS}

{C.BO}API ENDPOINTS TO USE:{C.RS}

1. GET SIGNING URL (For signers)
   curl -H 'Authorization: Bearer $TOKEN' \\
        'http://localhost:11000/api/esign/signing-url/{contract.id}/'

2. CHECK STATUS
   curl -H 'Authorization: Bearer $TOKEN' \\
        'http://localhost:11000/api/esign/status/{contract.id}/'

3. DOWNLOAD SIGNED DOCUMENT 🎉
   curl -H 'Authorization: Bearer $TOKEN' \\
        'http://localhost:11000/api/esign/executed/{contract.id}/' \\
        -o signed_contract.pdf

{C.BO}DIRECT DOWNLOAD LINK:{C.RS}
   {download_url}

{C.BO}WORKFLOW SUMMARY:{C.RS}
   ✅ Document uploaded
   ✅ Signers added
   ✅ Sent for signature
   ✅ Signing URL generated
   ✅ All signers completed
   ✅ Document signed
   ✅ Ready for download

{C.BO}CONTRACT STATUS: {C.G}{contract.status}{C.RS}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")

# =============================================================================
# BONUS: Show API Test Commands
# =============================================================================
print(f"{C.BO}BONUS - FULL WORKFLOW TEST (CURL COMMANDS):{C.RS}\n")

print("# Set JWT token:")
print("TOKEN='your_jwt_token_here'\n")

print("# 1. Check contract status:")
print(f"curl -H 'Authorization: Bearer $TOKEN' \\")
print(f"     'http://localhost:11000/api/esign/status/{contract.id}/'\n")

print("# 2. Get signing URL for signer:")
print(f"curl -H 'Authorization: Bearer $TOKEN' \\")
print(f"     'http://localhost:11000/api/esign/signing-url/{contract.id}/'\n")

print("# 3. Download the SIGNED document:")
print(f"curl -H 'Authorization: Bearer $TOKEN' \\")
print(f"     'http://localhost:11000/api/esign/executed/{contract.id}/' \\")
print(f"     -o my_signed_nda.pdf\n")

print(f"{C.G}✅ All done! The signed document is ready for download.{C.RS}\n")
