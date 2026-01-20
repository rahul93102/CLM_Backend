#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:11000/api/v1"
JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY4OTIyNjk2LCJpYXQiOjE3Njg4MzYyOTYsImp0aSI6ImY1NWU1YzlhOTU5MjQwZTY5N2QzNWMxNTYwNWFiNDg0IiwidXNlcl9pZCI6IjAwOWQ2NDEyLThmYjUtNGE0Yy05OTBmLTVlMDkyMzIzODk2YyJ9.aKR9DHQxau5GQylpLPEZfgELBwb7T2bWygIgP1geM4Y"
H = {"Authorization": f"Bearer {JWT}", "Content-Type": "application/json"}

tests = []

# Test 1: Agency
d1 = {"contract_type": "agency_agreement", "data": {"effective_date": "2026-01-20", "principal_name": "Global Marketing", "principal_address": "123 Business", "agent_name": "Digital", "agent_address": "456 Commerce", "monthly_compensation": "5000", "invoice_submission_date": "25", "payment_method": "Wire", "payment_address": "456", "contract_end_date": "2027-01-19", "principal_printed_name": "Robert", "agent_printed_name": "Sarah"}}
r1 = requests.post(f"{BASE_URL}/create/", json=d1, headers=H)
tests.append(("Agency Agreement", r1.status_code, r1.json().get("success"), r1.json().get("file_size")))

# Test 2: Property
d2 = {"contract_type": "property_management", "data": {"effective_date": "2026-01-20", "owner_name": "Michael", "owner_address": "789 Ln", "manager_name": "Premier", "manager_address": "321 Dr", "property_address": "789 Ln", "repair_approval_limit": "5000", "governing_law": "California", "owner_printed_name": "Michael", "manager_printed_name": "Patricia"}}
r2 = requests.post(f"{BASE_URL}/create/", json=d2, headers=H)
tests.append(("Property Management", r2.status_code, r2.json().get("success"), r2.json().get("file_size")))

# Test 3: Get Templates
r3 = requests.get(f"{BASE_URL}/templates/", headers=H)
tests.append(("Get Templates", r3.status_code, r3.json().get("success"), len(r3.json().get("templates", {}))))

# Test 4: Get Fields
r4 = requests.get(f"{BASE_URL}/fields/?contract_type=nda", headers=H)
tests.append(("Get NDA Fields", r4.status_code, r4.json().get("success"), len(r4.json().get("required_fields", []))))

print("\n" + "="*80)
print("CONTRACT GENERATION API - TEST RESULTS")
print("="*80 + "\n")
for test_name, status, success, value in tests:
    symbol = "✅" if success else "❌"
    print(f"{symbol} {test_name:30} | Status: {status} | Result: {success} | Value: {value}")
print("\n" + "="*80)
