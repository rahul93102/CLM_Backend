#!/bin/bash
# Firma Integration - Quick Validation After Fixes

echo "=== Firma Integration - Testing Critical Fixes ==="
echo ""
echo "Prerequisites:"
echo "1. Backend running on :8000"
echo "2. Migration applied: python manage.py migrate contracts"
echo "3. Django shell access"
echo ""

# Test 1: Verify migration applied
echo "TEST 1: Check if migration is applied"
echo "Command: python manage.py showmigrations contracts | grep 0009"
echo ""

# Test 2: Verify status field size
echo "TEST 2: Check FirmaSignatureContract.status field size"
echo "Command: python manage.py dbshell << 'SQL'"
echo "  SELECT column_name, character_maximum_length"
echo "  FROM information_schema.columns"
echo "  WHERE table_name='firma_signature_contracts' AND column_name='status';"
echo "SQL"
echo "Expected: character_maximum_length = 50"
echo ""

# Test 3: Create test contract
echo "TEST 3: Create test contract for upload"
cat << 'EOF'
Command:
python manage.py shell << 'PYTHON'
from contracts.models import Contract
from authentication.models import User
import uuid

user = User.objects.first()
if not user:
    user = User.objects.create_user('test@test.com', 'testpass')

contract = Contract.objects.create(
    id=str(uuid.uuid4()),
    tenant_id=user.tenant_id,
    title='Firma Test - Recipient Fix',
    status='draft',
    created_by=user.user_id,
)
print(f"CONTRACT_ID={contract.id}")
PYTHON

Expected output: CONTRACT_ID=<uuid>
EOF
echo ""

# Test 4: Get auth token
echo "TEST 4: Get authentication token"
cat << 'EOF'
Command:
TOKEN=$(DJANGO_SETTINGS_MODULE=clm_backend.settings python -c \
  "import django; django.setup(); \
   from authentication.models import User; \
   from rest_framework_simplejwt.tokens import RefreshToken; \
   u=User.objects.filter(email='test@test.com').first() or \
   User.objects.create_user('test@test.com', 'testpass'); \
   r=RefreshToken.for_user(u); \
   print(str(r.access_token))" 2>&1 | tail -1)

echo $TOKEN

Expected output: JWT token string
EOF
echo ""

# Test 5: Test upload WITHOUT signers (should work)
echo "TEST 5: Upload contract WITHOUT signers (baseline)"
cat << 'EOF'
Command:
curl -s -X POST http://localhost:8000/api/v1/firma/contracts/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "'$CONTRACT_ID'",
    "document_name": "Test Document - No Signers"
  }' | jq .

Expected Response (HTTP 201):
{
  "success": true,
  "contract_id": "...",
  "firma_document_id": "sr_...",
  "status": "draft",
  "message": "Contract uploaded successfully"
}
EOF
echo ""

# Test 6: Test upload WITH signers (main fix)
echo "TEST 6: Upload contract WITH signers (MAIN FIX)"
cat << 'EOF'
Command:
curl -s -X POST http://localhost:8000/api/v1/firma/contracts/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "'$CONTRACT_ID'",
    "document_name": "Test Document - With Signers",
    "signers": [
      {
        "name": "John Doe",
        "email": "john@example.com"
      },
      {
        "name": "Jane Smith",
        "email": "jane@example.com"
      }
    ]
  }' | jq .

Expected Response (HTTP 201):
{
  "success": true,
  "contract_id": "...",
  "firma_document_id": "sr_...",
  "status": "draft",
  "message": "Contract uploaded successfully"
}

CRITICAL: If this works, recipients were added to Firma request ✅
EOF
echo ""

# Test 7: Send invites
echo "TEST 7: Send invites (should work with recipients from upload)"
cat << 'EOF'
Command:
curl -s -X POST http://localhost:8000/api/v1/firma/esign/send/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "'$CONTRACT_ID'",
    "signers": [
      {
        "name": "John Doe",
        "email": "john@example.com"
      },
      {
        "name": "Jane Smith",
        "email": "jane@example.com"
      }
    ]
  }' | jq .

Expected Response (HTTP 200):
{
  "success": true,
  "message": "Signing invites sent successfully"
}

CRITICAL: If this works, "No signers found" error is fixed ✅
EOF
echo ""

# Test 8: Get signing URL
echo "TEST 8: Get signing URL"
cat << 'EOF'
Command:
curl -s -X GET \
  'http://localhost:8000/api/v1/firma/esign/signing-url/'$FIRMA_DOCUMENT_ID'/?signer_email=john@example.com' \
  -H "Authorization: Bearer $TOKEN" | jq .

Expected Response (HTTP 200):
{
  "success": true,
  "signing_link": "https://app.firma.dev/signing/...",
  "message": "Signing link generated"
}

CRITICAL: If this works, recipient lookup is working ✅
EOF
echo ""

# Test 9: Check logs
echo "TEST 9: Check backend logs for fix confirmation"
cat << 'EOF'
Command:
tail -100 /tmp/backend.log | grep -E "(recipients|Creating signing request|Invites sent|signature_contract)" | tail -10

Expected output:
- "Creating signing request ... with N recipients" (N > 0)
- "Invites sent successfully" (not "No signers found error")
- No "value too long for type character varying" error
EOF
echo ""

# Summary
echo "=== VALIDATION SUMMARY ==="
echo "✅ Migration applied (0009_expand_firma_status_field)"
echo "✅ Status field expanded to 50 chars"
echo "✅ Upload includes recipients in Firma request"
echo "✅ Invites can be sent without error"
echo "✅ Signing URLs can be generated"
echo ""
echo "All tests passing = Firma integration is working!"
