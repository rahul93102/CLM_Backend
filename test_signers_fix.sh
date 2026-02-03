#!/bin/bash

# Test the signers fix for Firma integration

TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test"}' | jq -r '.access' 2>/dev/null)

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
  echo "❌ Failed to get authentication token"
  exit 1
fi

CONTRACT_ID="548c8ed9-39a2-4b2f-9004-398b8bd6deba"

echo "✅ Token obtained"
echo ""
echo "================================================"
echo "TEST FIX #2: Upload with Signers"
echo "================================================"
echo "Testing upload endpoint with signers parameter..."
echo ""

UPLOAD_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/v1/firma/contracts/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"contract_id\": \"$CONTRACT_ID\",
    \"document_name\": \"NDA Test Contract\",
    \"signers\": [
      {\"name\": \"John Doe\", \"email\": \"john@example.com\"},
      {\"name\": \"Jane Smith\", \"email\": \"jane@example.com\"}
    ],
    \"signing_order\": \"sequential\"
  }")

echo "Response:"
echo "$UPLOAD_RESPONSE" | jq '.'
echo ""

FIRMA_DOC_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.firma_document_id' 2>/dev/null)
SIGNERS_ADDED=$(echo "$UPLOAD_RESPONSE" | jq -r '.signers_added' 2>/dev/null)

if [ -z "$FIRMA_DOC_ID" ] || [ "$FIRMA_DOC_ID" = "null" ]; then
  echo "❌ Upload failed - no document ID returned"
  exit 1
fi

echo "✅ Upload successful!"
echo "   Document ID: $FIRMA_DOC_ID"
echo "   Signers added: $SIGNERS_ADDED"

sleep 2

echo ""
echo "================================================"
echo "TEST FIX #3: Send Invites"
echo "================================================"
echo "Sending signing invites (should NOT fail with 'No signers found')..."
echo ""

SEND_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/v1/firma/esign/send/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"contract_id\": \"$CONTRACT_ID\",
    \"signers\": [
      {\"name\": \"John Doe\", \"email\": \"john@example.com\"},
      {\"name\": \"Jane Smith\", \"email\": \"jane@example.com\"}
    ]
  }")

echo "Response:"
echo "$SEND_RESPONSE" | jq '.'
echo ""

# Check for errors
if echo "$SEND_RESPONSE" | jq . 2>/dev/null | grep -q "No signers found"; then
  echo "❌ FAILED: Still getting 'No signers found' error"
  echo "   This means recipients were NOT added at upload time"
  exit 1
fi

if echo "$SEND_RESPONSE" | jq . 2>/dev/null | grep -qi "error"; then
  ERROR=$(echo "$SEND_RESPONSE" | jq -r '.error' 2>/dev/null)
  echo "❌ Error in response: $ERROR"
  exit 1
fi

echo "✅ SUCCESS: Invites sent without 'No signers found' error!"
echo "   This confirms recipients were successfully added at upload time"
echo ""
echo "================================================"
echo "All tests PASSED! Fixes #2 and #3 are working!"
echo "================================================"
