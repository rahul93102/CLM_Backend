#!/bin/bash
################################################################################
# CURL COMMANDS REFERENCE - REAL API TESTING
# Phase 3, 4, 5 Components with Real Responses
################################################################################

BASE_URL="http://localhost:11000"
API_BASE="$BASE_URL/api/v1"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     CURL COMMANDS FOR REAL-TIME API TESTING               ║"
echo "║     Phase 3 (Metadata), Phase 4 (Classification),         ║"
echo "║     Phase 5 (Obligations)                                  ║"
echo "╚════════════════════════════════════════════════════════════╝"

# ==============================================================================
# PHASE 3: METADATA EXTRACTION - Real Responses
# ==============================================================================

echo -e "\n📋 PHASE 3: METADATA EXTRACTION (30 Tests)"
echo "════════════════════════════════════════════════════════════════"
echo -e "\n🔷 Test 1: Service Agreement Metadata"
echo "COMMAND:"
echo 'curl -X POST http://localhost:11000/api/v1/ai/extract/metadata/ \'
echo '  -H "Content-Type: application/json" \'
echo "  -d '{\"document_text\":\"SERVICE AGREEMENT between TechCorp Inc. (Licensor) and DataSystems LLC (Licensee). Effective: January 1, 2024. Termination: December 31, 2025. Value: \$250,000 USD.\"}'"
echo "EXPECTED OUTPUT:"
curl -s -X POST "$API_BASE/ai/extract/metadata/" \
  -H "Content-Type: application/json" \
  -d '{"document_text":"SERVICE AGREEMENT between TechCorp Inc. (Licensor) and DataSystems LLC (Licensee). Effective: January 1, 2024. Termination: December 31, 2025. Value: $250,000 USD."}' | jq '.'

echo -e "\n🔷 Test 2: NDA Metadata"
echo "COMMAND:"
echo 'curl -X POST http://localhost:11000/api/v1/ai/extract/metadata/ \'
echo '  -H "Content-Type: application/json" \'
echo "  -d '{\"document_text\":\"MUTUAL NON-DISCLOSURE AGREEMENT between GlobalTech Solutions Inc., a Delaware corporation, and InnovateCorp LLC. Effective: February 1, 2024. Termination: February 1, 2027. Consideration: \$100,000 USD.\"}'"
echo "EXPECTED OUTPUT:"
curl -s -X POST "$API_BASE/ai/extract/metadata/" \
  -H "Content-Type: application/json" \
  -d '{"document_text":"MUTUAL NON-DISCLOSURE AGREEMENT between GlobalTech Solutions Inc., a Delaware corporation, and InnovateCorp LLC. Effective: February 1, 2024. Termination: February 1, 2027. Consideration: $100,000 USD."}' | jq '.'

echo -e "\n🔷 Test 3: Employment Contract Metadata"
echo "COMMAND:"
echo 'curl -X POST http://localhost:11000/api/v1/ai/extract/metadata/ \'
echo '  -H "Content-Type: application/json" \'
echo "  -d '{\"document_text\":\"EMPLOYMENT AGREEMENT between ABC Corp (Employer) and John Smith (Employee). Start Date: March 15, 2024. End Date: March 15, 2025. Salary: \$85,000 USD annually.\"}'"
echo "EXPECTED OUTPUT:"
curl -s -X POST "$API_BASE/ai/extract/metadata/" \
  -H "Content-Type: application/json" \
  -d '{"document_text":"EMPLOYMENT AGREEMENT between ABC Corp (Employer) and John Smith (Employee). Start Date: March 15, 2024. End Date: March 15, 2025. Salary: $85,000 USD annually."}' | jq '.'

echo -e "\n🔷 Test 4: Lease Agreement (Real Estate)"
echo "COMMAND:"
echo 'curl -X POST http://localhost:11000/api/v1/ai/extract/metadata/ \'
echo '  -H "Content-Type: application/json" \'
echo "  -d '{\"document_text\":\"COMMERCIAL LEASE AGREEMENT between Landlord LLC and Tenant Corp. Lease Term: 5 years. Start: April 1, 2024. End: March 31, 2029. Monthly Rent: \$5,000.\"}'"
echo "EXPECTED OUTPUT:"
curl -s -X POST "$API_BASE/ai/extract/metadata/" \
  -H "Content-Type: application/json" \
  -d '{"document_text":"COMMERCIAL LEASE AGREEMENT between Landlord LLC and Tenant Corp. Lease Term: 5 years. Start: April 1, 2024. End: March 31, 2029. Monthly Rent: $5,000."}' | jq '.'

echo -e "\n🔷 Test 5: Purchase Agreement"
echo "COMMAND:"
echo 'curl -X POST http://localhost:11000/api/v1/ai/extract/metadata/ \'
echo '  -H "Content-Type: application/json" \'
echo "  -d '{\"document_text\":\"PURCHASE AGREEMENT between Seller Industries and Buyer Manufacturing. Total Price: \$500,000 USD. Delivery Date: June 30, 2024. Warranty: 2 years.\"}'"
echo "EXPECTED OUTPUT:"
curl -s -X POST "$API_BASE/ai/extract/metadata/" \
  -H "Content-Type: application/json" \
  -d '{"document_text":"PURCHASE AGREEMENT between Seller Industries and Buyer Manufacturing. Total Price: $500,000 USD. Delivery Date: June 30, 2024. Warranty: 2 years."}' | jq '.'

# ==============================================================================
# PHASE 4: CLAUSE CLASSIFICATION - Real Responses
# ==============================================================================

echo -e "\n\n📋 PHASE 4: CLAUSE CLASSIFICATION (35 Tests)"
echo "════════════════════════════════════════════════════════════════"
echo -e "\n🔶 Test 31: Confidentiality Clause"
echo "COMMAND:"
echo 'curl -X POST http://localhost:11000/api/v1/ai/classify/ \'
echo '  -H "Content-Type: application/json" \'
echo "  -d '{\"text\":\"The receiving party shall maintain all confidential information in strict confidence and shall not disclose such information to third parties without prior written consent.\"}'"
echo "EXPECTED OUTPUT:"
curl -s -X POST "$API_BASE/ai/classify/" \
  -H "Content-Type: application/json" \
  -d '{"text":"The receiving party shall maintain all confidential information in strict confidence and shall not disclose such information to third parties without prior written consent."}' | jq '.'

echo -e "\n🔶 Test 32: Payment Terms"
echo "COMMAND:"
echo 'curl -X POST http://localhost:11000/api/v1/ai/classify/ \'
echo '  -H "Content-Type: application/json" \'
echo "  -d '{\"text\":\"Licensee shall pay the annual license fee of \$100,000 USD within thirty (30) days of invoice.\"}'"
echo "EXPECTED OUTPUT:"
curl -s -X POST "$API_BASE/ai/classify/" \
  -H "Content-Type: application/json" \
  -d '{"text":"Licensee shall pay the annual license fee of $100,000 USD within thirty (30) days of invoice."}' | jq '.'

echo -e "\n🔶 Test 33: Limitation of Liability"
echo "COMMAND:"
echo 'curl -X POST http://localhost:11000/api/v1/ai/classify/ \'
echo '  -H "Content-Type: application/json" \'
echo "  -d '{\"text\":\"In no event shall either party be liable for indirect, incidental, special, consequential, or punitive damages.\"}'"
echo "EXPECTED OUTPUT:"
curl -s -X POST "$API_BASE/ai/classify/" \
  -H "Content-Type: application/json" \
  -d '{"text":"In no event shall either party be liable for indirect, incidental, special, consequential, or punitive damages."}' | jq '.'

echo -e "\n🔶 Test 34: Termination Clause"
echo "COMMAND:"
echo 'curl -X POST http://localhost:11000/api/v1/ai/classify/ \'
echo '  -H "Content-Type: application/json" \'
echo "  -d '{\"text\":\"This Agreement may be terminated by either party upon ninety (90) days written notice.\"}'"
echo "EXPECTED OUTPUT:"
curl -s -X POST "$API_BASE/ai/classify/" \
  -H "Content-Type: application/json" \
  -d '{"text":"This Agreement may be terminated by either party upon ninety (90) days written notice."}' | jq '.'

echo -e "\n🔶 Test 35: Indemnification Clause"
echo "COMMAND:"
echo 'curl -X POST http://localhost:11000/api/v1/ai/classify/ \'
echo '  -H "Content-Type: application/json" \'
echo "  -d '{\"text\":\"Each party shall indemnify, defend, and hold harmless the other from claims arising from breach.\"}'"
echo "EXPECTED OUTPUT:"
curl -s -X POST "$API_BASE/ai/classify/" \
  -H "Content-Type: application/json" \
  -d '{"text":"Each party shall indemnify, defend, and hold harmless the other from claims arising from breach."}' | jq '.'

echo -e "\n🔶 Test 36: Warranty Clause"
echo "COMMAND:"
echo 'curl -X POST http://localhost:11000/api/v1/ai/classify/ \'
echo '  -H "Content-Type: application/json" \'
echo "  -d '{\"text\":\"Licensor warrants that the Software is free of defects and will perform in material accordance with the Documentation.\"}'"
echo "EXPECTED OUTPUT:"
curl -s -X POST "$API_BASE/ai/classify/" \
  -H "Content-Type: application/json" \
  -d '{"text":"Licensor warrants that the Software is free of defects and will perform in material accordance with the Documentation."}' | jq '.'

echo -e "\n🔶 Test 37: Intellectual Property Rights"
echo "COMMAND:"
echo 'curl -X POST http://localhost:11000/api/v1/ai/classify/ \'
echo '  -H "Content-Type: application/json" \'
echo "  -d '{\"text\":\"All intellectual property remains the exclusive property of Licensor. Licensee may not reverse engineer or decompile.\"}'"
echo "EXPECTED OUTPUT:"
curl -s -X POST "$API_BASE/ai/classify/" \
  -H "Content-Type: application/json" \
  -d '{"text":"All intellectual property remains the exclusive property of Licensor. Licensee may not reverse engineer or decompile."}' | jq '.'

echo -e "\n🔶 Test 38: Force Majeure Clause"
echo "COMMAND:"
echo 'curl -X POST http://localhost:11000/api/v1/ai/classify/ \'
echo '  -H "Content-Type: application/json" \'
echo "  -d '{\"text\":\"Neither party shall be liable for failure to perform due to events beyond reasonable control including natural disasters.\"}'"
echo "EXPECTED OUTPUT:"
curl -s -X POST "$API_BASE/ai/classify/" \
  -H "Content-Type: application/json" \
  -d '{"text":"Neither party shall be liable for failure to perform due to events beyond reasonable control including natural disasters."}' | jq '.'

# ==============================================================================
# PHASE 5: HEALTH CHECKS & SYSTEM VALIDATION
# ==============================================================================

echo -e "\n\n📋 PHASE 5: SYSTEM HEALTH & VALIDATION"
echo "════════════════════════════════════════════════════════════════"

echo -e "\n🟢 Test 68: General Health Check"
echo "COMMAND:"
echo 'curl -X GET http://localhost:11000/health/'
echo "EXPECTED OUTPUT:"
curl -s -X GET "$API_BASE/health/" | jq '.'

echo -e "\n🟢 Test 69: Database Health"
echo "COMMAND:"
echo 'curl -X GET http://localhost:11000/health/database/'
echo "EXPECTED OUTPUT:"
curl -s -X GET "$API_BASE/health/database/" | jq '.'

echo -e "\n🟢 Test 70: Cache Health"
echo "COMMAND:"
echo 'curl -X GET http://localhost:11000/health/cache/'
echo "EXPECTED OUTPUT:"
curl -s -X GET "$API_BASE/health/cache/" | jq '.'

echo -e "\n\n═══════════════════════════════════════════════════════════════"
echo "QUICK COPY-PASTE COMMANDS FOR MANUAL TESTING"
echo "═══════════════════════════════════════════════════════════════"

echo -e "\n📌 Extract Metadata from Service Agreement:"
echo 'curl -s -X POST http://localhost:11000/api/v1/ai/extract/metadata/ -H "Content-Type: application/json" -d "{\"document_text\":\"SERVICE AGREEMENT between Company A (Licensor) and Company B (Licensee). Effective: January 1, 2024. Value: \$500,000.\"}" | jq'

echo -e "\n📌 Classify Confidentiality Clause:"
echo 'curl -s -X POST http://localhost:11000/api/v1/ai/classify/ -H "Content-Type: application/json" -d "{\"text\":\"The receiving party shall maintain confidentiality and shall not disclose without written consent.\"}" | jq'

echo -e "\n📌 Check API Health:"
echo 'curl -s http://localhost:11000/health/ | jq'

echo -e "\n📌 Batch Test - All Metadata Tests (30):"
echo 'bash /Users/vishaljha/CLM_Backend/test_100_comprehensive.sh 2>&1 | grep "Test [0-9]*:" | head -30'

echo -e "\n📌 Batch Test - All Classification Tests (35):"
echo 'bash /Users/vishaljha/CLM_Backend/test_100_comprehensive.sh 2>&1 | grep "Test [0-9]*:" | tail -65 | head -35'

echo -e "\n📌 Full 100-Test Suite:"
echo 'bash /Users/vishaljha/CLM_Backend/test_100_comprehensive.sh 2>&1 | tee results.log'

echo -e "\n═══════════════════════════════════════════════════════════════"
echo "API ENDPOINT DOCUMENTATION"
echo "═══════════════════════════════════════════════════════════════"

cat << 'EOF'

METADATA EXTRACTION ENDPOINT
────────────────────────────────────────
Endpoint: POST /api/v1/ai/extract/metadata/
Purpose:  Extract structured metadata from contracts
Input:    JSON with "document_text" field
Output:   Parties, dates, values, contract type

Request Format:
{
  "document_text": "SERVICE AGREEMENT between..."
}

Response Format:
{
  "parties": [
    {"name": "Company A", "role": "Licensor"},
    {"name": "Company B", "role": "Licensee"}
  ],
  "effective_date": "2024-01-01",
  "termination_date": "2025-12-31",
  "contract_value": {
    "amount": 500000,
    "currency": "USD"
  },
  "contract_type": "Service Agreement"
}


CLAUSE CLASSIFICATION ENDPOINT
────────────────────────────────────────
Endpoint: POST /api/v1/ai/classify/
Purpose:  Classify contract clauses by type
Input:    JSON with "text" field (clause text)
Output:   Classification, confidence score

Request Format:
{
  "text": "The receiving party shall maintain..."
}

Response Format:
{
  "label": "Confidentiality",
  "category": "Legal",
  "confidence": 0.769
}

Supported Clause Types:
- Confidentiality (NDAs, secrecy clauses)
- Payment Terms (fees, billing, invoicing)
- Limitation of Liability (damage caps)
- Termination (exit conditions)
- Indemnification (hold harmless)
- Warranty (representations)
- Intellectual Property (IP rights)
- Force Majeure (unforeseen events)
- Governing Law (jurisdiction)
- Entire Agreement (integration)
- Non-Compete (restrictions)
- Insurance (coverage requirements)
- Audit Rights (inspection)
- Data Protection (privacy, GDPR)
- Dispute Resolution (escalation)
- Severability (legal separation)
- Counterparts (execution)
- Assignment (transfer)
- Notices (communication)
- Renewal (extension)
- SLA (service levels)
- Regulatory (compliance)
- Limitation of Use (scope)
- Support (help services)
- Acceptance (approval)
- Cost Allocation (expense distribution)
- Remedies (breach solutions)
- Professional Services (consulting)
- Third-Party (external refs)
- Waiver (relief)
And more...


HEALTH CHECK ENDPOINTS
────────────────────────────────────────
GET /health/               - Overall system status
GET /health/database/      - PostgreSQL connectivity
GET /health/cache/         - Redis connectivity
GET /health/metrics/       - Performance metrics

Response Format:
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "database": "operational",
  "cache": "operational"
}


TESTING BEST PRACTICES
────────────────────────────────────────
1. Use jq for JSON parsing: curl ... | jq '.'
2. Measure latency: time curl ...
3. Test edge cases: empty strings, special chars, very long text
4. Verify all required fields are present
5. Check confidence scores (0.0-1.0 range)
6. Monitor response times <5 seconds
7. Validate JSON schema compliance
8. Test with various contract types
9. Test multi-party scenarios
10. Test international content

SAMPLE TEST CASES
────────────────────────────────────────

✅ Simple Service Agreement
✅ Multi-party Joint Venture
✅ Employment Contract
✅ Real Estate Lease
✅ Purchase Agreement
✅ Software License
✅ Loan Agreement
✅ Insurance Policy
✅ Master Service Agreement
✅ Government Contract
✅ International Agreement
✅ Complex Confidentiality
✅ Payment Escalation Terms
✅ Conditional Obligations
✅ Multi-Exhibit Agreement
EOF

echo ""
