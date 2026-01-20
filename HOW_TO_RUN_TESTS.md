# 🧪 How to Run Actual Tests - Complete Commands

Run these commands to test the complete end-to-end flow with real API responses.

## Prerequisites

```bash
# 1. Start Django Server
cd /Users/vishaljha/CLM_Backend
python manage.py runserver 0.0.0.0:11000
```

## Get JWT Token

```bash
# Get actual access token for testing
python manage.py shell -c "from django.contrib.auth import get_user_model; from rest_framework_simplejwt.tokens import RefreshToken; User = get_user_model(); user, _ = User.objects.get_or_create(email='testuser@example.com', defaults={'user_id': 'test_user_123'}); token = str(RefreshToken.for_user(user).access_token); print('TOKEN=' + token)"
```

## Run Full E2E Test

```bash
# Save the token and run the full test
TOKEN="your_token_here"
cd /Users/vishaljha/CLM_Backend
python3 test_actual_e2e_flow.py
```

## Individual cURL Tests

### 1. Create Contract
```bash
curl -X POST "http://127.0.0.1:11000/api/v1/create/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_type": "nda",
    "data": {
      "date": "2026-01-20",
      "1st_party_name": "TechCorp Inc.",
      "2nd_party_name": "DevSoft LLC",
      "agreement_type": "Mutual",
      "1st_party_relationship": "Technology Company",
      "2nd_party_relationship": "Software Developer",
      "governing_law": "California",
      "1st_party_printed_name": "John Smith",
      "2nd_party_printed_name": "Jane Doe",
      "clauses": [
        {"name": "Confidentiality", "description": "All shared information must remain confidential"},
        {"name": "Non-Compete", "description": "No competing business for 2 years"}
      ]
    }
  }' | jq .
```

Expected Output:
```json
{
  "success": true,
  "contract_id": "...",
  "file_size": 109766,
  "status": 201
}
```

### 2. Get Contract Details (Before Signing)
```bash
CONTRACT_ID="your_contract_id"

curl -X GET "http://127.0.0.1:11000/api/v1/details/?contract_id=$CONTRACT_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.contract.signed'
```

Expected: Empty object `{}`

### 3. Send to SignNow
```bash
curl -X POST "http://127.0.0.1:11000/api/v1/send-to-signnow/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "'$CONTRACT_ID'",
    "signer_email": "jane@devsoft.com",
    "signer_name": "Jane Doe"
  }' | jq .
```

Expected:
```json
{
  "contract_id": "...",
  "signing_link": "https://app.signnow.com/sign/...",
  "message": "Send link to Jane Doe..."
}
```

### 4. Simulate SignNow Webhook
```bash
curl -X POST "http://127.0.0.1:11000/api/v1/webhook/signnow/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "document.signed",
    "document": {
      "contract_id": "'$CONTRACT_ID'",
      "signed_at": "2026-01-20T15:30:45Z",
      "signed_pdf_url": "https://signnow-storage.s3.amazonaws.com/signed_pdf_123.pdf",
      "signers": [{
        "full_name": "Jane Doe",
        "email": "jane@devsoft.com",
        "signed_at": "2026-01-20T15:30:45Z"
      }]
    }
  }' | jq .
```

Expected:
```json
{
  "status": "received",
  "contract_id": "...",
  "message": "Signature received from Jane Doe..."
}
```

### 5. Get Details After Signing
```bash
curl -X GET "http://127.0.0.1:11000/api/v1/details/?contract_id=$CONTRACT_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.contract.signed'
```

Expected:
```json
{
  "status": "signed",
  "signers": [{
    "name": "Jane Doe",
    "email": "jane@devsoft.com",
    "signature_text": "Jane Doe",
    "signed_at": "2026-01-20T15:30:45Z"
  }],
  "signed_at": "2026-01-20T15:30:45Z",
  "pdf_signed": true
}
```

### 6. Download Signed PDF
```bash
curl -X GET "http://127.0.0.1:11000/api/v1/download/?contract_id=$CONTRACT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -o "signed_contract.pdf"

file signed_contract.pdf
# Output: PDF document, version 1.4
```

---

## One-Liner Full Test Script

```bash
#!/bin/bash

# Set up
TOKEN="your_token_here"
BASE="http://127.0.0.1:11000/api/v1"

# 1. Create
echo "1. Creating contract..."
CID=$(curl -s -X POST "$BASE/create/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contract_type":"nda","data":{"date":"2026-01-20","1st_party_name":"TechCorp","2nd_party_name":"DevSoft","agreement_type":"Mutual","1st_party_relationship":"Tech","2nd_party_relationship":"Dev","governing_law":"California","1st_party_printed_name":"John","2nd_party_printed_name":"Jane","clauses":[{"name":"Confidentiality","description":"Keep secret"}]}}' | jq -r '.contract_id')
echo "✅ Contract: $CID"

# 2. Get details (before)
echo "2. Getting details (before signing)..."
curl -s -X GET "$BASE/details/?contract_id=$CID" -H "Authorization: Bearer $TOKEN" | jq '.contract.signed'

# 3. Send to SignNow
echo "3. Sending to SignNow..."
curl -s -X POST "$BASE/send-to-signnow/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"contract_id\":\"$CID\",\"signer_email\":\"jane@devsoft.com\",\"signer_name\":\"Jane Doe\"}" | jq '.signing_link'

# 4. Webhook
echo "4. Simulating SignNow webhook..."
curl -s -X POST "$BASE/webhook/signnow/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"event\":\"document.signed\",\"document\":{\"contract_id\":\"$CID\",\"signed_at\":\"2026-01-20T15:30:45Z\",\"signed_pdf_url\":\"https://signnow.s3/signed.pdf\",\"signers\":[{\"full_name\":\"Jane Doe\",\"email\":\"jane@devsoft.com\",\"signed_at\":\"2026-01-20T15:30:45Z\"}]}}" | jq '.status'

# 5. Get details (after)
echo "5. Getting details (after signing)..."
curl -s -X GET "$BASE/details/?contract_id=$CID" -H "Authorization: Bearer $TOKEN" | jq '.contract.signed.status'

# 6. Download
echo "6. Downloading PDF..."
curl -s -X GET "$BASE/download/?contract_id=$CID" -H "Authorization: Bearer $TOKEN" -o "signed_$CID.pdf"
echo "✅ Downloaded: signed_$CID.pdf ($(wc -c < signed_$CID.pdf) bytes)"
```

---

## Expected Test Results

```
✅ STEP 1: Create Contract - HTTP 201
   Contract ID: b2347b45-ce44-4867-86bd-cb2f87160c5a
   PDF Size: 109,766 bytes

✅ STEP 2: Get Details (Before) - HTTP 200
   Signed Status: {}

✅ STEP 3: Send to SignNow - HTTP 200
   Signing Link: https://app.signnow.com/sign/...

✅ STEP 4: Webhook - HTTP 200
   Message: Signature received from Jane Doe

✅ STEP 5: Get Details (After) - HTTP 200
   Signed Status: signed
   Signer: Jane Doe
   Email: jane@devsoft.com
   Signed At: 2026-01-20T15:30:45Z

✅ STEP 6: Download PDF - HTTP 200
   File Size: 109,766 bytes
   Valid PDF: Yes

═══════════════════════════════════════════════════════════════
ALL TESTS PASSED ✅
═══════════════════════════════════════════════════════════════
```

---

## Common Issues & Solutions

### Token Expired
```bash
# Get a fresh token
python manage.py shell -c "from django.contrib.auth import get_user_model; from rest_framework_simplejwt.tokens import RefreshToken; User = get_user_model(); user, _ = User.objects.get_or_create(email='testuser@example.com'); token = str(RefreshToken.for_user(user).access_token); print(token)"
```

### Server Not Running
```bash
# Start server
python manage.py runserver 0.0.0.0:11000 &
```

### Contract Not Found
```bash
# Make sure contract_id is correct (from Step 1 response)
curl -X GET "http://127.0.0.1:11000/api/v1/details/?contract_id=WRONG_ID"
# Should show 404 if ID is invalid
```

---

## Files for Testing

- Full test script: [test_actual_e2e_flow.py](test_actual_e2e_flow.py)
- Real results document: [ACTUAL_TEST_RESULTS.md](ACTUAL_TEST_RESULTS.md)
- This guide: [HOW_TO_RUN_TESTS.md](HOW_TO_RUN_TESTS.md)
