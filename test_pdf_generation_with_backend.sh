#!/bin/bash
# Test PDF generation with real SignNow backend calls

echo "════════════════════════════════════════════════════════════════"
echo "📄 TESTING PDF GENERATION WITH REAL SIGNNOW BACKEND"
echo "════════════════════════════════════════════════════════════════"

cd /Users/vishaljha/CLM_Backend

echo ""
echo "🔑 Step 1: Generating JWT Token..."
TOKEN=$(python3 get_api_token.py 2>&1 | grep "Access Token" -A 1 | tail -1 | tr -d ' ')

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to generate token"
    exit 1
fi

echo "✅ Token generated successfully"
echo ""

echo "🔄 Step 2: Generating PDF with real backend calls..."
echo ""
python3 generate_filled_pdf.py aae65358-f709-4994-ab28-f4e2874c35e3 "$TOKEN"

echo ""
echo "✅ Test complete!"
echo ""
echo "📋 Generated PDF: /Users/vishaljha/CLM_Backend/signed_nda.pdf"
