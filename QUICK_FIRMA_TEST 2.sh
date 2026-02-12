#!/bin/bash
# Quick Firma Integration Testing Guide

echo "=== Firma.dev Integration - Quick Test Guide ==="
echo ""

# 1. Backend Status
echo "1️⃣ Check Backend Status"
echo "   Command: ps aux | grep runserver | grep -v grep"
echo "   Expected: Django runserver process running on 0.0.0.0:8000"
echo ""

# 2. Get Auth Token
echo "2️⃣ Get Authentication Token"
cat << 'EOF'
   Command:
   TOKEN=$(DJANGO_SETTINGS_MODULE=clm_backend.settings python -c \
     "import django; django.setup(); from authentication.models import User; \
      from rest_framework_simplejwt.tokens import RefreshToken; \
      user = User.objects.filter(email='test@example.com').first() or \
      User.objects.create_user('test@example.com', 'testpass123'); \
      refresh = RefreshToken.for_user(user); \
      print(str(refresh.access_token))" 2>&1 | tail -1)
   
   Result: JWT token stored in $TOKEN variable
EOF
echo ""

# 3. Debug Config
echo "3️⃣ Test Debug Config Endpoint"
cat << 'EOF'
   Command:
   curl -s http://localhost:8000/api/v1/firma/debug/config/ \
     -H "Authorization: Bearer $TOKEN" | jq .
   
   Expected Response:
   {
     "firma_base_url": "https://api.firma.dev",
     "firma_api_key_configured": true,
     "mock_mode": false,
     "api_key_prefix": "firma_fe..."
   }
EOF
echo ""

# 4. Debug Connectivity
echo "4️⃣ Test Connectivity to Firma API"
cat << 'EOF'
   Command:
   curl -s http://localhost:8000/api/v1/firma/debug/connectivity/ \
     -H "Authorization: Bearer $TOKEN" | jq .
   
   Expected Response:
   {
     "status": "success",
     "http_status": 404,
     "url": "https://api.firma.dev/functions/v1/signing-request-api/",
     "response": "404 Not Found (expected for test path)"
   }
EOF
echo ""

# 5. Upload Contract (Create Signing Request)
echo "5️⃣ Upload Contract to Firma"
cat << 'EOF'
   First, create a fresh test contract in Django shell:
   
   python manage.py shell << 'SHELL'
   from contracts.models import Contract
   from authentication.models import User
   import uuid
   
   user = User.objects.first()
   contract = Contract.objects.create(
       id=str(uuid.uuid4()),
       tenant_id=user.tenant_id,
       title='Test Firma Contract',
       status='draft',
       created_by=user.user_id,
   )
   print(f"Contract ID: {contract.id}")
   SHELL
   
   Then test upload:
   
   curl -s -X POST http://localhost:8000/api/v1/firma/contracts/upload/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "contract_id": "CONTRACT_ID_FROM_ABOVE",
       "document_name": "Test Document"
     }' | jq .
   
   Expected Response (HTTP 201):
   {
     "id": "sr_...",
     "name": "Test Document",
     "status": "draft",
     "recipients": []
   }
EOF
echo ""

# 6. Test Backend Logs
echo "6️⃣ View Backend Logs"
cat << 'EOF'
   Command:
   tail -100 /tmp/backend.log | grep -E "(Firma|Creating signing|Signing request)"
   
   Expected: Log entries showing request details
EOF
echo ""

# 7. Restart Backend
echo "7️⃣ Restart Backend (if needed)"
cat << 'EOF'
   Command:
   cd /Users/vishaljha/Desktop/SK/CLM_Backend && \
   pkill -f "runserver" && sleep 2 && \
   python manage.py runserver 0.0.0.0:8000 > /tmp/backend.log 2>&1 &
EOF
echo ""

echo "=== Key Files ==="
echo "  .env config: CLM_Backend/.env"
echo "  Service code: CLM_Backend/contracts/firma_service.py"
echo "  Views: CLM_Backend/contracts/firma_views.py"
echo "  Logs: /tmp/backend.log"
echo ""

echo "=== Key Environment Variables ==="
echo "  FIRMA_BASE_URL=https://api.firma.dev"
echo "  FIRMA_API=firma_fe7fe6ea99bc0d357c125407a7a1273099bfa334cff8d9ee"
echo ""

echo "=== Documentation ==="
echo "  API Status: FIRMA_IMPLEMENTATION_STATUS.md"
echo "  Recent Changes: FIRMA_REFACTORING_COMPLETE.md"
echo "  Completion: COMPLETION_CHECKLIST.md"
echo "  Notes: FIRMA_INTEGRATION_NOTES.md"
