#!/bin/bash

# Get auth token
TOKEN=$(DJANGO_SETTINGS_MODULE=clm_backend.settings python -c "import django; django.setup(); from authentication.models import User; from rest_framework_simplejwt.tokens import RefreshToken; user = User.objects.filter(email='test@example.com').first() or User.objects.create_user('test@example.com', 'testpass123'); refresh = RefreshToken.for_user(user); print(str(refresh.access_token))" 2>&1 | tail -1)

echo "Token: $TOKEN"
echo ""

# Test upload endpoint with new JSON format
echo "Testing upload endpoint with base64 PDF..."
curl -v -X POST http://localhost:8000/api/v1/firma/contracts/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "0ddba3c2-0721-4c59-8da3-03af21b70fb3",
    "document_name": "Test Contract Refactored"
  }' 2>&1

echo ""
echo "Test complete"
