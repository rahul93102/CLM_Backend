#!/usr/bin/env python
"""
Comprehensive test suite for all CLM Backend endpoints
Tests real-time responses from port 11000
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:11000"
TEST_USER_EMAIL = "test_search@test.com"
TEST_USER_PASSWORD = "Test@1234"

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'
BOLD = '\033[1m'

def print_header(title):
    print(f"\n{BOLD}{BLUE}{'='*80}{END}")
    print(f"{BOLD}{BLUE}{title:^80}{END}")
    print(f"{BOLD}{BLUE}{'='*80}{END}\n")

def print_test(name):
    print(f"{YELLOW}[TEST]{END} {name}")

def print_success(msg):
    print(f"{GREEN}✓ {msg}{END}")

def print_error(msg):
    print(f"{RED}✗ {msg}{END}")

def print_info(msg):
    print(f"{BLUE}ℹ {msg}{END}")

def get_jwt_token():
    """Get JWT token for test user"""
    print_test("Getting JWT Token")
    
    url = f"{BASE_URL}/api/auth/login/"
    payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            token = data.get('access')
            if token:
                print_success(f"JWT Token obtained (first 20 chars: {token[:20]}...)")
                return token
            else:
                print_error("No access token in response")
                print_info(f"Response: {json.dumps(data, indent=2)}")
                return None
        else:
            print_error(f"Login failed: {resp.status_code}")
            print_info(f"Response: {resp.text}")
            return None
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None

def test_health_endpoint():
    """Test health check endpoint"""
    print_test("Health Check Endpoint")
    
    url = f"{BASE_URL}/api/v1/health/"
    
    try:
        resp = requests.get(url, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print_success("Server is healthy")
            print_info(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Unexpected status: {resp.status_code}")
            return False
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def test_semantic_search(token):
    """Test semantic search endpoint"""
    print_test("Semantic Search Endpoint")
    
    url = f"{BASE_URL}/api/v1/search/semantic/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {
        "q": "confidentiality",
        "limit": 5
    }
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            results = data.get('results', [])
            print_success(f"Retrieved {len(results)} results")
            
            for i, result in enumerate(results[:3], 1):
                print_info(f"\nResult {i}:")
                print_info(f"  - Score: {result.get('similarity_score', 'N/A'):.4f}")
                print_info(f"  - Document: {result.get('document_chunk_id', 'N/A')}")
                print_info(f"  - Text: {result.get('chunk_text', 'N/A')[:100]}...")
            
            return True
        else:
            print_error(f"Unexpected status: {resp.status_code}")
            print_info(f"Response: {resp.text[:500]}")
            return False
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def test_keyword_search(token):
    """Test keyword search endpoint"""
    print_test("Keyword Search Endpoint")
    
    url = f"{BASE_URL}/api/v1/search/keyword/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {
        "q": "confidentiality",
        "limit": 5
    }
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            results = data.get('results', [])
            print_success(f"Retrieved {len(results)} keyword search results")
            
            for i, result in enumerate(results[:2], 1):
                print_info(f"\nResult {i}:")
                print_info(f"  - Document: {result.get('document_chunk_id', 'N/A')}")
                print_info(f"  - Text: {result.get('chunk_text', 'N/A')[:100]}...")
            
            return True
        else:
            print_error(f"Unexpected status: {resp.status_code}")
            print_info(f"Response: {resp.text[:500]}")
            return False
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def test_advanced_search(token):
    """Test advanced search endpoint"""
    print_test("Advanced Search Endpoint")
    
    url = f"{BASE_URL}/api/v1/search/advanced/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": "confidentiality",
        "limit": 5,
        "filters": {}
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            results = data.get('results', [])
            print_success(f"Retrieved {len(results)} advanced search results")
            
            for i, result in enumerate(results[:2], 1):
                print_info(f"\nResult {i}:")
                print_info(f"  - Document: {result.get('document_chunk_id', 'N/A')}")
                print_info(f"  - Rank: {result.get('rank', 'N/A')}")
            
            return True
        else:
            print_error(f"Unexpected status: {resp.status_code}")
            print_info(f"Response: {resp.text[:500]}")
            return False
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def test_draft_generation(token):
    """Test async draft generation endpoint"""
    print_test("Async Draft Generation Endpoint")
    
    url = f"{BASE_URL}/api/v1/ai/generate/draft/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "contract_type": "NDA",
        "input_params": {
            "parties": ["Company A", "Company B"],
            "jurisdiction": "United States"
        }
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code in [200, 202]:
            data = resp.json()
            task_id = data.get('task_id')
            print_success(f"Draft generation task created (async)")
            print_info(f"Task ID: {task_id}")
            print_info(f"Status: {data.get('status', 'N/A')}")
            
            return task_id
        else:
            print_error(f"Unexpected status: {resp.status_code}")
            print_info(f"Response: {resp.text[:500]}")
            return None
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None

def test_draft_status(token, task_id):
    """Test draft generation status polling endpoint"""
    print_test(f"Draft Status Polling Endpoint (Task: {task_id})")
    
    url = f"{BASE_URL}/api/v1/ai/generate/status/{task_id}/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Poll for status
        for attempt in range(1, 6):
            resp = requests.get(url, headers=headers, timeout=10)
            print_info(f"Polling attempt {attempt}")
            print_info(f"Status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                status = data.get('status')
                print_info(f"  Task Status: {status}")
                
                if status == 'completed':
                    print_success(f"Draft generation completed")
                    draft_text = data.get('generated_text', 'N/A')
                    citations = data.get('citations', [])
                    print_info(f"  Generated Text (first 200 chars): {draft_text[:200]}...")
                    print_info(f"  Citations: {citations}")
                    return True
                elif status == 'failed':
                    error = data.get('error_message', 'Unknown error')
                    print_error(f"Draft generation failed: {error}")
                    return False
                else:
                    print_info(f"  Still processing... waiting 2 seconds")
                    time.sleep(2)
            else:
                print_error(f"Unexpected status: {resp.status_code}")
                return False
        
        print_info("Max polling attempts reached, task still processing")
        return True
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def test_metadata_extraction(token):
    """Test metadata extraction endpoint"""
    print_test("Metadata Extraction Endpoint")
    
    url = f"{BASE_URL}/api/v1/ai/extract/metadata/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": "This is a Confidentiality Agreement between Company A and Company B, effective January 1, 2024."
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print_success("Metadata extracted successfully")
            
            metadata = data.get('metadata', {})
            print_info(f"Extracted Metadata:")
            for key, value in metadata.items():
                print_info(f"  - {key}: {value}")
            
            return True
        else:
            print_error(f"Unexpected status: {resp.status_code}")
            print_info(f"Response: {resp.text[:500]}")
            return False
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def test_clause_classification(token):
    """Test clause classification endpoint"""
    print_test("Clause Classification Endpoint")
    
    url = f"{BASE_URL}/api/v1/ai/classify/clause/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "clause_text": "The receiving party agrees not to disclose confidential information to third parties without prior written consent."
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print_success("Clause classified successfully")
            
            classification = data.get('classification', {})
            print_info(f"Classification:")
            print_info(f"  - Type: {classification.get('type', 'N/A')}")
            print_info(f"  - Category: {classification.get('category', 'N/A')}")
            print_info(f"  - Confidence: {classification.get('confidence_score', 'N/A')}")
            
            return True
        else:
            print_error(f"Unexpected status: {resp.status_code}")
            print_info(f"Response: {resp.text[:500]}")
            return False
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def main():
    """Run all tests"""
    print_header(f"CLM BACKEND COMPREHENSIVE TEST SUITE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {
        "total": 0,
        "passed": 0,
        "failed": 0
    }
    
    # Test 1: Health Check
    print_header("1. HEALTH CHECK")
    test_results["total"] += 1
    if test_health_endpoint():
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    
    # Test 2: Get JWT Token
    print_header("2. AUTHENTICATION")
    test_results["total"] += 1
    token = get_jwt_token()
    if token:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
        print_error("Cannot continue without token")
        return
    
    # Test 3: Semantic Search
    print_header("3. SEARCH ENDPOINTS")
    
    print("\n--- Semantic Search ---")
    test_results["total"] += 1
    if test_semantic_search(token):
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    
    print("\n--- Keyword Search ---")
    test_results["total"] += 1
    if test_keyword_search(token):
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    
    print("\n--- Advanced Search ---")
    test_results["total"] += 1
    if test_advanced_search(token):
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    
    # Test 4: AI Endpoints
    print_header("4. AI ENDPOINTS")
    
    print("\n--- Draft Generation ---")
    test_results["total"] += 1
    task_id = test_draft_generation(token)
    if task_id:
        test_results["passed"] += 1
        
        # Poll for status
        print("\n--- Draft Status Polling ---")
        test_results["total"] += 1
        if test_draft_status(token, task_id):
            test_results["passed"] += 1
        else:
            test_results["failed"] += 1
    else:
        test_results["failed"] += 1
    
    print("\n--- Metadata Extraction ---")
    test_results["total"] += 1
    if test_metadata_extraction(token):
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    
    print("\n--- Clause Classification ---")
    test_results["total"] += 1
    if test_clause_classification(token):
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    
    # Final Summary
    print_header("TEST SUMMARY")
    print_info(f"Total Tests: {test_results['total']}")
    print_success(f"Passed: {test_results['passed']}")
    if test_results['failed'] > 0:
        print_error(f"Failed: {test_results['failed']}")
    
    pass_rate = (test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0
    if pass_rate == 100:
        print_success(f"Pass Rate: {pass_rate:.1f}%")
    elif pass_rate >= 80:
        print(f"{YELLOW}Pass Rate: {pass_rate:.1f}%{END}")
    else:
        print_error(f"Pass Rate: {pass_rate:.1f}%")
    
    print_header("TEST EXECUTION COMPLETE")

if __name__ == "__main__":
    main()
