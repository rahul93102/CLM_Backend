# Firma Integration - Critical Fixes Applied ✅

**Date**: February 3, 2026
**Status**: Fixed and Ready for Testing
**Severity**: Critical - Workflow Breaking Issues

---

## Executive Summary

Three critical bugs in Firma integration have been identified and fixed:

1. **Database Schema** - Status field too small (20 → 50 chars)
2. **Recipient Handling** - Recipients added at wrong time in workflow
3. **API Workflow** - Upload/invite sequence incompatible with Firma API

All fixes applied. Migration created. Ready for deployment and testing.

---

## Issues Fixed

### Issue #1: Database Field Truncation ❌→✅

**Symptom**: 
```
django.db.utils.DataError: value too long for type character varying(20)
```

**Cause**: FirmaSignatureContract.status field max_length=20 too small

**Fix**: 
- Updated models.py: max_length=20 → max_length=50
- Created migration 0009_expand_firma_status_field.py

**Status**: ✅ Fixed

---

### Issue #2: Recipients Not Added to Signing Request ❌→✅

**Symptom**:
```
POST /signing-request-api/signing-requests/{id}/send
Status: 400 | Body: {"error":"No signers found for this signing request"}
```

**Cause**: Recipients were never added to the signing request at creation time

**Fix Applied**:
1. Refactored `upload_document()` to accept recipients parameter
2. Refactored `create_invite()` to only send (not add recipients)
3. Refactored `_ensure_uploaded()` to convert signers before upload
4. Updated workflow: Signers → Convert → Upload WITH recipients → Send

**Files Changed**:
- contracts/firma_service.py (upload_document + create_invite methods)
- contracts/firma_views.py (_ensure_uploaded method)

**Status**: ✅ Fixed

---

### Issue #3: Recipient Lookup Failing ❌→✅

**Symptom**:
```
Could not find signing_request_user_id for suhaib96886@gmail.com in request ...
```

**Cause**: Recipients array was empty because they were never added during upload

**Fix**: With recipients now added at upload time, fetch returns populated array

**Status**: ✅ Fixed (depends on Issue #2)

---

## Code Changes

### Change #1: Database Model (contracts/models.py)

```python
# Line 611 - FirmaSignatureContract.status field
# BEFORE
status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)

# AFTER
status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft', db_index=True)
```

### Change #2: Upload Document Service (contracts/firma_service.py)

```python
# Added recipients parameter to upload_document()
def upload_document(
    self, 
    pdf_bytes: bytes, 
    document_name: str, 
    recipients: List[Dict[str, Any]] = None  # NEW PARAMETER
) -> Dict[str, Any]:
    """Create signing request with document and recipients."""
    payload = {
        'name': document_name,
        'document': base64_pdf,
        'recipients': recipients or []  # Recipients added at creation time
    }
```

### Change #3: Create Invite Service (contracts/firma_service.py)

```python
# Changed from "add recipients + send" to "send only"
def create_invite(self, document_id: str, signers: List[Dict[str, str]], ...) -> Dict[str, Any]:
    """Send signing invites for existing signing request."""
    # Only calls /send endpoint (no payload)
    # Recipients should already be in signing request from upload
    resp = self._request('POST', url, json={})
```

### Change #4: Ensure Uploaded (contracts/firma_views.py)

```python
# NEW: Accept signers parameter and convert before upload
def _ensure_uploaded(
    *, 
    contract: Contract, 
    document_name: str, 
    signers=None,  # NEW
    signing_order: str = 'sequential'  # NEW
) -> FirmaSignatureContract:
    # Convert signers to Firma format BEFORE upload
    recipients = []
    if signers:
        for idx, signer in enumerate(signers):
            recipient = {
                'first_name': first_name,
                'last_name': last_name,
                'email': signer['email'],
                'designation': 'Signer',
                'order': idx + 1 if signing_order == 'sequential' else 0,
            }
            recipients.append(recipient)
    
    # Pass recipients to upload
    upload_res = service.upload_document(pdf_bytes, document_name, recipients=recipients)
```

### Change #5: Migration (contracts/migrations/0009_expand_firma_status_field.py)

```python
# NEW FILE - Database migration to expand status field
class Migration(migrations.Migration):
    dependencies = [
        ("contracts", "0008_alter_signingauditlog_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="firmasignaturecontract",
            name="status",
            field=models.CharField(
                max_length=50,  # Changed from 20
                choices=[...],
                db_index=True,
                default="draft",
            ),
        ),
    ]
```

---

## Deployment Instructions

### Step 1: Verify Code Changes
```bash
cd /Users/vishaljha/Desktop/SK/CLM_Backend
git diff contracts/models.py contracts/firma_service.py contracts/firma_views.py
# Should show all the changes listed above
```

### Step 2: Apply Migration
```bash
python manage.py migrate contracts
# Should apply migration: 0009_expand_firma_status_field
```

### Step 3: Restart Backend
```bash
pkill -f "runserver"
python manage.py runserver 0.0.0.0:8000
```

### Step 4: Verify Backend Started
```bash
tail -50 /tmp/backend.log | grep -E "(System check|migrations|Watching for file changes)"
# Should show no errors
```

---

## Testing Plan

### Test 1: Simple Upload (No Signers)
```bash
curl -X POST http://localhost:8000/api/v1/firma/contracts/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"contract_id": "...", "document_name": "Test"}'

Expected: HTTP 201, firma_document_id returned
```

### Test 2: Upload WITH Signers (MAIN TEST)
```bash
curl -X POST http://localhost:8000/api/v1/firma/contracts/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "contract_id": "...",
    "document_name": "Test",
    "signers": [{"name": "John", "email": "john@test.com"}]
  }'

Expected: HTTP 201, firma_document_id returned, recipients in Firma request
Check logs: "Creating signing request ... with 1 recipients"
```

### Test 3: Send Invites (CRITICAL TEST)
```bash
curl -X POST http://localhost:8000/api/v1/firma/esign/send/ \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "contract_id": "...",
    "signers": [{"name": "John", "email": "john@test.com"}]
  }'

Expected: HTTP 200, "Invites sent successfully"
NOT Expected: "No signers found" error
```

### Test 4: Get Signing URL
```bash
curl -X GET 'http://localhost:8000/api/v1/firma/esign/signing-url/{id}/?signer_email=john@test.com' \
  -H "Authorization: Bearer $TOKEN"

Expected: HTTP 200, signing_link with https://app.firma.dev/signing/...
NOT Expected: "Could not find signing_request_user_id" warning
```

---

## Validation Checklist

- [ ] Migration applied without errors
- [ ] Backend starts without errors
- [ ] Database field expanded to 50 chars
- [ ] Upload with signers works (HTTP 201)
- [ ] Invites send without "No signers found" error
- [ ] Signing URLs generated correctly
- [ ] Full workflow: upload → send → sign → download works
- [ ] No "value too long for type character varying" errors
- [ ] Logs show recipients being passed to Firma

---

## Rollback Plan (if needed)

```bash
# Undo migration
python manage.py migrate contracts 0008_alter_signingauditlog_options_and_more

# Revert code changes (git)
git checkout contracts/models.py contracts/firma_service.py contracts/firma_views.py

# Restart backend
pkill -f "runserver"
python manage.py runserver 0.0.0.0:8000
```

---

## Expected Results After Fix

✅ Upload contract with recipients to Firma API
✅ Firma creates signing request with all signers
✅ Send invites triggers emails to recipients
✅ Signers receive notification emails
✅ Signers get individual signing URLs
✅ Status field accepts any value up to 50 chars
✅ Complete end-to-end signing workflow functional

---

## Key Files Modified

| File | Change | Type |
|------|--------|------|
| contracts/models.py | Status field expansion | Model |
| contracts/firma_service.py | Recipient parameter + workflow fix | Service |
| contracts/firma_views.py | Signer conversion before upload | View |
| contracts/migrations/0009_expand_firma_status_field.py | NEW: Database migration | Migration |

---

## Testing Documentation

See [TEST_FIRMA_FIXES.sh](TEST_FIRMA_FIXES.sh) for complete testing guide with commands.

See [FIRMA_CRITICAL_FIXES.md](FIRMA_CRITICAL_FIXES.md) for detailed technical analysis.

---

## Next Steps After Verification

1. Run full test suite to ensure no regressions
2. Test with real Firma account and signers
3. Verify email notifications are sent
4. Confirm signed PDF download works
5. Deploy to production

---

## Summary

**Critical workflow-breaking bugs** in Firma integration have been fixed:
- Database schema expanded to handle longer status values
- Recipients now added at correct point in workflow (during upload, not after)
- API workflow refactored to match Firma's requirements

**All changes backward compatible** - endpoints unchanged, only internal logic modified.

**Ready for deployment** - migration created, code complete, ready for testing.

