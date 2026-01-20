import os
import sys
import django
import requests
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.utils import timezone
from contracts.models import SignNowCredential

CLIENT_ID = '5f2b0125c6437bf6a3db5d0802dc804d'
CLIENT_SECRET = 'dc2f8d0ffbbb26cc13d8cd503e3cd249'
AUTH_CODE = '59533e0b74f52ec5e2a76386fcf12f6e887d0ddc00b1639ca560a902b6e0ce44'

print('Exchanging authorization code for access token...')

payload = {
    'grant_type': 'authorization_code',
    'code': AUTH_CODE,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'redirect_uri': 'http://localhost:11000/callback'
}

response = requests.post('https://api.signnow.com/oauth2/token', data=payload, timeout=10)
print(f'Status: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    access_token = data.get('access_token')
    refresh_token = data.get('refresh_token', '')
    expires_in = data.get('expires_in', 3600)
    
    print(f'✅ SUCCESS!')
    print(f'Access token: {access_token[:40]}...')
    print(f'Refresh token: {refresh_token[:40]}...')
    print(f'Expires in: {expires_in} seconds ({expires_in/3600:.1f} hours)')
    
    cred = SignNowCredential.objects.first()
    cred.access_token = access_token
    cred.refresh_token = refresh_token
    cred.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
    cred.last_refreshed_at = timezone.now()
    cred.save()
    
    print(f'\n✅ Database updated!')
    print(f'Token expires at: {cred.token_expires_at}')
    print('\n✅ READY FOR REAL-TIME SIGNATURE POLLING!')
else:
    print(f'❌ Failed: {response.text}')
