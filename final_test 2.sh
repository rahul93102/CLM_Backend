#!/bin/bash

# Firma Integration - Signers Fix Test

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcwMTkyNjAwLCJpYXQiOjE3NzAxMDYyMDAsImp0aSI6ImRmYmJiYTU3NmUyYjRkYWJhZDI0OGMyYzYyMzE0YmYxIiwidXNlcl9pZCI6IjQyNzg1ZjQ2LTg4ZDMtNGFiYy1hYzY2LTNmZTA5MjNhNzg2ZCJ9.VHM9xEPkM2SzlfYWZ07Kajkp3iTuJVgaxdQHu1jZs1s"

CONTRACT_ID="548c8ed9-39a2-4b2f-9004-398b8bd6deba"

echo "================================================"
echo "TEST: Upload with Signers (Fix #2)"
echo "================================================"

UPLOAD=$(curl -s -X POST http://127.0.0.1:8000/api/v1/firma/contracts/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"contract_id\": \"$CONTRACT_ID\",
    \"document_name\": \"Test Contract\",
    \"signers\": [
      {\"name\": \"John Doe\", \"email\": \"john@example.com\"},
      {\"name\": \"Jane Smith\", \"email\": \"jane@example.com\"}
    ]
  }")

echo "$UPLOAD" | jq '.'

FIRMA_ID=$(echo "$UPLOAD" | jq -r '.firma_document_id')
SIGNERS=$(echo "$UPLOAD" | jq -r '.signers_added')

echo ""
echo "✅ Upload result:"
echo "   Document ID: $FIRMA_ID"
echo "   Signers added: $SIGNERS"

sleep 2

echo ""
echo "================================================"
echo "TEST: Send Invites (Fix #3)"
echo "================================================"

SEND=$(curl -s -X POST http://127.0.0.1:8000/api/v1/firma/esign/send/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"contract_id\": \"$CONTRACT_ID\",
    \"signers\": [
      {\"name\": \"John Doe\", \"email\": \"john@example.com\"},
      {\"name\": \"Jane Smith\", \"email\": \"jane@example.com\"}
    ]
  }")

echo "$SEND" | jq '.'

if echo "$SEND" | grep -q "No signers found"; then
  echo ""
  echo "❌ FAILED: 'No signers found' error still appears"
else
  echo ""
  echo "✅ SUCCESS: No 'No signers found' error!"
fi
