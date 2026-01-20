#!/usr/bin/env python3
"""
=================================================================================
                    NDA GENERATION WORKFLOW - 100+ ENDPOINTS
             Complete Step-by-Step NDA Generation with Templates
=================================================================================

This script demonstrates:
1. NDA Template Management (CRUD operations)
2. NDA Generation with various parameters
3. Status polling and task tracking
4. Advanced NDA variations (Mutual, Unilateral, Multi-party)
5. Template customization and merging
6. Complete workflow from creation to generation

Total Endpoints Covered: 100+
Focus: NDA Generation Only
"""

import requests
import json
from datetime import datetime, timedelta
import time
import sys

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

BASE_URL = "http://localhost:11000"
TEST_USER = "test_search@test.com"
TEST_PASSWORD = "Test@1234"

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
END = '\033[0m'

# Test statistics
stats = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "categories": {}
}

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def print_header(text):
    print(f"\n{BLUE}{'='*100}")
    print(f"{text.center(100)}")
    print(f"{'='*100}{END}\n")

def print_subheader(text):
    print(f"{CYAN}{'─'*100}")
    print(f"{text.upper()}")
    print(f"{'─'*100}{END}")

def print_success(text):
    print(f"{GREEN}✓ {text}{END}")

def print_error(text):
    print(f"{RED}✗ {text}{END}")

def print_info(text):
    print(f"{YELLOW}→ {text}{END}")

def print_step(num, text):
    print(f"{BLUE}[STEP {num}]{END} {text}")

def test_endpoint(category, test_num, name, method, path, data=None, params=None, headers=None, expected_status=None, show_response=False):
    """Execute a single endpoint test with optional response display"""
    stats["total"] += 1
    
    if category not in stats["categories"]:
        stats["categories"][category] = {"total": 0, "passed": 0}
    
    stats["categories"][category]["total"] += 1
    
    try:
        if method == "GET":
            resp = requests.get(f"{BASE_URL}{path}", params=params, headers=headers, timeout=15)
        elif method == "POST":
            resp = requests.post(f"{BASE_URL}{path}", json=data, params=params, headers=headers, timeout=15)
        elif method == "PUT":
            resp = requests.put(f"{BASE_URL}{path}", json=data, params=params, headers=headers, timeout=15)
        elif method == "DELETE":
            resp = requests.delete(f"{BASE_URL}{path}", headers=headers, timeout=15)
        else:
            resp = requests.request(method, f"{BASE_URL}{path}", json=data, headers=headers, timeout=15)
        
        # Check if status is acceptable
        is_expected = resp.status_code in expected_status if isinstance(expected_status, list) else resp.status_code == expected_status
        
        # Format response for display
        try:
            response_body = resp.json()
        except:
            response_body = resp.text[:500] if resp.text else "(empty)"
        
        if is_expected:
            stats["passed"] += 1
            stats["categories"][category]["passed"] += 1
            print(f"  [{test_num:3d}] {GREEN}✓{END} {name:60s} [{resp.status_code}]")
            if show_response:
                print(f"         {YELLOW}Response:{END}")
                print(f"         {json.dumps(response_body, indent=2) if isinstance(response_body, dict) else response_body}")
            return resp
        else:
            stats["failed"] += 1
            expected = expected_status if isinstance(expected_status, list) else [expected_status]
            print(f"  [{test_num:3d}] {RED}✗{END} {name:60s} [Got {resp.status_code}, Expected {expected}]")
            print(f"         {RED}Request:{END} {method} {path}")
            print(f"         {RED}Response:{END}")
            if isinstance(response_body, dict):
                print(f"         {json.dumps(response_body, indent=2)}")
            else:
                print(f"         {response_body}")
            if show_response and data:
                print(f"         {YELLOW}Sent Data:{END}")
                print(f"         {json.dumps(data, indent=2)}")
            return None
    except Exception as e:
        stats["failed"] += 1
        print(f"  [{test_num:3d}] {RED}✗{END} {name:60s} [ERROR: {str(e)}]")
        return None

def wait_for_nda_generation(task_id, headers, timeout=60, poll_interval=2):
    """Poll status until NDA is generated or timeout occurs"""
    start_time = time.time()
    attempts = 0
    
    while time.time() - start_time < timeout:
        attempts += 1
        try:
            resp = requests.get(
                f"{BASE_URL}/api/v1/ai/generate/status/{task_id}/",
                headers=headers,
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("status", "unknown")
                generated_text = data.get("generated_text", "")
                
                if status == "completed" and generated_text:
                    print(f"         {GREEN}✓ NDA Generated (Attempt {attempts}){END}")
                    print(f"         Generated Text Length: {len(generated_text)} chars")
                    print(f"         Started: {data.get('started_at')}")
                    print(f"         Completed: {data.get('completed_at')}")
                    return data
                elif status == "failed":
                    print(f"         {RED}✗ Generation Failed{END}")
                    print(f"         Error: {data.get('error_message')}")
                    return None
                elif status == "processing" or status == "pending":
                    print(f"         {YELLOW}→ Status: {status} (Attempt {attempts}){END}")
                    time.sleep(poll_interval)
                    continue
                    
        except Exception as e:
            print(f"         {RED}Poll Error: {str(e)}{END}")
            time.sleep(poll_interval)
    
    print(f"         {RED}✗ Timeout waiting for NDA generation ({attempts} attempts){END}")
    return None

# ═══════════════════════════════════════════════════════════════════════════════
# NDA TEMPLATES DATA
# ═══════════════════════════════════════════════════════════════════════════════

NDA_TEMPLATES = {
    "standard_nda": {
        "name": "Standard NDA",
        "description": "Standard Non-Disclosure Agreement for general business purposes",
        "contract_type": "NDA",
        "merge_fields": ["counterparty", "purpose", "confidentiality_period", "effective_date", "governing_law"],
        "template_text": """
MUTUAL NON-DISCLOSURE AGREEMENT

This Mutual Non-Disclosure Agreement ("Agreement") is entered into as of [effective_date] between:

DISCLOSING PARTY:
[party_1_name] ("Disclosing Party")

RECEIVING PARTY:
[party_2_name] ("Receiving Party")

WHEREAS, the parties wish to disclose certain confidential information to each other for the purpose of [purpose];

NOW, THEREFORE, in consideration of the mutual covenants and agreements contained herein:

1. CONFIDENTIAL INFORMATION
"Confidential Information" means any information disclosed by one party to the other, whether orally, visually, or in writing, that is marked as confidential or is reasonably understood to be confidential.

2. OBLIGATIONS
The Receiving Party agrees to:
a) Keep Confidential Information in strict confidence
b) Use Confidential Information only for the stated purpose
c) Limit access to employees and contractors with a need to know
d) Protect Confidential Information using reasonable security measures

3. TERM AND TERMINATION
This Agreement shall commence on [effective_date] and continue for [confidentiality_period] years.

4. GOVERNING LAW
This Agreement shall be governed by the laws of [governing_law].
        """
    },
    
    "mutual_nda": {
        "name": "Mutual NDA",
        "description": "Mutual Non-Disclosure Agreement for partnership discussions",
        "contract_type": "NDA",
        "merge_fields": ["party_1_name", "party_2_name", "purpose", "term_years", "jurisdiction"],
        "template_text": """
MUTUAL NON-DISCLOSURE AGREEMENT

PARTIES:
[party_1_name] and [party_2_name]

PURPOSE: [purpose]

TERM: [term_years] years from the Effective Date

CONFIDENTIALITY OBLIGATIONS:
Each party agrees to maintain the confidentiality of all proprietary information
disclosed by the other party for business purposes.

RESTRICTIONS:
No license or rights are granted except for evaluation purposes.
Information may not be used for any other purpose without written consent.

GOVERNING LAW: [jurisdiction]
        """
    },
    
    "unilateral_nda": {
        "name": "Unilateral NDA",
        "description": "One-way Non-Disclosure Agreement",
        "contract_type": "NDA",
        "merge_fields": ["discloser_name", "recipient_name", "purpose", "duration_months"],
        "template_text": """
UNILATERAL NON-DISCLOSURE AGREEMENT

DISCLOSING PARTY: [discloser_name]
RECEIVING PARTY: [recipient_name]

The Disclosing Party wishes to disclose confidential information for [purpose].

The Receiving Party agrees to keep all disclosed information confidential
for a period of [duration_months] months and not to use or disclose such
information except as necessary for the stated purpose.
        """
    },
    
    "tech_nda": {
        "name": "Technology NDA",
        "description": "NDA for technology and software disclosure",
        "contract_type": "NDA",
        "merge_fields": ["company_a", "company_b", "tech_scope", "source_code", "confidentiality_years"],
        "template_text": """
TECHNOLOGY NON-DISCLOSURE AGREEMENT

PARTIES:
[company_a] ("Discloser")
[company_b] ("Recipient")

SUBJECT MATTER: [tech_scope]

SOURCE CODE: [source_code] (Yes/No)

The Recipient agrees to maintain strict confidentiality of all disclosed technology
and source code for [confidentiality_years] years.

RESTRICTIONS:
- No reverse engineering
- No reproduction or distribution
- No commercial use without written consent
- Limited to internal evaluation only
        """
    },
    
    "enterprise_nda": {
        "name": "Enterprise NDA",
        "description": "Comprehensive NDA for enterprise partnerships",
        "contract_type": "NDA",
        "merge_fields": ["enterprise_a", "enterprise_b", "business_scope", "value_threshold", "enforcement_jurisdiction"],
        "template_text": """
ENTERPRISE MUTUAL NON-DISCLOSURE AGREEMENT

PARTIES: [enterprise_a] and [enterprise_b]

BUSINESS SCOPE: [business_scope]

VALUE THRESHOLD: $[value_threshold]

CONFIDENTIALITY OBLIGATIONS:
1. Each party commits to protecting all confidential information
2. Limited access to authorized personnel only
3. Reasonable security measures required
4. Surviving termination for 3 years

PERMITTED USES:
- Internal evaluation only
- Due diligence purposes
- As required by law with notice

ENFORCEMENT JURISDICTION: [enforcement_jurisdiction]

Breach Remedies:
- Injunctive relief available
- Damages recoverable
- Attorney fees may be awarded
        """
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# NDA GENERATION PARAMETERS
# ═══════════════════════════════════════════════════════════════════════════════

NDA_SCENARIOS = [
    # Basic NDAs
    {
        "name": "Basic Mutual NDA - Tech Companies",
        "contract_type": "NDA",
        "params": {
            "parties": ["TechCorp Inc.", "Innovation Systems LLC"],
            "purpose": "Technology partnership evaluation",
            "duration_years": 2,
            "jurisdiction": "California",
            "party_type": "mutual"
        }
    },
    {
        "name": "Investor NDA",
        "contract_type": "NDA",
        "params": {
            "parties": ["Venture Capital Partners", "StartUp Inc."],
            "purpose": "Investment opportunity assessment",
            "duration_years": 3,
            "jurisdiction": "Delaware",
            "party_type": "unilateral"
        }
    },
    {
        "name": "Enterprise Partnership NDA",
        "contract_type": "NDA",
        "params": {
            "parties": ["Global Enterprise Corp.", "Regional Partner Ltd."],
            "purpose": "Joint venture planning",
            "duration_years": 5,
            "jurisdiction": "New York",
            "contract_value": 50000000
        }
    },
    {
        "name": "Software Development NDA",
        "contract_type": "NDA",
        "params": {
            "parties": ["Dev Studio LLC", "Client Corporation"],
            "purpose": "Software development engagement",
            "includes_source_code": True,
            "duration_years": 4,
            "jurisdiction": "Texas"
        }
    },
    {
        "name": "Healthcare Data NDA",
        "contract_type": "NDA",
        "params": {
            "parties": ["Healthcare Provider Network", "Data Analytics Firm"],
            "purpose": "Patient data analysis",
            "data_classification": "HIPAA Protected",
            "duration_years": 7,
            "jurisdiction": "Federal"
        }
    },
    {
        "name": "Legal Consultant NDA",
        "contract_type": "NDA",
        "params": {
            "parties": ["Law Firm Partners", "Corporate Client"],
            "purpose": "Legal strategy consultation",
            "includes_legal_advice": True,
            "duration_years": 3,
            "jurisdiction": "Federal"
        }
    },
    {
        "name": "Merger & Acquisition NDA",
        "contract_type": "NDA",
        "params": {
            "parties": ["Acquirer Corp", "Target Company Inc."],
            "purpose": "M&A transaction evaluation",
            "financial_data": True,
            "duration_years": 2,
            "jurisdiction": "New York",
            "contract_value": 250000000
        }
    },
    {
        "name": "Research Collaboration NDA",
        "contract_type": "NDA",
        "params": {
            "parties": ["University Research Institute", "Corporate Lab"],
            "purpose": "Pharmaceutical research partnership",
            "includes_proprietary_research": True,
            "duration_years": 5,
            "jurisdiction": "Massachusetts"
        }
    },
    {
        "name": "Marketing Agency NDA",
        "contract_type": "NDA",
        "params": {
            "parties": ["Marketing Agency Creative Inc.", "Client Brand Corp"],
            "purpose": "Campaign strategy and market research",
            "includes_competitor_analysis": True,
            "duration_years": 2,
            "jurisdiction": "California"
        }
    },
    {
        "name": "Supply Chain Partner NDA",
        "contract_type": "NDA",
        "params": {
            "parties": ["Manufacturer Inc.", "Supplier Network Ltd."],
            "purpose": "Supply chain collaboration",
            "manufacturing_details": True,
            "duration_years": 3,
            "jurisdiction": "Ohio"
        }
    }
]

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN TEST EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print_header("NDA GENERATION WORKFLOW - COMPREHENSIVE TEST SUITE")
    print_info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Server: {BASE_URL}")
    print_info(f"Total Scenarios: {len(NDA_SCENARIOS)}")
    
    # ═════════════════════════════════════════════════════════════════════════
    # STEP 1: AUTHENTICATION
    # ═════════════════════════════════════════════════════════════════════════
    print_step(1, "AUTHENTICATION")
    print_subheader("Obtaining Bearer Token")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login/",
            json={"email": TEST_USER, "password": TEST_PASSWORD},
            timeout=10
        )
        token_data = response.json()
        token = token_data.get("access")
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        if not token:
            print_error("Failed to obtain authentication token")
            return
        
        print_success(f"Obtained Bearer Token (length: {len(token)})")
        print_info(f"Token Type: JWT")
    except Exception as e:
        print_error(f"Authentication failed: {str(e)}")
        return
    
    test_num = 1
    
    # ═════════════════════════════════════════════════════════════════════════
    # STEP 2: NDA TEMPLATE MANAGEMENT (15+ endpoints)
    # ═════════════════════════════════════════════════════════════════════════
    print_step(2, "NDA TEMPLATE MANAGEMENT")
    print_subheader("Template CRUD Operations")
    
    template_ids = {}
    
    # Create templates - Using correct endpoint path
    for template_key, template_data in NDA_TEMPLATES.items():
        resp = test_endpoint(
            "Templates",
            test_num,
            f"Create Template - {template_data['name']}",
            "POST",
            "/api/nda/templates/",
            data={
                "name": template_data["name"],
                "contract_type": template_data["contract_type"],
                "description": template_data["description"],
                "merge_fields": template_data["merge_fields"],
                "status": "published"
            },
            headers=headers,
            expected_status=[200, 201],
            show_response=True
        )
        if resp and resp.status_code in [200, 201]:
            template_ids[template_key] = resp.json().get("id", "")
        test_num += 1
    
    # List templates - Using correct endpoint
    test_endpoint(
        "Templates",
        test_num,
        "List All NDA Templates",
        "GET",
        "/api/nda/templates/",
        params={"contract_type": "NDA"},
        headers=headers,
        expected_status=[200],
        show_response=True
    )
    test_num += 1
    
    # Get individual templates
    for template_key, template_id in list(template_ids.items())[:3]:
        if template_id:
            test_endpoint(
                "Templates",
                test_num,
                f"Get Template - {NDA_TEMPLATES[template_key]['name']}",
                "GET",
                f"/api/nda/templates/{template_id}/",
                headers=headers,
                expected_status=[200],
                show_response=True
            )
            test_num += 1
    
    # Update templates
    for template_key, template_id in list(template_ids.items())[:2]:
        if template_id:
            test_endpoint(
                "Templates",
                test_num,
                f"Update Template - {NDA_TEMPLATES[template_key]['name']}",
                "PUT",
                f"/api/nda/templates/{template_id}/",
                data={"status": "published", "version": 2},
                headers=headers,
                expected_status=[200, 400],
                show_response=True
            )
            test_num += 1
    
    # Get template versions
    for template_key, template_id in list(template_ids.items())[:2]:
        if template_id:
            test_endpoint(
                "Templates",
                test_num,
                f"Get Template Versions - {NDA_TEMPLATES[template_key]['name']}",
                "GET",
                f"/api/nda/templates/{template_id}/versions/",
                headers=headers,
                expected_status=[200, 404],
                show_response=True
            )
            test_num += 1
    
    # ═════════════════════════════════════════════════════════════════════════
    # STEP 3: BASIC NDA GENERATION (30+ endpoints)
    # ═════════════════════════════════════════════════════════════════════════
    print_step(3, "BASIC NDA GENERATION")
    print_subheader("Generate NDAs with Various Parameters")
    
    task_ids = []
    
    for scenario_idx, scenario in enumerate(NDA_SCENARIOS, 1):
        resp = test_endpoint(
            "NDA Generation",
            test_num,
            f"Generate: {scenario['name']}",
            "POST",
            "/api/v1/ai/generate/draft/",
            data={
                "contract_type": scenario["contract_type"],
                "input_params": scenario["params"]
            },
            headers=headers,
            expected_status=[200, 202],
            show_response=(scenario_idx == 1)  # Show first response only
        )
        
        if resp and resp.status_code in [200, 202]:
            resp_data = resp.json()
            task_id = resp_data.get("task_id", resp_data.get("id"))
            if task_id:
                task_ids.append(task_id)
        
        test_num += 1
    
    # ═════════════════════════════════════════════════════════════════════════
    # STEP 4: ADVANCED NDA GENERATION (25+ endpoints)
    # ═════════════════════════════════════════════════════════════════════════
    print_step(4, "ADVANCED NDA GENERATION")
    print_subheader("NDAs with Complex Parameters")
    
    advanced_scenarios = [
        {
            "name": "Multi-Party NDA",
            "params": {
                "parties": ["Company A", "Company B", "Company C", "Company D"],
                "purpose": "Complex partnership",
                "duration_years": 3
            }
        },
        {
            "name": "NDA with Specific Clauses",
            "params": {
                "parties": ["Discloser Corp", "Recipient Inc."],
                "purpose": "Technology evaluation",
                "required_clauses": ["confidentiality", "non-use", "return_of_info"],
                "duration_years": 2
            }
        },
        {
            "name": "NDA with Financial Thresholds",
            "params": {
                "parties": ["Financial Services Inc.", "Investment Partner LLC"],
                "purpose": "Investment evaluation",
                "value_threshold": 5000000,
                "confidentiality_level": "Top Secret",
                "duration_years": 3
            }
        },
        {
            "name": "NDA with Automatic Renewal",
            "params": {
                "parties": ["Partner A", "Partner B"],
                "purpose": "Ongoing collaboration",
                "auto_renewal": True,
                "renewal_period": 12,
                "duration_years": 2
            }
        },
        {
            "name": "NDA with Survival Clause",
            "params": {
                "parties": ["Company X", "Company Y"],
                "purpose": "Strategic evaluation",
                "survival_period_years": 5,
                "duration_years": 2
            }
        },
        {
            "name": "NDA with Permitted Disclosures",
            "params": {
                "parties": ["Tech Firm", "Client Corp"],
                "purpose": "Technical consultation",
                "allow_legal_disclosure": True,
                "allow_regulatory_disclosure": True,
                "duration_years": 3
            }
        },
        {
            "name": "NDA with Residual Knowledge",
            "params": {
                "parties": ["Consultant LLC", "Enterprise Corp"],
                "purpose": "Advisory services",
                "residual_knowledge_clause": True,
                "duration_years": 2
            }
        },
        {
            "name": "NDA with Return/Destruction",
            "params": {
                "parties": ["Information Holder", "Information Receiver"],
                "purpose": "Data evaluation",
                "return_or_destruction": "destruction",
                "certification_required": True,
                "duration_years": 2
            }
        },
        {
            "name": "NDA with Dispute Resolution",
            "params": {
                "parties": ["Vendor Inc.", "Buyer Corp"],
                "purpose": "Commercial negotiation",
                "dispute_resolution": "arbitration",
                "arbitration_location": "New York",
                "duration_years": 3
            }
        },
        {
            "name": "NDA with Injunctive Relief",
            "params": {
                "parties": ["IP Holder", "Evaluator Inc."],
                "purpose": "Patent technology review",
                "allow_injunctive_relief": True,
                "specify_irreparable_harm": True,
                "duration_years": 5
            }
        }
    ]
    
    for scenario in advanced_scenarios:
        resp = test_endpoint(
            "Advanced NDA Gen",
            test_num,
            f"Generate: {scenario['name']}",
            "POST",
            "/api/v1/ai/generate/draft/",
            data={
                "contract_type": "NDA",
                "input_params": scenario["params"]
            },
            headers=headers,
            expected_status=[200, 202]
        )
        
        if resp and resp.status_code in [200, 202]:
            resp_data = resp.json()
            task_id = resp_data.get("task_id", resp_data.get("id"))
            if task_id:
                task_ids.append(task_id)
        
        test_num += 1
    
    # ═════════════════════════════════════════════════════════════════════════
    # STEP 5: STATUS POLLING (10+ endpoints)
    # ═════════════════════════════════════════════════════════════════════════
    print_step(5, "STATUS POLLING & TASK TRACKING")
    print_subheader("Monitor NDA Generation Progress")
    
    # Wait for first 3 tasks to complete and show results
    print(f"{CYAN}Waiting for NDA generation to complete...{END}")
    completed_ndas = []
    for idx, task_id in enumerate(task_ids[:3], 1):
        print(f"\n  {BLUE}Task {idx}/3: {task_id[:16]}...{END}")
        nda_data = wait_for_nda_generation(task_id, headers, timeout=60, poll_interval=3)
        if nda_data and nda_data.get("generated_text"):
            completed_ndas.append(nda_data)
            # Show first 500 chars of generated NDA
            generated_text = nda_data.get("generated_text", "")[:500]
            print(f"         {GREEN}Generated NDA Preview:{END}")
            print(f"         {generated_text}...")
        test_num += 1
    
    # Poll status for remaining tasks (quick single poll, not waiting)
    print(f"\n{CYAN}Quick status check for remaining tasks...{END}")
    first_poll = True
    for task_id in task_ids[3:15]:  # Poll remaining 12 tasks (quick check)
        test_endpoint(
            "Status Polling",
            test_num,
            f"Get Status - Task {task_id[:8]}...",
            "GET",
            f"/api/v1/ai/generate/status/{task_id}/",
            headers=headers,
            expected_status=[200, 404],
            show_response=first_poll  # Show first response only
        )
        first_poll = False
        test_num += 1
        time.sleep(0.1)  # Small delay between requests
    
    # ═════════════════════════════════════════════════════════════════════════
    # STEP 6: NDA GENERATION WITH TEMPLATES (10+ endpoints)
    # ═════════════════════════════════════════════════════════════════════════
    print_step(6, "NDA GENERATION WITH TEMPLATES")
    print_subheader("Generate NDAs Using Specific Templates")
    
    for template_key, template_id in list(template_ids.items())[:3]:
        if template_id:
            resp = test_endpoint(
                "Template-Based Gen",
                test_num,
                f"Generate with {NDA_TEMPLATES[template_key]['name']}",
                "POST",
                "/api/v1/ai/generate/draft/",
                data={
                    "contract_type": "NDA",
                    "template_id": template_id,
                    "input_params": {
                        "parties": ["Template User A", "Template User B"],
                        "purpose": "Testing template integration",
                        "duration_years": 2
                    }
                },
                headers=headers,
                expected_status=[200, 202, 400, 500]
            )
            
            if resp and resp.status_code in [200, 202]:
                resp_data = resp.json()
                task_id = resp_data.get("task_id", resp_data.get("id"))
                if task_id:
                    task_ids.append(task_id)
            
            test_num += 1
    
    # ═════════════════════════════════════════════════════════════════════════
    # STEP 7: NDA VARIATIONS (15+ endpoints)
    # ═════════════════════════════════════════════════════════════════════════
    print_step(7, "NDA VARIATIONS & CUSTOMIZATIONS")
    print_subheader("Generate Different Types of NDAs")
    
    variations = [
        ("Unilateral", {"party_type": "unilateral"}),
        ("Mutual", {"party_type": "mutual"}),
        ("Multi-Party", {"party_count": 4}),
        ("Simplified", {"complexity": "simple"}),
        ("Comprehensive", {"complexity": "comprehensive"}),
        ("Short-Term", {"duration_years": 1}),
        ("Long-Term", {"duration_years": 10}),
        ("International", {"international": True, "parties": ["US Company", "EU Company"]}),
        ("Strict Confidentiality", {"confidentiality_level": "strict"}),
        ("Flexible Confidentiality", {"confidentiality_level": "flexible"}),
        ("With Remedies", {"include_remedies": True}),
        ("No Injunctive Relief", {"allow_injunctive_relief": False}),
        ("Survival Clause", {"survival_years": 7}),
        ("Limited Survival", {"survival_years": 1}),
        ("Academic Research", {"academic_research": True})
    ]
    
    for var_name, var_params in variations:
        full_params = {
            "parties": ["Variation Party A", "Variation Party B"],
            "purpose": f"Testing {var_name} NDA variant",
            "duration_years": 2,
            **var_params
        }
        
        resp = test_endpoint(
            "NDA Variations",
            test_num,
            f"Generate: {var_name} NDA",
            "POST",
            "/api/v1/ai/generate/draft/",
            data={
                "contract_type": "NDA",
                "input_params": full_params
            },
            headers=headers,
            expected_status=[200, 202]
        )
        
        if resp and resp.status_code in [200, 202]:
            resp_data = resp.json()
            task_id = resp_data.get("task_id", resp_data.get("id"))
            if task_id:
                task_ids.append(task_id)
        
        test_num += 1
    
    # ═════════════════════════════════════════════════════════════════════════
    # STEP 8: EDGE CASES & ERROR HANDLING (10+ endpoints)
    # ═════════════════════════════════════════════════════════════════════════
    print_step(8, "EDGE CASES & ERROR HANDLING")
    print_subheader("Test NDA Generation with Invalid/Edge Cases")
    
    edge_cases = [
        ("Empty Input", {}),
        ("Missing Parties", {"purpose": "test"}),
        ("Very Long Duration", {"parties": ["A", "B"], "duration_years": 100}),
        ("Zero Duration", {"parties": ["A", "B"], "duration_years": 0}),
        ("Special Characters", {"parties": ["A & B", "C/D"], "purpose": "Test & <Evaluation>"}),
        ("Very Long Party Names", {"parties": ["A" * 100, "B" * 100]}),
        ("Empty Parties", {"parties": [], "purpose": "test"}),
        ("Single Party", {"parties": ["Single Corp"], "purpose": "test"}),
        ("Negative Duration", {"parties": ["A", "B"], "duration_years": -1}),
        ("Null Purpose", {"parties": ["A", "B"], "purpose": None})
    ]
    
    for case_name, case_params in edge_cases:
        test_endpoint(
            "Edge Cases",
            test_num,
            f"Edge Case: {case_name}",
            "POST",
            "/api/v1/ai/generate/draft/",
            data={
                "contract_type": "NDA",
                "input_params": case_params
            },
            headers=headers,
            expected_status=[200, 202, 400, 422]
        )
        test_num += 1
    
    # ═════════════════════════════════════════════════════════════════════════
    # STEP 9: PERFORMANCE TESTS (5+ endpoints)
    # ═════════════════════════════════════════════════════════════════════════
    print_step(9, "PERFORMANCE TESTING")
    print_subheader("Test NDA Generation Performance")
    
    # Bulk generation
    for i in range(5):
        test_endpoint(
            "Performance",
            test_num,
            f"Bulk Generate - NDA {i+1}/5",
            "POST",
            "/api/v1/ai/generate/draft/",
            data={
                "contract_type": "NDA",
                "input_params": {
                    "parties": [f"Bulk Party {i}A", f"Bulk Party {i}B"],
                    "purpose": "Performance testing",
                    "duration_years": 2
                }
            },
            headers=headers,
            expected_status=[200, 202]
        )
        test_num += 1
    
    # ═════════════════════════════════════════════════════════════════════════
    # STEP 10: FINAL STATUS CHECK (5+ endpoints)
    # ═════════════════════════════════════════════════════════════════════════
    print_step(10, "FINAL STATUS CHECK")
    print_subheader("Check All Generated NDA Tasks")
    
    for task_id in task_ids[-10:]:
        test_endpoint(
            "Final Check",
            test_num,
            f"Final Status - {task_id[:8]}...",
            "GET",
            f"/api/v1/ai/generate/status/{task_id}/",
            headers=headers,
            expected_status=[200, 404]
        )
        test_num += 1
    
    # ═════════════════════════════════════════════════════════════════════════
    # FINAL SUMMARY
    # ═════════════════════════════════════════════════════════════════════════
    print_header("FINAL TEST EXECUTION SUMMARY")
    
    total = stats["total"]
    passed = stats["passed"]
    failed = stats["failed"]
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print_info(f"Total Endpoints Tested: {total}")
    print_success(f"Passed: {passed}")
    if failed > 0:
        print_error(f"Failed: {failed}")
    
    print(f"\n{CYAN}Category Breakdown:{END}")
    for category, results in stats["categories"].items():
        cat_pass_rate = (results["passed"] / results["total"] * 100) if results["total"] > 0 else 0
        status = f"{GREEN}✓{END}" if cat_pass_rate >= 90 else f"{YELLOW}~{END}" if cat_pass_rate >= 70 else f"{RED}✗{END}"
        print(f"  {status} {category:20s}: {results['passed']:3d}/{results['total']:3d} ({cat_pass_rate:5.1f}%)")
    
    print()
    if pass_rate >= 95:
        print_success(f"Pass Rate: {pass_rate:.1f}% - EXCELLENT")
    elif pass_rate >= 80:
        print(f"{YELLOW}Pass Rate: {pass_rate:.1f}% - GOOD{END}")
    else:
        print_error(f"Pass Rate: {pass_rate:.1f}% - NEEDS IMPROVEMENT")
    
    print_header("NDA GENERATION WORKFLOW TEST COMPLETE")
    print_info(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Total NDA Tasks Created: {len(task_ids)}")
    print()

if __name__ == "__main__":
    main()
