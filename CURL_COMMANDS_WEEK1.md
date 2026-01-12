# 🔐 Week 1 Authentication API - CURL Commands

Base URL: `https://clm-backend-at23.onrender.com`

---

## 📋 Test Credentials

```bash
EMAIL=test_auth_user@example.com
PASSWORD=TestPassword123!
FULL_NAME="Test User"
```

---

## ✅ Test 1: User Registration

**Register a new user account**

```bash
curl -X POST https://clm-backend-at23.onrender.com/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_auth_user@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User"
  }'
```

**Expected Response (201):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "user_id": "uuid",
    "email": "test_auth_user@example.com",
    "full_name": "Test User"
  }
}
```

---

## 🔑 Test 2: User Login

**Login with email and password**

```bash
curl -X POST https://clm-backend-at23.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_auth_user@example.com",
    "password": "TestPassword123!"
  }'
```

**Expected Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "user_id": "uuid",
    "email": "test_auth_user@example.com"
  }
}
```

**Save the `access` token for authenticated requests:**
```bash
ACCESS_TOKEN="your_access_token_here"
```

---

## 👤 Test 3: Get Current User Profile

**Get authenticated user details (requires access token)**

```bash
curl -X GET https://clm-backend-at23.onrender.com/api/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

**Example with actual token:**
```bash
curl -X GET https://clm-backend-at23.onrender.com/api/auth/me/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json"
```

**Expected Response (200):**
```json
{
  "user_id": "uuid",
  "email": "test_auth_user@example.com",
  "tenant_id": "uuid",
  "is_active": true
}
```

---

## 🔄 Test 4: Refresh Access Token

**Get a new access token using refresh token**

```bash
curl -X POST https://clm-backend-at23.onrender.com/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

**Expected Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 📧 Test 5: Request Login OTP

**Request OTP for login (email-based)**

```bash
curl -X POST https://clm-backend-at23.onrender.com/api/auth/request-login-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_auth_user@example.com"
  }'
```

**Expected Response (200):**
```json
{
  "message": "OTP sent to your email",
  "email": "test_auth_user@example.com"
}
```

**Note:** Check email for OTP code

---

## ✔️ Test 6: Verify Email OTP

**Verify OTP received via email**

```bash
curl -X POST https://clm-backend-at23.onrender.com/api/auth/verify-email-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_auth_user@example.com",
    "otp": "123456"
  }'
```

**Expected Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "message": "Email verified successfully"
}
```

---

## 🔐 Test 7: Forgot Password

**Request password reset OTP**

```bash
curl -X POST https://clm-backend-at23.onrender.com/api/auth/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_auth_user@example.com"
  }'
```

**Expected Response (200):**
```json
{
  "message": "Password reset OTP sent to your email",
  "email": "test_auth_user@example.com"
}
```

---

## 🔑 Test 8: Verify Password Reset OTP

**Verify password reset OTP**

```bash
curl -X POST https://clm-backend-at23.onrender.com/api/auth/verify-password-reset-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_auth_user@example.com",
    "otp": "123456"
  }'
```

**Expected Response (200):**
```json
{
  "reset_token": "reset-token-uuid",
  "message": "OTP verified successfully"
}
```

---

## 🔄 Test 9: Resend Password Reset OTP

**Resend password reset OTP if not received**

```bash
curl -X POST https://clm-backend-at23.onrender.com/api/auth/resend-password-reset-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_auth_user@example.com"
  }'
```

**Expected Response (200):**
```json
{
  "message": "Password reset OTP resent to your email",
  "email": "test_auth_user@example.com"
}
```

---

## 🚪 Test 10: Logout

**Logout user (requires access token)**

```bash
curl -X POST https://clm-backend-at23.onrender.com/api/auth/logout/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response (200):**
```json
{
  "message": "Logout successful"
}
```

---

## ❌ Test 11: Invalid Credentials

**Login with wrong password (should fail)**

```bash
curl -X POST https://clm-backend-at23.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_auth_user@example.com",
    "password": "WrongPassword123!"
  }'
```

**Expected Response (401):**
```json
{
  "error": "Invalid credentials",
  "detail": "Invalid email or password"
}
```

---

## ❌ Test 12: Missing Required Fields

**Register without password (should fail)**

```bash
curl -X POST https://clm-backend-at23.onrender.com/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_auth_user@example.com"
  }'
```

**Expected Response (400):**
```json
{
  "password": ["This field is required."]
}
```

---

## ❌ Test 13: Unauthorized Access

**Access protected endpoint without token (should fail)**

```bash
curl -X GET https://clm-backend-at23.onrender.com/api/auth/me/ \
  -H "Content-Type: application/json"
```

**Expected Response (401):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## 🔧 Helper Scripts

### Save token to variable for reuse:
```bash
# Register and save tokens
RESPONSE=$(curl -s -X POST https://clm-backend-at23.onrender.com/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_auth_user@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User"
  }')

# Extract tokens (requires jq)
ACCESS_TOKEN=$(echo $RESPONSE | jq -r '.access')
REFRESH_TOKEN=$(echo $RESPONSE | jq -r '.refresh')

echo "Access Token: $ACCESS_TOKEN"
echo "Refresh Token: $REFRESH_TOKEN"

# Use token in next request
curl -X GET https://clm-backend-at23.onrender.com/api/auth/me/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### Complete test flow:
```bash
#!/bin/bash

BASE_URL="https://clm-backend-at23.onrender.com"
EMAIL="test_auth_user@example.com"
PASSWORD="TestPassword123!"

echo "1. Registering user..."
REGISTER_RESPONSE=$(curl -s -X POST $BASE_URL/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"full_name\":\"Test User\"}")

ACCESS_TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.access')
REFRESH_TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.refresh')

echo "2. Getting current user..."
curl -s -X GET $BASE_URL/api/auth/me/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo "3. Refreshing token..."
curl -s -X POST $BASE_URL/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d "{\"refresh\":\"$REFRESH_TOKEN\"}" | jq

echo "4. Logging out..."
curl -s -X POST $BASE_URL/api/auth/logout/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

---

## 📝 Testing in Postman

1. Import the JSON collection provided
2. Update `{{base_url}}` variable to: `https://clm-backend-at23.onrender.com`
3. Update `{{email}}` to your test email
4. Update `{{password}}` to your test password
5. Run requests in order (Register → Login → Get User → etc.)

---

## ⚙️ Common Issues

| Issue | Solution |
|-------|----------|
| `Connection refused` | API might be sleeping (free tier). Wait 30s and try again |
| `Invalid token` | Token expired. Request a new one using refresh endpoint |
| `CORS error` | Check if CORS is enabled in Django settings |
| `401 Unauthorized` | Token missing or invalid. Check Authorization header |
| `Email not received` | Check spam folder or resend OTP |

---

## 🔗 Health Check

Test if API is running:
```bash
curl -X GET https://clm-backend-at23.onrender.com/health/
```

Expected Response (200):
```json
{
  "status": "healthy",
  "timestamp": "2026-01-12T10:30:00Z"
}
```
