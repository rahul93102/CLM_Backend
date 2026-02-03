# Fix Summary - Upload Endpoint Missing Signers Parameter

## The Problem

The initial upload endpoint was NOT accepting the `signers` parameter that was needed to add recipients to the Firma signing request at creation time.

```python
# BEFORE - Upload endpoint signature
def firma_upload_contract(request):
    contract_id = request.data.get('contract_id')
    document_name = request.data.get('document_name')
    
    # NO signers parameter!
    # Called without signers:
    record = _ensure_uploaded(contract=contract, document_name=str(document_name))
    # ↓ Result: Recipients empty → "No signers found" error on /send
```

## The Solution

Modified the upload endpoint to:
1. Accept `signers` parameter from request
2. Accept `signing_order` parameter from request  
3. Pass both to `_ensure_uploaded()` which then passes to `upload_document()`

```python
# AFTER - Upload endpoint signature
def firma_upload_contract(request):
    contract_id = request.data.get('contract_id')
    document_name = request.data.get('document_name') or getattr(contract, 'title', 'Contract')
    signers = request.data.get('signers') or []  # ← NEW
    signing_order = request.data.get('signing_order') or 'sequential'  # ← NEW
    
    # Now pass signers through the chain:
    record = _ensure_uploaded(
        contract=contract,
        document_name=str(document_name),
        signers=signers,  # ← PASSED
        signing_order=signing_order  # ← PASSED
    )
```

## Complete Flow After Fix

```
1. API Request (includes signers):
   POST /api/v1/firma/contracts/upload/
   {
     "contract_id": "...",
     "document_name": "...",
     "signers": [
       {"name": "John Doe", "email": "john@example.com"},
       {"name": "Jane Smith", "email": "jane@example.com"}
     ]
   }

2. Upload Endpoint (in firma_views.py):
   - Extracts contract_id, document_name, signers, signing_order
   - Calls: _ensure_uploaded(contract, document_name, signers, signing_order)

3. _ensure_uploaded() (in firma_views.py):
   - Converts signers to Firma format (first_name, last_name, email, designation, order)
   - Creates recipients list with converted data
   - Calls: upload_document(pdf_bytes, name, recipients=recipients)

4. upload_document() (in firma_service.py):
   - Builds payload with recipients included:
     {
       "name": "...",
       "document": "base64pdf",
       "recipients": [
         {"first_name": "John", "last_name": "Doe", "email": "john@example.com", ...},
         {"first_name": "Jane", "last_name": "Smith", "email": "jane@example.com", ...}
       ]
     }
   - POSTs to Firma API

5. Firma API Response:
   - Creates signing request WITH recipients populated
   - Returns: {"id": "doc-id", "recipients": [...]}

6. Send Invites (via /send endpoint):
   - Recipients already in signing request
   - /send endpoint works successfully
   - Signers receive emails with signing links
   ✓ SUCCESS
```

## Files Modified

### [contracts/firma_views.py](contracts/firma_views.py#L238-L275)

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def firma_upload_contract(request):
    """Upload contract PDF to Firma.

    Request:
    {
      "contract_id": "uuid",
      "document_name": "Optional name",
      "signers": [{"name": "John Doe", "email": "john@example.com"}, ...],  # ← NEW
      "signing_order": "sequential" or "parallel"  # ← NEW
    }
    """
    contract_id = request.data.get('contract_id')
    if not contract_id:
        return Response({'error': 'contract_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    contract = get_object_or_404(Contract, id=contract_id)
    if hasattr(contract, 'firma_signature_contract'):
        existing = contract.firma_signature_contract
        return Response(
            {
                'error': 'Contract already uploaded for Firma signing',
                'firma_document_id': existing.firma_document_id,
                'status': existing.status,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    document_name = request.data.get('document_name') or getattr(contract, 'title', 'Contract')
    signers = request.data.get('signers') or []  # ← NEW: Extract from request
    signing_order = request.data.get('signing_order') or 'sequential'  # ← NEW: Extract from request
    
    logger.info(f"Firma upload starting: contract_id={contract_id}, document_name={document_name}, signers={len(signers)}")

    try:
        # ← CHANGED: Now pass signers and signing_order
        record = _ensure_uploaded(
            contract=contract,
            document_name=str(document_name),
            signers=signers,  # ← ADDED
            signing_order=signing_order  # ← ADDED
        )
        
        logger.info(f"Firma upload succeeded: contract_id={contract_id}, firma_document_id={record.firma_document_id}")

        return Response(
            {
                'success': True,
                'contract_id': str(contract_id),
                'firma_document_id': record.firma_document_id,
                'status': record.status,
                'signers_added': len(signers),  # ← NEW: Confirm count in response
                'message': 'Contract uploaded successfully' + (f' with {len(signers)} signers' if signers else ''),  # ← UPDATED
            },
            status=status.HTTP_201_CREATED,
        )
    # ... error handling ...
```

## Test Results

### ✅ Test 1: Upload with Signers
**Input:**
```bash
POST /api/v1/firma/contracts/upload/
Authorization: Bearer $TOKEN
Content-Type: application/json

{
  "contract_id": "548c8ed9-39a2-4b2f-9004-398b8bd6deba",
  "document_name": "Test with Signers",
  "signers": [
    {"name": "John Doe", "email": "john@example.com"},
    {"name": "Jane Smith", "email": "jane@example.com"}
  ]
}
```

**Output (HTTP 201):**
```json
{
  "success": true,
  "contract_id": "548c8ed9-39a2-4b2f-9004-398b8bd6deba",
  "firma_document_id": "aad1d08e-3094-4d8e-9910-632b92d2ee93",
  "status": "draft",
  "signers_added": 2,
  "message": "Contract uploaded successfully with 2 signers"
}
```

✅ **SUCCESS**: Recipients added at upload time

### ✅ Test 2: Send Invites (No More "No Signers Found" Error)
**Input:**
```bash
POST /api/v1/firma/esign/send/
Authorization: Bearer $TOKEN
Content-Type: application/json

{
  "contract_id": "548c8ed9-39a2-4b2f-9004-398b8bd6deba",
  "signers": [
    {"name": "John Doe", "email": "john@example.com"},
    {"name": "Jane Smith", "email": "jane@example.com"}
  ]
}
```

**Output (HTTP 200):**
```json
{
  "success": true,
  "contract_id": "548c8ed9-39a2-4b2f-9004-398b8bd6deba",
  "status": "sent",
  "signers_invited": 2,
  "expires_at": "2026-03-05T08:10:46.867216+00:00",
  "message": "Invitations sent successfully"
}
```

✅ **SUCCESS**: Invites sent without "No signers found" error

---

## Root Cause Analysis

The issue occurred because:

1. **Upload endpoint design was incomplete**: The endpoint didn't accept signers as a parameter
2. **No recipient conversion at upload**: Signers weren't converted to Firma format before upload
3. **Firma API requirement**: Firma requires recipients at creation time, not added after
4. **Missing chain communication**: The upload endpoint wasn't passing through to _ensure_uploaded which does the conversion

**Why the fix works:**
- Upload endpoint now accepts `signers` parameter
- Passes it to `_ensure_uploaded()` which converts to Firma format
- Recipients included in Firma signing request payload at creation time
- /send endpoint finds recipients and sends emails successfully

---

## Summary

**Changed**: 1 file ([contracts/firma_views.py](contracts/firma_views.py))  
**Lines Modified**: ~15  
**Breaking Changes**: None (backwards compatible - signers optional)  
**Tests Passed**: ✅ Both upload with signers and send invites working  
**Status**: ✅ PRODUCTION READY

