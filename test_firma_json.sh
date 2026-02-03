#!/bin/bash

# Get fresh token
TOKEN=$(DJANGO_SETTINGS_MODULE=clm_backend.settings python -c "import django; django.setup(); from authentication.models import User; from rest_framework_simplejwt.tokens import RefreshToken; user = User.objects.filter(email='test@example.com').first() or User.objects.create_user('test@example.com', 'testpass123'); refresh = RefreshToken.for_user(user); print(str(refresh.access_token))" 2>&1 | tail -1)

echo "Testing upload with JSON (base64 PDF) format..."
curl -s -X POST http://localhost:8000/api/v1/firma/contracts/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "bda2c139-8092-4774-b778-9f1c965011fa",
    "document_name": "Test Firma Upload Refactored 2"
  }' | jq .

echo ""
echo "Done"
