# Firma Integration - Critical Bug Fixes

## Issues Identified & Fixed

### 1. **Database Schema Issue: Status Field Truncation** ❌→✅

**Error**:
```
django.db.utils.DataError: value too long for type character varying(20)
```

**Root Cause**: 
- FirmaSignatureContract.status field defined as `CharField(max_length=20)`
- Firma's response status values are longer than 20 characters
- Database rejects save operation when status exceeds field length

**Fix Applied**:
- Updated [contracts/models.py](contracts/models.py#L611): Changed `max_length=20` → `max_length=50`
- Created migration: [contracts/migrations/0009_expand_firma_status_field.py](contracts/migrations/0009_expand_firma_status_field.py)

**Impact**: Status field can now accommodate longer values from Firma API

---

### 2. **Recipient Handling: Wrong Workflow** ❌→✅

**Error**:
```
POST /signing-request-api/signing-requests/{id}/send
Status: 400 | Body: {"error":"No signers found for this signing request"}
```

**Root Cause**:
- Current flow: Upload with empty recipients → Try to add recipients via /send endpoint
- Firma API requirement: Recipients must be included at signing request CREATION time
- /send endpoint only triggers emails; it doesn't add recipients
- Result: Trying to send invites to non-existent recipients → 400 error

**Fix Applied**:
Three-part refactoring:

**Part 1** - Update `upload_document()` signature to accept recipients:
```python
# BEFORE
def upload_document(self, pdf_bytes: bytes, document_name: str) -> Dict[str, Any]:
    payload = {
        'name': document_name,
        'document': base64_pdf,
        'recipients': []  # Always empty!
    }

# AFTER
def upload_document(self, pdf_bytes: bytes, document_name: str, recipients: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = {
        'name': document_name,
        'document': base64_pdf,
        'recipients': recipients or []  # Can now include recipients!
    }
```

**Part 2** - Update `create_invite()` to only send (not add recipients):
```python
# BEFORE - Tried to add recipients AND send
def create_invite(self, document_id: str, signers: List[Dict[str, str]], ...):
    payload = {
        'recipients': recipients,  # This fails - recipients already in signing request
    }

# AFTER - Only sends invites
def create_invite(self, document_id: str, signers: List[Dict[str, str]], ...):
    # Just call /send endpoint with no payload
    resp = self._request('POST', url, json={})
    # Gracefully handle "No signers found" error with helpful message
```

**Part 3** - Update `_ensure_uploaded()` to convert signers BEFORE upload:
```python
# BEFORE
def _ensure_uploaded(*, contract: Contract, document_name: str):
    upload_res = service.upload_document(pdf_bytes, document_name)  # No recipients

# AFTER
def _ensure_uploaded(*, contract: Contract, document_name: str, signers=None, signing_order='sequential'):
    # Convert signers to Firma format upfront
    recipients = []
    if signers:
        for idx, signer in enumerate(signers):
            recipients.append({
                'first_name': first_name,
                'last_name': last_name,
                'email': signer['email'],
                'designation': 'Signer',
                'order': idx + 1 if signing_order == 'sequential' else 0,
            })
    # Pass recipients to upload
    upload_res = service.upload_document(pdf_bytes, document_name, recipients=recipients)
```

**Impact**: Recipients are now added at the right time (during creation), enabling successful signing workflows

---

### 3. **Recipient Lookup: Empty Recipients Array** ❌→✅

**Error**:
```
Could not find signing_request_user_id for suhaib96886@gmail.com in request dc521995-7b7a-4e2c-a753-379cfb1c3570
```

**Root Cause**:
- `get_signing_link()` calls `get_document_status()` to fetch recipients
- Recipients array was always empty because they were never added at creation time
- Fallback logic tried to use document_id as signing URL (doesn't work)

**Fix Applied**:
- With recipients now added at upload time, `get_document_status()` will return populated recipients array
- `get_signing_link()` can now find the recipient and extract their signing_request_user_id
- Fallback still available but should not be needed

**Impact**: Signing URLs can now be generated properly with recipient-specific IDs

---

## Workflow Correction

### OLD (Broken) Workflow:
```
1. Upload contract to Firma
   → Creates signing request with EMPTY recipients array
   
2. Try to add signers
   → Calls /send endpoint
   → Firma says "No signers found" (400 error)
   
3. Try to get signing URL
   → Fetch signing request details
   → Recipients array is empty
   → Can't find recipient by email
   → Fallback to document_id (doesn't work)
   
❌ FAILS: No signers, no signing URLs, no workflow
```

### NEW (Fixed) Workflow:
```
1. Convert signers to Firma format
   → Split names, add designation, set order
   
2. Upload contract to Firma WITH recipients
   → Creates signing request with POPULATED recipients array
   → Firma validates and accepts
   
3. Send invites
   → Call /send endpoint
   → Firma sends emails to all recipients
   → Recipients receive signing links
   
4. Get signing URL for specific signer
   → Fetch signing request details
   → Find recipient by email
   → Extract signing_request_user_id
   → Generate https://app.firma.dev/signing/{id}
   
✅ SUCCESS: All signers get emails, can sign documents
```

---

## Code Changes Summary

### File: contracts/models.py
- Line 611: `max_length=20` → `max_length=50` for status field

### File: contracts/firma_service.py
- `upload_document()`: Added `recipients` parameter (default: None)
- `create_invite()`: Changed from "add recipients" to "send invites only"

### File: contracts/firma_views.py
- `_ensure_uploaded()`: Added `signers` and `signing_order` parameters
- Signer conversion logic moved here (before upload, not after)

### File: contracts/migrations/0009_expand_firma_status_field.py
- NEW: Migration to expand status field from 20 to 50 chars

---

## Deployment Steps

### 1. Apply Code Changes
```bash
# Files already modified:
# - contracts/models.py (status field)
# - contracts/firma_service.py (upload_document + create_invite)
# - contracts/firma_views.py (_ensure_uploaded)
# - contracts/migrations/0009_expand_firma_status_field.py (NEW)
```

### 2. Apply Migration
```bash
cd /Users/vishaljha/Desktop/SK/CLM_Backend
python manage.py migrate contracts
```

### 3. Restart Backend
```bash
pkill -f "runserver"
python manage.py runserver 0.0.0.0:8000
```

### 4. Test Upload with Signers
```bash
# Get token
TOKEN=$(DJANGO_SETTINGS_MODULE=clm_backend.settings python -c \
  "import django; django.setup(); ..." | tail -1)

# Create test contract
CONTRACT_ID=$(python manage.py shell -c \
  "from contracts.models import Contract; from authentication.models import User; \
   import uuid; u=User.objects.first(); \
   c=Contract.objects.create(id=str(uuid.uuid4()), tenant_id=u.tenant_id, title='Test', \
   status='draft', created_by=u.user_id); print(c.id)" | grep '-')

# Test upload
curl -X POST http://localhost:8000/api/v1/firma/contracts/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contract_id": "'$CONTRACT_ID'", "document_name": "Test Document"}'
```

---

## Testing Checklist

- [ ] Migration applies without errors
- [ ] Status field accepts longer values (50+ chars)
- [ ] Contract uploads with recipients successfully
- [ ] Invites can be sent without "No signers found" error
- [ ] Signing URLs are generated for each recipient
- [ ] Full workflow: upload → send → signing → download

---

## Expected Behavior After Fix

1. ✅ Upload includes recipients in Firma request
2. ✅ Firma creates signing request with all signers
3. ✅ Send invites triggers emails to recipients
4. ✅ Recipients receive signing notification emails
5. ✅ Signing URLs are unique per recipient
6. ✅ Status can be set to any value up to 50 chars
7. ✅ Signing workflow completes successfully

---

## Key Insights

**Why Recipients Must Be Upfront**:
- Firma's API requires recipients at signing request creation
- This is by design - Firma validates recipient structure during creation
- You cannot add recipients to an existing signing request
- The /send endpoint only triggers email notifications

**Why Schema Change Was Needed**:
- Firma's status values may be longer than 20 characters
- Database field was too restrictive
- Expanding to 50 chars provides comfortable margin

**Why Workflow Refactoring Was Critical**:
- Current code flow was incompatible with Firma's API design
- Had to move recipient preparation upstream (to upload time)
- This required changing how views call the service layer

---

## Files Modified

1. **contracts/models.py** - Expanded status field
2. **contracts/firma_service.py** - Fixed recipient handling
3. **contracts/firma_views.py** - Updated upload workflow
4. **contracts/migrations/0009_expand_firma_status_field.py** - NEW migration

**No breaking changes** - API endpoints remain the same, only internal logic changed.

