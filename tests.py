"""
End-to-End Test Suite for Contract Generation with SignNow Integration
Tests complete workflow: Create → Details → Send to SignNow → Webhook → Download

Production-ready test script for validating contract generation and signature workflow.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:11000/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY4OTc5ODk5LCJpYXQiOjE3Njg4OTM0OTksImp0aSI6IjUyYzgwYzg5ZTRlMDQwYzVhODIyYTFmN2Q5Y2ZmNTZlIiwidXNlcl9pZCI6ImMyNTZiNjU5LTAzMWEtNDRiZi1iMDkxLTdiZTM4OGQ4NTkzNCJ9.cdqz312NR3tCX6iU_jIKB8U4VLCAToDb75Bp7_eFRKo"


def print_step(step, title):
    """Print formatted step header"""
    print(f"\n{'='*80}")
    print(f"STEP {step}: {title}")
    print(f"{'='*80}")


def print_response(response, show_body=True):
    """Print formatted response"""
    print(f"\nStatus: {response.status_code}")
    if show_body:
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response: {response.text[:500]}")


def get_headers():
    """Get request headers with authentication"""
    return {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }


class ContractTest:
    """Main test class for contract workflow"""

    def __init__(self):
        self.contract_id = None
        self.test_results = []

    def test_1_create_contract(self):
        """Test 1: Create contract with clauses"""
        print_step(1, "CREATE CONTRACT WITH CLAUSES")

        payload = {
            "contract_type": "nda",
            "data": {
                "date": "2026-01-20",
                "1st_party_name": "TechCorp Inc.",
                "2nd_party_name": "DevSoft LLC",
                "agreement_type": "Mutual",
                "1st_party_relationship": "Technology Company",
                "2nd_party_relationship": "Software Developer",
                "governing_law": "California",
                "1st_party_printed_name": "John Smith",
                "2nd_party_printed_name": "Jane Doe",
                "clauses": [
                    {
                        "name": "Confidentiality",
                        "description": "All shared information must remain confidential"
                    },
                    {
                        "name": "Non-Compete",
                        "description": "No competing business for 2 years"
                    }
                ]
            }
        }

        response = requests.post(f"{BASE_URL}/create/", headers=get_headers(), json=payload)
        print_response(response)

        if response.status_code == 201:
            self.contract_id = response.json().get('contract_id')
            print(f"\n✅ Contract created: {self.contract_id}")
            self.test_results.append(("Create Contract", "PASS", 201))
            return True
        else:
            print(f"\n❌ Failed to create contract")
            self.test_results.append(("Create Contract", "FAIL", response.status_code))
            return False

    def test_2_get_details_before_signing(self):
        """Test 2: Get contract details before signing"""
        print_step(2, "GET DETAILS (BEFORE SIGNING)")

        if not self.contract_id:
            print("❌ No contract ID")
            self.test_results.append(("Get Details (Before)", "SKIP", None))
            return False

        response = requests.get(
            f"{BASE_URL}/details/?contract_id={self.contract_id}",
            headers=get_headers()
        )
        print_response(response)

        if response.status_code == 200:
            data = response.json()
            clauses_count = len(data.get('contract', {}).get('clauses', []))
            is_signed = bool(data.get('contract', {}).get('signed'))
            print(f"\n✅ Clauses: {clauses_count}, Signed: {is_signed}")
            self.test_results.append(("Get Details (Before)", "PASS", 200))
            return True
        else:
            self.test_results.append(("Get Details (Before)", "FAIL", response.status_code))
            return False

    def test_3_send_to_signnow(self):
        """Test 3: Send contract to SignNow"""
        print_step(3, "SEND TO SIGNNOW")

        if not self.contract_id:
            self.test_results.append(("Send to SignNow", "SKIP", None))
            return False

        payload = {
            "contract_id": self.contract_id,
            "signer_email": "jane@devsoft.com",
            "signer_name": "Jane Doe"
        }

        response = requests.post(
            f"{BASE_URL}/send-to-signnow/",
            headers=get_headers(),
            json=payload
        )
        print_response(response)

        if response.status_code == 200:
            print(f"\n✅ Sent to SignNow")
            self.test_results.append(("Send to SignNow", "PASS", 200))
            return True
        else:
            self.test_results.append(("Send to SignNow", "FAIL", response.status_code))
            return False

    def test_4_webhook_received(self):
        """Test 4: Simulate SignNow webhook"""
        print_step(4, "SIGNNOW WEBHOOK (USER SIGNED)")

        if not self.contract_id:
            self.test_results.append(("Webhook Received", "SKIP", None))
            return False

        payload = {
            "event": "document.signed",
            "document": {
                "contract_id": self.contract_id,
                "signed_at": "2026-01-20T15:30:45Z",
                "signed_pdf_url": "https://signnow-storage.s3.amazonaws.com/signed_pdf_123.pdf",
                "signers": [
                    {
                        "full_name": "Jane Doe",
                        "email": "jane@devsoft.com",
                        "signed_at": "2026-01-20T15:30:45Z"
                    }
                ]
            }
        }

        response = requests.post(
            f"{BASE_URL}/webhook/signnow/",
            headers=get_headers(),
            json=payload
        )
        print_response(response)

        if response.status_code == 200:
            print(f"\n✅ Webhook received")
            self.test_results.append(("Webhook Received", "PASS", 200))
            return True
        else:
            self.test_results.append(("Webhook Received", "FAIL", response.status_code))
            return False

    def test_5_get_details_after_signing(self):
        """Test 5: Get contract details after signing"""
        print_step(5, "GET DETAILS (AFTER SIGNING)")

        if not self.contract_id:
            self.test_results.append(("Get Details (After)", "SKIP", None))
            return False

        response = requests.get(
            f"{BASE_URL}/details/?contract_id={self.contract_id}",
            headers=get_headers()
        )
        print_response(response)

        if response.status_code == 200:
            data = response.json()
            signed_status = data.get('contract', {}).get('signed', {}).get('status')
            signers = data.get('contract', {}).get('signed', {}).get('signers', [])
            print(f"\n✅ Status: {signed_status}")
            if signers:
                print(f"   Signer: {signers[0].get('name')} ({signers[0].get('email')})")
            self.test_results.append(("Get Details (After)", "PASS", 200))
            return True
        else:
            self.test_results.append(("Get Details (After)", "FAIL", response.status_code))
            return False

    def test_6_download_pdf(self):
        """Test 6: Download signed PDF"""
        print_step(6, "DOWNLOAD SIGNED PDF")

        if not self.contract_id:
            self.test_results.append(("Download PDF", "SKIP", None))
            return False

        response = requests.get(
            f"{BASE_URL}/download/?contract_id={self.contract_id}",
            headers=get_headers()
        )

        print(f"\nStatus: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Length: {len(response.content)} bytes")

        if response.status_code == 200 and response.content[:4] == b'%PDF':
            pdf_filename = f"contract_{self.contract_id}.pdf"
            with open(pdf_filename, 'wb') as f:
                f.write(response.content)
            print(f"\n✅ PDF Downloaded: {pdf_filename} ({len(response.content)} bytes)")
            self.test_results.append(("Download PDF", "PASS", 200))
            return True
        else:
            self.test_results.append(("Download PDF", "FAIL", response.status_code))
            return False

    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*80)
        print("CONTRACT GENERATION & SIGNNOW INTEGRATION TEST SUITE")
        print("="*80)

        tests = [
            self.test_1_create_contract,
            self.test_2_get_details_before_signing,
            self.test_3_send_to_signnow,
            self.test_4_webhook_received,
            self.test_5_get_details_after_signing,
            self.test_6_download_pdf
        ]

        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"\n❌ Test error: {str(e)}")
                test_name = test.__doc__.split('\n')[1].strip() if test.__doc__ else "Unknown"
                self.test_results.append((test_name, "ERROR", str(e)))

        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)

        passed = sum(1 for _, status, _ in self.test_results if status == "PASS")
        failed = sum(1 for _, status, _ in self.test_results if status == "FAIL")
        skipped = sum(1 for _, status, _ in self.test_results if status == "SKIP")

        print(f"\n{'Test':<30} {'Status':<10} {'Code':<10}")
        print("-" * 50)

        for test_name, status, code in self.test_results:
            status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⊘"
            print(f"{test_name:<30} {status_icon} {status:<8} {str(code):<10}")

        print("-" * 50)
        print(f"Total: {len(self.test_results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")

        if failed == 0 and passed > 0:
            print("\n✅ ALL TESTS PASSED")
            return 0
        else:
            print(f"\n❌ {failed} TEST(S) FAILED")
            return 1


def main():
    """Main entry point"""
    tester = ContractTest()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
