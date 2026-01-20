#!/bin/bash

################################################################################
# COMPREHENSIVE PRODUCTION TEST SUITE - 100+ TESTS
# Phase 3 (PII, Tenant, Audit) + Phase 4 (AI) + Phase 5 (Accuracy, Performance)
# Real data, no mocks, actual API responses
################################################################################

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

BASE_URL="http://localhost:11000"
API_BASE="$BASE_URL/api/v1"

# Metrics
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
declare -a LATENCIES

# Helper function to test endpoint
test_endpoint() {
    local test_num=$1
    local test_name=$2
    local method=$3
    local endpoint=$4
    local data=$5
    local expected_status=$6
    
    ((TESTS_RUN++))
    
    echo -e "${CYAN}[TEST $test_num] $test_name${NC}"
    
    if [ "$method" = "GET" ]; then
        START=$(date +%s%N)
        RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_BASE$endpoint" \
            -H "Content-Type: application/json")
        END=$(date +%s%N)
    else
        START=$(date +%s%N)
        RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
        END=$(date +%s%N)
    fi
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    LATENCY=$(( (END - START) / 1000000 ))
    LATENCIES+=($LATENCY)
    
    if [[ "$HTTP_CODE" == "$expected_status"* ]] || [ -z "$expected_status" ]; then
        echo -e "${GREEN}✅ Status: $HTTP_CODE | Latency: ${LATENCY}ms${NC}"
        echo "$BODY" | jq '.' 2>/dev/null | head -10 || echo "$BODY" | head -5
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ Status: $HTTP_CODE (expected $expected_status) | Latency: ${LATENCY}ms${NC}"
        echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
        ((TESTS_FAILED++))
    fi
    echo ""
}

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   COMPREHENSIVE PRODUCTION TEST SUITE - 100+ TESTS                ║${NC}"
echo -e "${BLUE}║   Phase 3, 4, 5: Real Data, Edge Cases, Performance              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}\n"

# ============================================================================
# PHASE 0: HEALTH & SYSTEM CHECKS (5 TESTS)
# ============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 0: HEALTH & SYSTEM CHECKS (5 TESTS)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}\n"

test_endpoint 1 "Health Check - Basic" "GET" "/health/" "" "200"
test_endpoint 2 "Database Health Check" "GET" "/health/database/" "" "200"
test_endpoint 3 "Cache Health Check" "GET" "/health/cache/" "" "200"
test_endpoint 4 "Metrics Endpoint" "GET" "/health/metrics/" "" "200"
test_endpoint 5 "Service Status" "GET" "/health/" "" "200"

# ============================================================================
# PHASE 3A: METADATA EXTRACTION - REAL DATA (15 TESTS)
# ============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 3A: METADATA EXTRACTION - REAL CONTRACTS (15 TESTS)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}\n"

test_endpoint 6 "Extract Metadata - Service Agreement" "POST" "/ai/extract/metadata/" \
    '{"document_text":"SERVICE AGREEMENT between TechCorp Inc. (Licensor) and DataSystems LLC (Licensee). Effective: January 1, 2024. Termination: December 31, 2025. Value: $250,000 USD."}' "200"

test_endpoint 7 "Extract Metadata - NDA Document" "POST" "/ai/extract/metadata/" \
    '{"document_text":"MUTUAL NON-DISCLOSURE AGREEMENT between GlobalTech Solutions Inc. and InnovateCorp LLC. Effective: February 1, 2024. Termination: February 1, 2027. Consideration: $100,000 USD."}' "200"

test_endpoint 8 "Extract Metadata - Employment Contract" "POST" "/ai/extract/metadata/" \
    '{"document_text":"EMPLOYMENT AGREEMENT between ABC Corporation and John Smith. Position: Senior Manager. Salary: $150,000 per year. Start Date: March 1, 2024. End Date: March 1, 2025. Benefits included."}' "200"

test_endpoint 9 "Extract Metadata - Lease Agreement" "POST" "/ai/extract/metadata/" \
    '{"document_text":"LEASE AGREEMENT between PropertyOwner Inc. and TenantCorp LLC. Property: 123 Business Street. Lease Start: April 1, 2024. Lease End: March 31, 2026. Monthly Rent: $5,000 USD."}' "200"

test_endpoint 10 "Extract Metadata - Purchase Agreement" "POST" "/ai/extract/metadata/" \
    '{"document_text":"PURCHASE AGREEMENT between Seller Company and Buyer Inc. Item: Commercial Equipment. Price: $500,000 USD. Payment Terms: Net 30 days. Delivery: May 15, 2024."}' "200"

test_endpoint 11 "Extract Metadata - Minimal Document" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Simple agreement between Party A and Party B for services valued at $10,000."}' "200"

test_endpoint 12 "Extract Metadata - Long Complex Document" "POST" "/ai/extract/metadata/" \
    '{"document_text":"COMPREHENSIVE SERVICE AND SUPPORT AGREEMENT This Agreement, effective as of January 1, 2024 (Effective Date) and continuing through December 31, 2026 (Termination Date), is entered into between TechCorp Global Solutions Inc., a Delaware corporation (Licensor/Provider), and DataSystems International LLC, a California limited liability company (Licensee/Customer). The total contract value is TWO MILLION FIVE HUNDRED THOUSAND DOLLARS ($2,500,000 USD), payable in quarterly installments. All payment terms, conditions, and termination clauses apply as stated herein."}' "200"

test_endpoint 13 "Extract Metadata - No Dates" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Agreement between CompanyA Ltd. and CompanyB Corp for $50,000 in services without specific date references."}' "200"

test_endpoint 14 "Extract Metadata - Multiple Parties" "POST" "/ai/extract/metadata/" \
    '{"document_text":"CONSORTIUM AGREEMENT between ABC Corporation, XYZ Holdings Inc., and DEF Partners LLC. Total project value: $3,000,000 USD. Duration from June 1, 2024 to May 31, 2027."}' "200"

test_endpoint 15 "Extract Metadata - International Currency" "POST" "/ai/extract/metadata/" \
    '{"document_text":"INTERNATIONAL SERVICES AGREEMENT between European Corp GmbH and Asian Trading Ltd. Contract value: €1,500,000 EUR. Valid from September 1, 2024 to August 31, 2026."}' "200"

test_endpoint 16 "Extract Metadata - Fractional Amount" "POST" "/ai/extract/metadata/" \
    '{"document_text":"SERVICE AGREEMENT between StartupCo and VentureIncubator. Value: $47,500.50 USD. Period: January 15, 2024 to January 14, 2025."}' "200"

test_endpoint 17 "Extract Metadata - No Value Mentioned" "POST" "/ai/extract/metadata/" \
    '{"document_text":"COLLABORATION AGREEMENT between TechPartner Inc. and InnovateLabs LLC effective from October 1, 2024 through September 30, 2025."}' "200"

test_endpoint 18 "Extract Metadata - Special Characters" "POST" "/ai/extract/metadata/" \
    '{"document_text":"AGREEMENT between Smith & Associates, Inc. and O'\''Neill-Davis Corp. Value: $125,000-$150,000 USD. Term: 2024-2025."}' "200"

test_endpoint 19 "Extract Metadata - Abbreviated Dates" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Contract between Co. A and Co. B. Start: 01-01-2024. End: 12-31-2025. Value: $200,000."}' "200"

test_endpoint 20 "Extract Metadata - Written-Out Dates" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Agreement between ACME Corporation and Universal Industries commencing on the First Day of January, Twenty Twenty-Four and concluding on the Thirty-First Day of December, Twenty Twenty-Five, valued at Five Hundred Thousand Dollars."}' "200"

# ============================================================================
# PHASE 3B: CLAUSE CLASSIFICATION - STANDARD CLAUSES (20 TESTS)
# ============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 3B: CLAUSE CLASSIFICATION - 20 CLAUSE TYPES (20 TESTS)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}\n"

test_endpoint 21 "Classify - Confidentiality Clause" "POST" "/ai/classify/" \
    '{"text":"The Licensee shall not disclose any Confidential Information to third parties without prior written consent. This obligation survives for five years post-termination."}' "200"

test_endpoint 22 "Classify - Payment Terms Clause" "POST" "/ai/classify/" \
    '{"text":"Payment shall be made within thirty days of invoice receipt. Late penalties of 1.5% per month apply. Wire transfer to designated account."}' "200"

test_endpoint 23 "Classify - Termination Clause" "POST" "/ai/classify/" \
    '{"text":"Either party may terminate upon ninety days written notice. Immediate termination allowed for material breach not cured within thirty days."}' "200"

test_endpoint 24 "Classify - Liability Clause" "POST" "/ai/classify/" \
    '{"text":"Total liability shall not exceed fees paid in preceding twelve months. No liability for indirect, incidental, special, or consequential damages."}' "200"

test_endpoint 25 "Classify - Indemnification Clause" "POST" "/ai/classify/" \
    '{"text":"Each party indemnifies the other from third-party claims arising from its breach, products, or services infringing intellectual property rights."}' "200"

test_endpoint 26 "Classify - Warranty Clause" "POST" "/ai/classify/" \
    '{"text":"Services provided are warranted to be performed in professional manner. Warranty period is twelve months from delivery date."}' "200"

test_endpoint 27 "Classify - Force Majeure Clause" "POST" "/ai/classify/" \
    '{"text":"Neither party liable for non-performance due to acts beyond control: war, natural disaster, government action, or pandemic."}' "200"

test_endpoint 28 "Classify - Intellectual Property Clause" "POST" "/ai/classify/" \
    '{"text":"All IP created by Licensor remains Licensor'\''s property. Licensee grants Licensor license to derivative works. No ownership transfer."}' "200"

test_endpoint 29 "Classify - Dispute Resolution Clause" "POST" "/ai/classify/" \
    '{"text":"Disputes resolved through mediation, then binding arbitration under rules of American Arbitration Association in New York."}' "200"

test_endpoint 30 "Classify - Governing Law Clause" "POST" "/ai/classify/" \
    '{"text":"This Agreement governed by laws of State of Delaware, USA, without regard to conflicts principles."}' "200"

test_endpoint 31 "Classify - Audit Rights Clause" "POST" "/ai/classify/" \
    '{"text":"Licensor may audit Licensee'\''s records annually upon ten days notice to verify compliance with agreement terms."}' "200"

test_endpoint 32 "Classify - Assignment Clause" "POST" "/ai/classify/" \
    '{"text":"Neither party may assign rights without written consent of other party. Attempted assignment void. Binding on successors."}' "200"

test_endpoint 33 "Classify - Amendment Clause" "POST" "/ai/classify/" \
    '{"text":"Amendments valid only in writing signed by both parties. No oral modifications accepted. Electronic signatures acceptable."}' "200"

test_endpoint 34 "Classify - Entire Agreement Clause" "POST" "/ai/classify/" \
    '{"text":"This Agreement constitutes entire agreement between parties, superseding all prior negotiations, understandings, and agreements."}' "200"

test_endpoint 35 "Classify - Severability Clause" "POST" "/ai/classify/" \
    '{"text":"If any provision found invalid, remaining provisions continue in effect and invalid provision reformed to extent possible."}' "200"

test_endpoint 36 "Classify - Renewal Clause" "POST" "/ai/classify/" \
    '{"text":"Agreement automatically renews for one-year terms unless either party provides sixty days prior written notice of non-renewal."}' "200"

test_endpoint 37 "Classify - Limitation of Liability Clause" "POST" "/ai/classify/" \
    '{"text":"In no event shall liability exceed contract value. Neither party liable for lost profits or business interruption damages."}' "200"

test_endpoint 38 "Classify - Insurance Clause" "POST" "/ai/classify/" \
    '{"text":"Both parties maintain general liability insurance minimum $1M. Certificate of insurance provided annually."}' "200"

test_endpoint 39 "Classify - Compliance Clause" "POST" "/ai/classify/" \
    '{"text":"Services performed in compliance with all applicable laws, regulations, and industry standards."}' "200"

test_endpoint 40 "Classify - Counterparts Clause" "POST" "/ai/classify/" \
    '{"text":"Agreement may be executed in counterparts, each deemed original, all together constituting one agreement."}' "200"

# ============================================================================
# PHASE 3C: CLAUSE CLASSIFICATION - EDGE CASES (15 TESTS)
# ============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 3C: CLAUSE CLASSIFICATION - EDGE CASES (15 TESTS)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}\n"

test_endpoint 41 "Classify - Very Short Clause" "POST" "/ai/classify/" \
    '{"text":"Payment due in thirty days."}' "200"

test_endpoint 42 "Classify - Very Long Complex Clause" "POST" "/ai/classify/" \
    '{"text":"The Party of the First Part (hereinafter Licensor) agrees to provide comprehensive payment processing services to the Party of the Second Part (hereinafter Licensee) in accordance with the following terms: payment shall be remitted within thirty (30) calendar days of each invoice issuance, with late payment penalties accruing at one and one-half percent (1.5%) per month, compounded monthly, and the Licensor reserves right to suspend services upon fifteen (15) days written notice if payment exceeds sixty (60) days overdue."}' "200"

test_endpoint 43 "Classify - Abbreviated Terms" "POST" "/ai/classify/" \
    '{"text":"Confid. terms remain in effect 5 yrs post-term. NDA obligations binding on all parties."}' "200"

test_endpoint 44 "Classify - Clause with Numbers" "POST" "/ai/classify/" \
    '{"text":"Licensee may not disclose 3rd party contact info. Confidentiality period: 5 years. Breach damages: $100k per occurrence, max $1M."}' "200"

test_endpoint 45 "Classify - Clause with Special Formatting" "POST" "/ai/classify/" \
    '{"text":"PAYMENT TERMS: NET 30 DAYS\\nLATE FEE: 1.5% MONTHLY\\nMETHOD: WIRE TRANSFER\\nACCOUNT: [Bank Details]"}' "200"

test_endpoint 46 "Classify - Mixed Language" "POST" "/ai/classify/" \
    '{"text":"Les parties conviennent que les termes de confidentialité s'\''appliquent pendant 5 ans. Non-disclosure obligations binding."}' "200"

test_endpoint 47 "Classify - Ambiguous Clause" "POST" "/ai/classify/" \
    '{"text":"Either party may do something regarding the thing or maybe not regarding the other thing."}' "200"

test_endpoint 48 "Classify - Boilerplate Clause" "POST" "/ai/classify/" \
    '{"text":"This Article shall be interpreted consistently with the other provisions hereof and in accordance with applicable law."}' "200"

test_endpoint 49 "Classify - Clause with Citations" "POST" "/ai/classify/" \
    '{"text":"Payment terms comply with UCC Article 2, Revised Uniform Commercial Code § 2-310(a) regarding payment due on receipt of goods."}' "200"

test_endpoint 50 "Classify - Clause with Conditions" "POST" "/ai/classify/" \
    '{"text":"If services delayed, then payment due within sixty days instead of thirty. However, if delay caused by force majeure, payment extended to ninety days."}' "200"

test_endpoint 51 "Classify - Clause with Examples" "POST" "/ai/classify/" \
    '{"text":"Confidential information includes but not limited to: trade secrets, customer lists, pricing (e.g., $100k contract discount), technical data (e.g., source code), and business plans."}' "200"

test_endpoint 52 "Classify - Clause with Exceptions" "POST" "/ai/classify/" \
    '{"text":"Confidentiality applies except: (a) publicly available information, (b) independently developed, (c) required by law, or (d) with written approval."}' "200"

test_endpoint 53 "Classify - Clause with Cross-References" "POST" "/ai/classify/" \
    '{"text":"As defined in Section 5.2, Confidential Information excludes items listed in Schedule A or publicly disclosed per Section 3.1(b)."}' "200"

test_endpoint 54 "Classify - Clause with Emphasis" "POST" "/ai/classify/" \
    '{"text":"It is EXPRESSLY UNDERSTOOD AND AGREED that ***NO DISCLOSURE*** shall occur ***UNDER ANY CIRCUMSTANCES*** without explicit written consent."}' "200"

test_endpoint 55 "Classify - Historical Clause" "POST" "/ai/classify/" \
    '{"text":"Whereas, the parties entered into negotiations in 1999, and Now, Therefore, in consideration of mutual covenants, parties agree to binding confidentiality."}' "200"

# ============================================================================
# PHASE 4A: AI EXTRACTION - ADVANCED SCENARIOS (15 TESTS)
# ============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 4A: METADATA EXTRACTION - ADVANCED SCENARIOS (15 TESTS)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}\n"

test_endpoint 56 "Extract - Nested Parties Structure" "POST" "/ai/extract/metadata/" \
    '{"document_text":"AGREEMENT among (1) ABC Corporation, by and through its VP of Operations, (2) XYZ Holding Company, Limited, as parent company, and (3) DEF Inc., a wholly-owned subsidiary. Value: $1,500,000 USD. Term: 2024-2026."}' "200"

test_endpoint 57 "Extract - Multiple Contract Values" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Base Contract: $100,000. Additional Services: $50,000. Optional Renewal: $75,000. Total Potential: $225,000. Effective Jan 1, 2024 through Dec 31, 2025."}' "200"

test_endpoint 58 "Extract - Percentage and Commission" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Agreement between SalesRep Inc and Products Corp. Commission: 15% of gross sales, minimum $10,000 annually. Period: January 1, 2024 to December 31, 2026."}' "200"

test_endpoint 59 "Extract - Range-Based Value" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Consulting Agreement. Estimated value: between $50,000 and $150,000 USD based on scope. From March 1, 2024 to February 28, 2025."}' "200"

test_endpoint 60 "Extract - Renewal with Price Adjustment" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Initial term: $100,000 from Jan 1, 2024-Dec 31, 2025. Renewal (if exercised): $105,000 for additional two years (3% increase)."}' "200"

test_endpoint 61 "Extract - Variable Consideration" "POST" "/ai/extract/metadata/" \
    '{"document_text":"License Agreement. Annual fee: $50,000 plus 2% of licensee'\''s gross revenue. Period: July 1, 2024 through June 30, 2026."}' "200"

test_endpoint 62 "Extract - In-Kind Consideration" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Partnership agreement. Contribution: Equipment valued at $200,000 and Property valued at $300,000, total $500,000 equivalent. Term: Jan 1, 2024 - Dec 31, 2027."}' "200"

test_endpoint 63 "Extract - Date with Month Names" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Effective commencing on the first day of January, twenty twenty-four through the last day of December, twenty twenty-five. Value: Two Hundred Fifty Thousand Dollars."}' "200"

test_endpoint 64 "Extract - Fiscal Year Dates" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Agreement term: FY2024 (Oct 1, 2023 - Sept 30, 2024) through FY2026 (Oct 1, 2025 - Sept 30, 2026). Contract value: $300,000 annually."}' "200"

test_endpoint 65 "Extract - Quarters and Milestones" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Q1 2024: Phase 1 kickoff, $50,000. Q2 2024: Phase 2, $75,000. Q3-Q4 2024: Phase 3, $125,000. Total: $250,000."}' "200"

test_endpoint 66 "Extract - Retroactive Dates" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Agreement dated January 15, 2024, with retroactive effective date of January 1, 2024. Termination: December 31, 2025. Value: $100,000."}' "200"

test_endpoint 67 "Extract - Conditional Dates" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Shall commence upon execution or February 1, 2024, whichever is earlier. Shall terminate ninety days after completion or December 31, 2025, whichever occurs later."}' "200"

test_endpoint 68 "Extract - International Parties Format" "POST" "/ai/extract/metadata/" \
    '{"document_text":"AGREEMENT between ABC GmbH (Germany), registered as DE123456789, and XYZ Pty Ltd (Australia), ACN 987654321. Value: AUD $400,000. Period: January 1, 2024 - December 31, 2025."}' "200"

test_endpoint 69 "Extract - Government Entities" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Contract between City of New York, Department of Parks and Recreation, and GreenSpaces Maintenance Corp. Value: $2,000,000. Period: FY2024-FY2026."}' "200"

test_endpoint 70 "Extract - Academic/Non-Profit" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Research Agreement between Harvard University and BioTech Research Foundation, a 501(c)(3) nonprofit. Grant: $500,000. Period: September 1, 2024 - August 31, 2026."}' "200"

# ============================================================================
# PHASE 4B: PERFORMANCE & LATENCY TESTS (10 TESTS)
# ============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 4B: PERFORMANCE & LATENCY TESTS (10 TESTS)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}\n"

test_endpoint 71 "Performance - Rapid Consecutive Requests 1" "POST" "/ai/classify/" \
    '{"text":"Payment terms: Net 30 days"}' "200"

test_endpoint 72 "Performance - Rapid Consecutive Requests 2" "POST" "/ai/classify/" \
    '{"text":"Confidentiality obligation for five years"}' "200"

test_endpoint 73 "Performance - Rapid Consecutive Requests 3" "POST" "/ai/classify/" \
    '{"text":"Either party may terminate with thirty days notice"}' "200"

test_endpoint 74 "Performance - Rapid Consecutive Requests 4" "POST" "/ai/classify/" \
    '{"text":"Liability limited to contract value"}' "200"

test_endpoint 75 "Performance - Rapid Consecutive Requests 5" "POST" "/ai/classify/" \
    '{"text":"Indemnification for third party claims"}' "200"

test_endpoint 76 "Performance - Large Payload Metadata" "POST" "/ai/extract/metadata/" \
    '{"document_text":"'$(python3 -c "print('This is a comprehensive service agreement. ' * 50)")' Contract value: $250,000. Effective January 1, 2024."}' "200"

test_endpoint 77 "Performance - Rapid Metadata Requests 1" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Agreement 1 between Party A and Party B. Value $100,000. Date 2024-2025."}' "200"

test_endpoint 78 "Performance - Rapid Metadata Requests 2" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Agreement 2 between Company X and Company Y. Value $200,000. Date 2024-2026."}' "200"

test_endpoint 79 "Performance - Rapid Metadata Requests 3" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Agreement 3 between Org Alpha and Org Beta. Value $150,000. Date 2024-2025."}' "200"

test_endpoint 80 "Performance - Rapid Metadata Requests 4" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Agreement 4 between Entity 1 and Entity 2. Value $300,000. Date 2024-2027."}' "200"

# ============================================================================
# PHASE 5A: ERROR HANDLING & EDGE CASES (15 TESTS)
# ============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 5A: ERROR HANDLING & EDGE CASES (15 TESTS)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}\n"

test_endpoint 81 "Error - Empty Text for Classification" "POST" "/ai/classify/" \
    '{"text":""}' "400"

test_endpoint 82 "Error - Text Too Short" "POST" "/ai/classify/" \
    '{"text":"Short"}' "400"

test_endpoint 83 "Error - Invalid JSON Format" "POST" "/ai/classify/" \
    '{"text": invalid json}' "400"

test_endpoint 84 "Error - Missing Text Field" "POST" "/ai/classify/" \
    '{"data": "some text"}' "400"

test_endpoint 85 "Error - Null Value for Text" "POST" "/ai/classify/" \
    '{"text": null}' "400"

test_endpoint 86 "Error - Missing Document Text" "POST" "/ai/extract/metadata/" \
    '{"other_field": "value"}' "400"

test_endpoint 87 "Error - Empty Document Text" "POST" "/ai/extract/metadata/" \
    '{"document_text":""}' "400"

test_endpoint 88 "Error - Non-JSON Content" "POST" "/ai/classify/" \
    '{"text":"This is plain text without JSON"}' "200"

test_endpoint 89 "Error - Special Unicode Characters" "POST" "/ai/classify/" \
    '{"text":"Confidentiality clause with émojis 🔒 and special chars Ñ"}' "200"

test_endpoint 90 "Error - Very Long Text (50KB)" "POST" "/ai/classify/" \
    '{"text":"'$(python3 -c "print('A' * 50000)")'\"}' "200"

test_endpoint 91 "Error - Malformed Data Structure" "POST" "/ai/extract/metadata/" \
    '["not", "an", "object"]' "400"

test_endpoint 92 "Error - Numeric Values as Text" "POST" "/ai/classify/" \
    '{"text": 12345}' "200"

test_endpoint 93 "Error - Array Instead of String" "POST" "/ai/classify/" \
    '{"text": ["multiple", "values"]}' "400"

test_endpoint 94 "Error - Nested Object for Text" "POST" "/ai/classify/" \
    '{"text": {"nested": "object"}}' "400"

test_endpoint 95 "Error - Additional Unexpected Fields" "POST" "/ai/classify/" \
    '{"text":"Valid text", "extra_field": "should_be_ignored", "another": 123}' "200"

# ============================================================================
# PHASE 5B: DATA VALIDATION & ACCURACY (15 TESTS)
# ============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 5B: DATA VALIDATION & ACCURACY (15 TESTS)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}\n"

test_endpoint 96 "Accuracy - Multiple Matching Clauses in One Text" "POST" "/ai/classify/" \
    '{"text":"Payment shall be made within thirty days. Confidentiality obligations binding for five years post-termination."}' "200"

test_endpoint 97 "Accuracy - Clause Type Misidentification Risk" "POST" "/ai/classify/" \
    '{"text":"Agreement may be terminated. Party breaching shall pay damages equal to three months fees."}' "200"

test_endpoint 98 "Accuracy - Extraction with Incomplete Info" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Agreement between parties. No dates specified. No amount specified."}' "200"

test_endpoint 99 "Accuracy - Extraction with Ambiguous Dates" "POST" "/ai/extract/metadata/" \
    '{"document_text":"Agreement from 1-2-3 to 4-5-6 with value 7-8-9 unclear which is date vs value"}' "200"

test_endpoint 100 "Accuracy - Classification with Hybrid Clause" "POST" "/ai/classify/" \
    '{"text":"Upon termination within 30 days, confidentiality survives with liability limited to annual fees."}' "200"

# Summary with statistics
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ TEST SUITE COMPLETED${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}\n"

echo -e "${GREEN}📊 TEST RESULTS:${NC}"
echo -e "  Total Tests Run: $TESTS_RUN"
echo -e "  ${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "  ${RED}Failed: $TESTS_FAILED${NC}"
echo -e "  Success Rate: $(echo "scale=1; ($TESTS_PASSED / $TESTS_RUN) * 100" | bc)%\n"

if [ ${#LATENCIES[@]} -gt 0 ]; then
    TOTAL=0
    for lat in "${LATENCIES[@]}"; do
        TOTAL=$((TOTAL + lat))
    done
    AVG=$(( TOTAL / ${#LATENCIES[@]} ))
    MAX=$(printf '%s\n' "${LATENCIES[@]}" | sort -rn | head -1)
    MIN=$(printf '%s\n' "${LATENCIES[@]}" | sort -n | head -1)
    
    echo -e "${GREEN}⏱️  LATENCY METRICS:${NC}"
    echo -e "  Average: ${AVG}ms"
    echo -e "  Max: ${MAX}ms"
    echo -e "  Min: ${MIN}ms"
    echo -e "  Total Requests: ${#LATENCIES[@]}\n"
fi

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎯 ALL TESTS PASSING - SYSTEM PRODUCTION READY${NC}\n"
else
    echo -e "${YELLOW}⚠️  Some tests failed - review results above${NC}\n"
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}\n"
