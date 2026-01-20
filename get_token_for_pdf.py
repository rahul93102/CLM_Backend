#!/usr/bin/env python3
"""Get JWT token for PDF generation with real backend API calls"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
sys.path.insert(0, '/Users/vishaljha/CLM_Backend')

django.setup()

import requests
from django.contrib.auth import get_user_model

User = get_user_model()

def get_token_from_api(email, password):
    """Get JWT token from authentication API"""
    try:
        token_url = "http://localhost:11000/api/auth/token/"
        
        print(f"🔐 Requesting token from: {token_url}")
        print(f"   Email: {email}")
        
        response = requests.post(token_url, json={
            'email': email,
            'password': password
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access')
            refresh = data.get('refresh')
            
            if token:
                print(f"\n✅ Token obtained successfully!")
                print(f"\n🔑 Access Token:")
                print(f"   {token}\n")
                
                if refresh:
                    print(f"🔄 Refresh Token:")
                    print(f"   {refresh}\n")
                
                return token
            else:
                print(f"❌ No token in response: {data}")
                return None
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting token: {e}")
        return None

def create_test_user_if_needed():
    """Create a test user if it doesn't exist"""
    try:
        email = "test@example.com"
        password = "TestPassword123"
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
            print(f"✅ Test user already exists: {email}")
            return email, password
        except User.DoesNotExist:
            print(f"📝 Creating test user: {email}")
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name="Test",
                last_name="User"
            )
            print(f"✅ Test user created successfully")
            return email, password
            
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return None, None

def main():
    print("\n" + "="*70)
    print("JWT TOKEN GENERATOR FOR PDF BACKEND CALLS")
    print("="*70)
    
    if len(sys.argv) > 2:
        # Use provided credentials
        email = sys.argv[1]
        password = sys.argv[2]
    else:
        # Create or use test user
        print("\n📋 Using test credentials...")
        email, password = create_test_user_if_needed()
        
        if not email:
            print("❌ Failed to create test user")
            return None
    
    # Get token
    print(f"\n🔄 Attempting to get token...")
    token = get_token_from_api(email, password)
    
    if token:
        print("\n💡 Usage:")
        print(f"   python3 generate_filled_pdf.py <contract_id> \"{token}\"")
        print(f"\n   Or save to file:")
        print(f"   echo '{token}' > /tmp/token.txt")
        print(f"   python3 generate_filled_pdf.py <contract_id> $(cat /tmp/token.txt)")
        return token
    else:
        print("\n❌ Could not obtain token")
        print("\n📌 Troubleshooting:")
        print("   1. Make sure Django server is running:")
        print("      python3 manage.py runserver 0.0.0.0:11000")
        print("   2. Check if /api/auth/token/ endpoint exists")
        print("   3. Verify credentials are correct")
        return None

if __name__ == '__main__':
    main()
