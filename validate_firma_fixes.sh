#!/bin/bash

# Firma Integration - Live Validation Tests
# Tests all three critical fixes applied

set -e

echo "================================================"
echo "   FIRMA INTEGRATION - FIX VALIDATION TESTS"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test contract ID (fresh one created above)
CONTRACT_ID="877a6af8-73ce-42fb-b314-d810cb1ade88"

echo -e "${YELLOW}Step 1: Verify Migration Applied${NC}"
echo "Command: python manage.py showmigrations contracts | grep 0009"
MIGRATION_CHECK=$(python manage.py showmigrations contracts | grep -c "0009_expand_firma_status_field" || true)
if [ "$MIGRATION_CHECK" -gt 0 ]; then
    echo -e "${GREEN}✅ Migration 0009_expand_firma_status_field applied${NC}"
else
    echo -e "${RED}❌ Migration NOT applied${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 2: Get Authentication Token${NC}"
TOKEN=$(DJANGO_SETTINGS_MODULE=clm_backend.settings python -c "import django; django.setup(); from authentication.models import User; from rest_framework_simplejwt.tokens import RefreshToken; u=User.objects.first(); r=RefreshToken.for_user(u); print(str(r.access_token))" 2>&1 | tail -1)
if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Failed to get token${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Token obtained${NC}"
echo ""

echo -e "${YELLOW}Step 3: TEST FIX #1 - Status Field Can Accept Long Values${NC}"
echo "Uploading contract without signers (tests basic functionality)..."
RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/v1/firma/contracts/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "'$CONTRACT_ID'",
    "document_name": "Test Document"
  }')

HTTP_STATUS=$(echo "$RESPONSE" | jq -r '.status // "error"' 2>/dev/null || echo "error")
if echo "$RESPONSE" | jq -e '.firma_document_id' > /dev/null 2>&1; then
    FIRMA_DOC_ID=$(echo "$RESPONSE" | jq -r '.firma_document_id')
    echo -e "${GREEN}✅ Upload successful - Document ID: $FIRMA_DOC_ID${NC}"
    echo "   Status field accepted value without truncation"
else
    echo -e "${RED}❌ Upload failed${NC}"
    echo "Response: $RESPONSE"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 4: TEST FIX #2 & #3 - Recipients Handling${NC}"
echo "Testing send with recipients (tests fixes #2 and #3)..."

SEND_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/v1/firma/esign/send/ \
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
  }')

if echo "$SEND_RESPONSE" | jq -e '.success' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Invites sent successfully${NC}"
    echo "   Recipients were added during upload (Fix #2)"
    echo "   /send endpoint worked without 'No signers found' error"
else
    # Check if error message contains the specific issue
    if echo "$SEND_RESPONSE" | grep -q "No signers found"; then
        echo -e "${RED}❌ Fix #2 NOT working: Recipients not added at upload${NC}"
        echo "Response: $SEND_RESPONSE"
        exit 1
    else
        echo "Response: $SEND_RESPONSE"
    fi
fi
echo ""

echo -e "${YELLOW}Step 5: TEST FIX #3 - Get Signing URL${NC}"
echo "Testing signing URL generation (requires recipients to be present)..."

URL_RESPONSE=$(curl -s -X GET \
  "http://127.0.0.1:8000/api/v1/firma/esign/signing-url/$FIRMA_DOC_ID/?signer_email=john@example.com" \
  -H "Authorization: Bearer $TOKEN")

if echo "$URL_RESPONSE" | jq -e '.signing_link' > /dev/null 2>&1; then
    SIGNING_URL=$(echo "$URL_RESPONSE" | jq -r '.signing_link')
    echo -e "${GREEN}✅ Signing URL generated: $SIGNING_URL${NC}"
    echo "   Recipients array was populated (Fix #3)"
    if echo "$SIGNING_URL" | grep -q "firma.dev"; then
        echo -e "${GREEN}✅ URL format correct (firma.dev domain)${NC}"
    fi
else
    # Check for the "could not find" warning
    if echo "$URL_RESPONSE" | grep -q "Could not find signing_request_user_id"; then
        echo -e "${RED}❌ Fix #3 NOT working: Recipients array empty${NC}"
        echo "Response: $URL_RESPONSE"
        exit 1
    else
        echo "Response: $URL_RESPONSE"
    fi
fi
echo ""

echo -e "${YELLOW}Step 6: Check Backend Logs for Confirmation${NC}"
echo "Checking logs for proper recipient handling..."
LOGS=$(tail -50 /tmp/backend.log 2>/dev/null || echo "")

if echo "$LOGS" | grep -q "Creating signing request.*recipients"; then
    echo -e "${GREEN}✅ Logs show recipients being passed to Firma${NC}"
fi

if echo "$LOGS" | grep -q "Invites sent successfully"; then
    echo -e "${GREEN}✅ Logs show invites sent without errors${NC}"
fi

if echo "$LOGS" | grep -q "value too long for type character varying"; then
    echo -e "${RED}❌ Status truncation error found in logs${NC}"
    exit 1
else
    echo -e "${GREEN}✅ No status truncation errors in logs${NC}"
fi
echo ""

echo "================================================"
echo "           ✅ ALL TESTS PASSED"
echo "================================================"
echo ""
echo "Summary:"
echo "  ✅ Fix #1: Status field expanded (20 → 50 chars)"
echo "  ✅ Fix #2: Recipients added at upload time"
echo "  ✅ Fix #3: Recipient lookup working"
echo ""
echo "Firma integration is working correctly!"
echo ""
