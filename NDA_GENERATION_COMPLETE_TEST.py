#!/usr/bin/env python3
"""
NDA GENERATION SYSTEM - COMPLETE WORKFLOW TEST
Demonstrates all 5 steps of NDA generation with actual API testing
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:11000/api/nda"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

# Color codes for output
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_section(title: str):
    """Print a section header"""
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}{title}{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")

def print_subsection(title: str):
    """Print a subsection header"""
    print(f"\n{BOLD}{YELLOW}{title}{RESET}")
    print(f"{YELLOW}{'-'*80}{RESET}\n")

def print_response(label: str, data: Any, indent: int = 0):
    """Pretty print response data"""
    prefix = " " * indent
    print(f"{prefix}{GREEN}{label}:{RESET}")
    if isinstance(data, dict):
        print(f"{prefix}{json.dumps(data, indent=2)}")
    else:
        print(f"{prefix}{data}")

def print_error(message: str):
    """Print error message"""
    print(f"{RED}{message}{RESET}")

def print_success(message: str):
    """Print success message"""
    print(f"{GREEN}✓ {message}{RESET}")

# ============================================================================
# STEP 1: TEMPLATE DISCOVERY
# ============================================================================

def step_1_template_discovery():
    """STEP 1: Get available templates"""
    print_section("STEP 1: TEMPLATE DISCOVERY")
    print("Retrieving all available NDA templates...\n")
    
    print_subsection("REQUEST")
    print("Method: GET")
    print("Endpoint: /api/nda/templates")
    print("Headers:", json.dumps(HEADERS, indent=2))
    
    try:
        response = requests.get(f"{BASE_URL}/templates", headers=HEADERS)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print_subsection("RESPONSE")
            print_success(f"Retrieved {len(data['templates'])} templates")
            
            # Print template summary
            for template in data['templates']:
                print(f"\n{BOLD}Template ID: {template['id']}{RESET}")
                print(f"  Name: {template['name']}")
                print(f"  Type: {template['type']}")
                print(f"  Description: {template['description']}")
                print(f"  Sections: {template['sections']}")
                print(f"  Clauses: {template['clauses']}")
                print(f"  Appendices: {template['appendices']}")
                print(f"  Character Count: {template['character_count']:,}")
                print(f"  Estimated Pages: {template['estimated_pages']}")
                print(f"  Customizable Fields: {template['customizable_fields']}")
            
            return data['templates'][0]['id']  # Return first template ID
        else:
            print_error(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return None

# ============================================================================
# STEP 2: CLAUSE INSPECTION
# ============================================================================

def step_2_clause_inspection(template_id: str):
    """STEP 2: Get clauses for selected template"""
    print_section("STEP 2: CLAUSE INSPECTION")
    print(f"Retrieving clauses for template: {template_id}\n")
    
    print_subsection("REQUEST")
    print("Method: GET")
    print(f"Endpoint: /api/nda/templates/{template_id}/clauses")
    
    try:
        response = requests.get(
            f"{BASE_URL}/templates/{template_id}/clauses",
            headers=HEADERS
        )
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print_subsection("RESPONSE SUMMARY")
            print_success(f"Template: {data['template_name']}")
            print_success(f"Total Sections: {data['total_sections']}")
            print_success(f"Total Clauses: {data['total_clauses']}")
            
            # Print sections overview
            print(f"\n{BOLD}DOCUMENT SECTIONS:{RESET}")
            for section in data['sections']:
                print(f"\n  Section {section['section_number']}: {section['title']}")
                print(f"    Clauses: {len(section['clauses'])}")
                for clause in section['clauses'][:2]:  # Show first 2 clauses
                    print(f"      • {clause['number']} - {clause['title']}")
                if len(section['clauses']) > 2:
                    print(f"      ... and {len(section['clauses']) - 2} more")
            
            # Print appendices
            print(f"\n{BOLD}APPENDICES:{RESET}")
            for appendix in data['appendices']:
                print(f"\n  Appendix {appendix['number']}: {appendix['title']}")
                print(f"    Optional: {appendix['optional']}")
                print(f"    Description: {appendix['description']}")
            
            # Print variables required
            print(f"\n{BOLD}VARIABLES REQUIRED:{RESET}")
            for category, variables in data['variables_required'].items():
                print(f"\n  {category}:")
                for var in variables:
                    print(f"    • {var}")
            
            return data
        else:
            print_error(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return None

# ============================================================================
# STEP 3: PREVIEW GENERATION (Variable Input)
# ============================================================================

def step_3_preview_generation(template_id: str):
    """STEP 3: Generate preview with variables"""
    print_section("STEP 3: PREVIEW GENERATION (VARIABLE INPUT)")
    print("Generating a preview with party information and variables...\n")
    
    # Prepare request payload
    payload = {
        "template_id": template_id,
        "party_1": {
            "name": "TechCorp Inc.",
            "address": "123 Silicon Valley Blvd, San Francisco, CA 94105",
            "representative": "Jane Smith",
            "title": "Chief Technology Officer"
        },
        "party_2": {
            "name": "InnovateLabs LLC",
            "address": "456 Innovation Drive, Mountain View, CA 94043",
            "representative": "John Doe",
            "title": "VP of Business Development"
        },
        "agreement_details": {
            "jurisdiction": "California",
            "duration_years": 5,
            "effective_date": "2025-01-18",
            "purpose": "Evaluation of technology partnership opportunities"
        },
        "customization": {
            "care_standard": "industry standard care",
            "permitted_use": "evaluation of business opportunities",
            "advisor_types": ["attorneys", "accountants", "financial advisors"],
            "return_method": "destruction",
            "residual_memory_exception": True
        },
        "appendices": {
            "confidential_information_schedule": True,
            "authorized_recipients": True,
            "security_requirements": True
        }
    }
    
    print_subsection("REQUEST")
    print("Method: POST")
    print("Endpoint: /api/nda/generate/preview")
    print("\nPayload (Party Information):")
    print(f"  Party 1: {payload['party_1']['name']}")
    print(f"  Party 2: {payload['party_2']['name']}")
    print(f"  Jurisdiction: {payload['agreement_details']['jurisdiction']}")
    print(f"  Duration: {payload['agreement_details']['duration_years']} years")
    print(f"  Purpose: {payload['agreement_details']['purpose']}")
    print(f"  Appendices: All 3 included")
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate/preview",
            json=payload,
            headers=HEADERS
        )
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 202:
            data = response.json()
            
            print_subsection("RESPONSE")
            print_success(f"Preview Generated Successfully")
            print_success(f"Preview ID: {data['preview_id']}")
            print_success(f"Expires in: {data['preview_expires_in_seconds']} seconds")
            
            print(f"\n{BOLD}DOCUMENT STATISTICS:{RESET}")
            stats = data['preview_statistics']
            print(f"  Total Characters: {stats['total_characters']:,}")
            print(f"  Total Words: {stats['total_words']:,}")
            print(f"  Estimated Pages: {stats['estimated_pages']}")
            print(f"  Sections Included: {stats['sections_included']}")
            print(f"  Clauses Included: {stats['clauses_included']}")
            print(f"  Appendices Included: {stats['appendices_included']}")
            
            print(f"\n{BOLD}PREVIEW (First 500 characters):{RESET}")
            preview_text = data['preview_document'][:500]
            print(f"{preview_text}...")
            
            return data['preview_id']
        else:
            print_error(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return None

# ============================================================================
# STEP 4: ASYNC GENERATION
# ============================================================================

def step_4_async_generation(preview_id: str):
    """STEP 4: Start async generation"""
    print_section("STEP 4: ASYNC GENERATION (START JOB)")
    print("Starting background NDA generation job...\n")
    
    payload = {
        "preview_id": preview_id,
        "formats": ["markdown", "pdf", "docx"],
        "delivery": {
            "email": True,
            "email_recipients": ["jane@techcorp.com", "john@innovatelabs.com"],
            "add_to_library": True,
            "webhook_url": "https://example.com/webhooks/nda-generated"
        },
        "metadata": {
            "project_name": "Tech Partnership Evaluation",
            "tags": ["partnership", "evaluation", "confidential"],
            "reference_number": "NDA-2025-001"
        }
    }
    
    print_subsection("REQUEST")
    print("Method: POST")
    print("Endpoint: /api/nda/generate")
    print("\nPayload:")
    print(f"  Preview ID: {preview_id}")
    print(f"  Formats: markdown, pdf, docx")
    print(f"  Email Recipients: 2")
    print(f"  Add to Library: Yes")
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate",
            json=payload,
            headers=HEADERS
        )
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 202:
            data = response.json()
            
            print_subsection("RESPONSE")
            print_success(f"Generation Job Started")
            print_success(f"Job ID: {data['job']['job_id']}")
            print_success(f"Document ID: {data['document']['document_id']}")
            print_success(f"Current Status: {data['job']['status']}")
            print_success(f"Estimated Time: {data['estimated_time_seconds']} seconds")
            
            print(f"\n{BOLD}FORMATS REQUESTED:{RESET}")
            for fmt in data['formats_requested']:
                print(f"  • {fmt}")
            
            print(f"\n{BOLD}DELIVERY SETTINGS:{RESET}")
            delivery = data['delivery_settings']
            print(f"  Email: {delivery['email_enabled']}")
            print(f"  Library: {delivery['library_enabled']}")
            print(f"  Webhook: {delivery['webhook_enabled']}")
            
            return data['job']['job_id'], data['document']['document_id']
        else:
            print_error(f"Error: {response.status_code}")
            print(response.text)
            return None, None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return None, None

# ============================================================================
# POLLING - Check Job Progress
# ============================================================================

def poll_job_status(job_id: str, max_polls: int = 50):
    """Poll job status until complete"""
    print_subsection("POLLING JOB PROGRESS")
    print(f"Polling job: {job_id}\n")
    
    poll_count = 0
    
    while poll_count < max_polls:
        try:
            response = requests.get(
                f"{BASE_URL}/job/{job_id}/status",
                headers=HEADERS
            )
            
            if response.status_code == 200:
                data = response.json()
                
                progress = data['progress_percentage']
                stage = data['current_stage']
                message = data['message']
                
                # Print progress
                bar_length = 40
                filled = int(bar_length * progress / 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                
                print(f"[{bar}] {progress}% - {stage}: {message}")
                
                if data['status'] == 'completed':
                    print_subsection("GENERATION COMPLETE ✓")
                    
                    print(f"\n{BOLD}GENERATION RESULTS:{RESET}")
                    print_success(f"Status: {data['status']}")
                    print_success(f"Total Time: {data['generation_time_seconds']} seconds")
                    print_success(f"Formats Generated: {len(data['formats_generated'])}")
                    
                    print(f"\n{BOLD}FORMATS GENERATED:{RESET}")
                    for fmt in data['formats_generated']:
                        print(f"  ✓ {fmt}")
                    
                    print(f"\n{BOLD}DELIVERY STATUS:{RESET}")
                    for service, delivery_info in data['deliveries_sent'].items():
                        if delivery_info.get('sent') or delivery_info.get('added'):
                            status = "✓ Sent" if delivery_info.get('sent') else "✓ Added"
                            print(f"  {status}: {service}")
                    
                    return True
                
                time.sleep(2)
                poll_count += 1
            else:
                print_error(f"Error: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print_error(f"Request failed: {e}")
            return False
    
    print_error(f"Polling timeout after {max_polls} attempts")
    return False

# ============================================================================
# STEP 5: RESULT RETRIEVAL
# ============================================================================

def step_5_result_retrieval(document_id: str):
    """STEP 5: Retrieve and preview generated document"""
    print_section("STEP 5: RESULT RETRIEVAL & PREVIEW")
    print(f"Retrieving generated document: {document_id}\n")
    
    print_subsection("REQUEST 1: GET DOCUMENT METADATA")
    print("Method: GET")
    print(f"Endpoint: /api/nda/documents/{document_id}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/documents/{document_id}",
            headers=HEADERS
        )
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            doc = data['document']
            
            print_subsection("RESPONSE")
            print_success(f"Document Retrieved Successfully")
            print_success(f"Title: {doc['title']}")
            print_success(f"Status: {doc['status']}")
            
            print(f"\n{BOLD}PARTIES:{RESET}")
            print(f"  Party 1: {doc['parties']['party_1']}")
            print(f"  Party 2: {doc['parties']['party_2']}")
            
            print(f"\n{BOLD}TERMS:{RESET}")
            print(f"  Jurisdiction: {doc['terms']['jurisdiction']}")
            print(f"  Duration: {doc['terms']['duration']}")
            print(f"  Effective Date: {doc['terms']['effective_date']}")
            
            print(f"\n{BOLD}STATISTICS:{RESET}")
            stats = doc['statistics']
            print(f"  Characters: {stats['total_characters']:,}")
            print(f"  Words: {stats['total_words']:,}")
            print(f"  Pages: {stats['estimated_pages']}")
            print(f"  Sections: {stats['sections']}")
            print(f"  Clauses: {stats['clauses']}")
            print(f"  Appendices: {stats['appendices']}")
            
            print(f"\n{BOLD}AVAILABLE FORMATS:{RESET}")
            for fmt, info in doc['formats_available'].items():
                if info['available']:
                    print(f"  ✓ {fmt.upper()}")
                    print(f"    Size: {info['size_formatted']}")
            
            print(f"\n{BOLD}AVAILABLE ACTIONS:{RESET}")
            for action, url in doc['actions'].items():
                print(f"  • {action}: {url}")
            
            return document_id
        else:
            print_error(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return None

def get_document_preview(document_id: str):
    """Get HTML preview of document"""
    print_subsection("REQUEST 2: GET DOCUMENT PREVIEW")
    print("Method: GET")
    print(f"Endpoint: /api/nda/documents/{document_id}/preview")
    
    try:
        response = requests.get(
            f"{BASE_URL}/documents/{document_id}/preview",
            headers={"Accept": "text/html"}
        )
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            print_subsection("RESPONSE")
            print_success(f"HTML Preview Retrieved")
            
            # Show first 1000 characters of HTML
            preview_html = response.text[:1000]
            print(f"\n{BOLD}HTML Preview (first 1000 characters):{RESET}")
            print(preview_html + "...")
            
            return True
        else:
            print_error(f"Error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Execute complete NDA generation workflow"""
    
    print(f"\n{BOLD}{BLUE}")
    print("╔" + "═"*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "NDA GENERATION SYSTEM - COMPLETE WORKFLOW TEST".center(78) + "║")
    print("║" + " "*78 + "║")
    print("║" + "All 5 Steps with Actual API Testing".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "═"*78 + "╝")
    print(f"{RESET}\n")
    
    # Step 1: Template Discovery
    template_id = step_1_template_discovery()
    if not template_id:
        print_error("Failed to retrieve templates. Exiting.")
        return
    
    # Step 2: Clause Inspection
    clauses = step_2_clause_inspection(template_id)
    if not clauses:
        print_error("Failed to retrieve clauses. Exiting.")
        return
    
    # Step 3: Preview Generation
    preview_id = step_3_preview_generation(template_id)
    if not preview_id:
        print_error("Failed to generate preview. Exiting.")
        return
    
    # Step 4: Async Generation
    job_id, document_id = step_4_async_generation(preview_id)
    if not job_id or not document_id:
        print_error("Failed to start generation. Exiting.")
        return
    
    # Poll job status
    poll_success = poll_job_status(job_id)
    if not poll_success:
        print_error("Job polling failed. Exiting.")
        return
    
    # Step 5: Result Retrieval
    doc_retrieved = step_5_result_retrieval(document_id)
    if not doc_retrieved:
        print_error("Failed to retrieve document. Exiting.")
        return
    
    # Get preview
    get_document_preview(document_id)
    
    # Final Summary
    print_section("✓ COMPLETE WORKFLOW TEST SUCCESSFUL")
    print(f"\n{BOLD}WORKFLOW COMPLETED SUCCESSFULLY!{RESET}\n")
    print(f"{GREEN}Summary:{RESET}")
    print(f"  ✓ Step 1: Template Discovery - PASSED")
    print(f"  ✓ Step 2: Clause Inspection - PASSED")
    print(f"  ✓ Step 3: Preview Generation - PASSED")
    print(f"  ✓ Step 4: Async Generation - PASSED")
    print(f"  ✓ Step 5: Result Retrieval - PASSED")
    print(f"\n{GREEN}Document Generated:{RESET}")
    print(f"  ID: {document_id}")
    print(f"  Formats: markdown, pdf, docx")
    print(f"  Status: Ready for download\n")

if __name__ == "__main__":
    main()
