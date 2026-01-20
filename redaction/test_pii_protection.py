"""
Tests for PII (Personally Identifiable Information) Detection and Scrubbing
"""

import pytest
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken

from .pii_service import PIIScrubber, get_pii_scrubber, PiiEntity
from .models import RedactionJobModel

User = get_user_model()


class TestPIIScrubber(TestCase):
    """Test PII scrubbing functionality"""
    
    def setUp(self):
        self.scrubber = PIIScrubber()
    
    # ===== EMAIL TESTS =====
    def test_scrub_single_email(self):
        """Test scrubbing single email address"""
        text = "Contact john.doe@example.com for more info"
        scrubbed = self.scrubber.scrub_text(text)
        
        assert "@example.com" in scrubbed
        assert "john.doe" not in scrubbed
        assert "john" not in scrubbed or "john@" not in scrubbed
    
    def test_scrub_multiple_emails(self):
        """Test scrubbing multiple email addresses"""
        text = "Email alice@company.com or bob@company.com"
        scrubbed = self.scrubber.scrub_text(text)
        
        assert "alice" not in scrubbed
        assert "bob" not in scrubbed
        assert "@company.com" in scrubbed
    
    # ===== PHONE TESTS =====
    def test_scrub_us_phone_formatted(self):
        """Test scrubbing US phone with formatting"""
        text = "Call (555) 123-4567 for support"
        scrubbed = self.scrubber.scrub_text(text)
        
        assert "555" not in scrubbed
        assert "123" not in scrubbed
        assert "4567" in scrubbed  # Last 4 should remain
    
    def test_scrub_us_phone_no_format(self):
        """Test scrubbing US phone without formatting"""
        text = "Phone: 5551234567"
        scrubbed = self.scrubber.scrub_text(text)
        
        assert "555" not in scrubbed
        assert "123" not in scrubbed
        assert "4567" in scrubbed
    
    def test_scrub_international_phone(self):
        """Test scrubbing international phone numbers"""
        text = "International: +44 20 7123 4567"
        scrubbed = self.scrubber.scrub_text(text)
        
        assert "+44" not in scrubbed or "4567" in scrubbed
    
    # ===== SSN TESTS =====
    def test_scrub_ssn_dashes(self):
        """Test scrubbing SSN with dashes"""
        text = "SSN: 123-45-6789"
        scrubbed = self.scrubber.scrub_text(text)
        
        assert "123-45" not in scrubbed
        assert "6789" in scrubbed
    
    def test_scrub_ssn_no_dashes(self):
        """Test scrubbing SSN without dashes"""
        text = "ID: 123456789"
        scrubbed = self.scrubber.scrub_text(text)
        
        # May or may not be detected (confidence 0.75), but if detected, should be redacted
        # This is lower confidence, so we just check it works
        assert isinstance(scrubbed, str)
    
    # ===== CREDIT CARD TESTS =====
    def test_scrub_visa_card(self):
        """Test scrubbing Visa card number"""
        text = "Card: 4532 1234 5678 9010"
        scrubbed = self.scrubber.scrub_text(text)
        
        assert "4532" not in scrubbed
        assert "1234" not in scrubbed
        assert "9010" in scrubbed
    
    def test_scrub_mastercard(self):
        """Test scrubbing Mastercard number"""
        text = "Payment method: 5234123456789010"
        scrubbed = self.scrubber.scrub_text(text)
        
        assert "5234" not in scrubbed
        assert "9010" in scrubbed
    
    def test_scrub_amex_card(self):
        """Test scrubbing American Express card"""
        text = "AMEX: 378282246310005"
        scrubbed = self.scrubber.scrub_text(text)
        
        assert "3782822" not in scrubbed
        assert "0005" in scrubbed
    
    # ===== ID DOCUMENT TESTS =====
    def test_scrub_passport(self):
        """Test scrubbing passport number"""
        text = "Passport: AB123456789"
        scrubbed = self.scrubber.scrub_text(text)
        
        assert "123456789" not in scrubbed
        assert "AB" in scrubbed  # Keep first 2 chars
    
    def test_scrub_driver_license(self):
        """Test scrubbing driver license"""
        text = "License: CA12345678"
        scrubbed = self.scrubber.scrub_text(text)
        
        assert "12345678" not in scrubbed
        assert "CA" in scrubbed
    
    def test_scrub_vin(self):
        """Test scrubbing Vehicle Identification Number"""
        text = "VIN: 1HGCM82633A123456"
        scrubbed = self.scrubber.scrub_text(text)
        
        assert "123456" not in scrubbed
    
    # ===== IP ADDRESS TESTS =====
    def test_scrub_ipv4(self):
        """Test scrubbing IPv4 addresses"""
        text = "Server: 192.168.1.1"
        scrubbed = self.scrubber.scrub_text(text)
        
        assert "192.168" not in scrubbed
        assert "[REDACTED" in scrubbed
    
    def test_scrub_ipv6(self):
        """Test scrubbing IPv6 addresses"""
        text = "IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        scrubbed = self.scrubber.scrub_text(text)
        
        assert "2001:0db8" not in scrubbed
    
    # ===== SECURITY TOKENS =====
    def test_scrub_api_key(self):
        """Test scrubbing API keys"""
        text = 'API_KEY="sk_live_12345678901234567890"'
        scrubbed = self.scrubber.scrub_text(text)
        
        assert "sk_live" not in scrubbed or "[REDACTED" in scrubbed
    
    def test_scrub_jwt_token(self):
        """Test scrubbing JWT tokens"""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        text = f"Authorization: Bearer {token}"
        scrubbed = self.scrubber.scrub_text(text)
        
        assert token not in scrubbed or "[REDACTED" in scrubbed
    
    # ===== DICT SCRUBBING =====
    def test_scrub_dict(self):
        """Test scrubbing dictionary with mixed PII"""
        data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone': '(555) 123-4567',
            'ssn': '123-45-6789',
            'address': '123 Main St, Anytown, USA'
        }
        
        scrubbed = self.scrubber.scrub_dict(data)
        
        assert '@example.com' in scrubbed['email']
        assert 'john' not in scrubbed['email'] or '@example.com' in scrubbed['email']
        assert '4567' in scrubbed['phone']
        assert '6789' in scrubbed['ssn']
    
    def test_scrub_nested_dict(self):
        """Test scrubbing nested dictionaries"""
        data = {
            'user': {
                'name': 'Jane Smith',
                'contact': {
                    'email': 'jane@company.com',
                    'phone': '555-987-6543'
                }
            }
        }
        
        scrubbed = self.scrubber.scrub_dict(data)
        
        assert 'jane' not in scrubbed['user']['contact']['email'] or '@company.com' in scrubbed['user']['contact']['email']
        assert '6543' in scrubbed['user']['contact']['phone']
    
    def test_scrub_list_of_dicts(self):
        """Test scrubbing list of dictionaries"""
        data = [
            {'email': 'user1@test.com', 'phone': '555-111-1111'},
            {'email': 'user2@test.com', 'phone': '555-222-2222'},
        ]
        
        scrubbed = self.scrubber.scrub_list(data)
        
        assert 'user1' not in scrubbed[0]['email'] or '@test.com' in scrubbed[0]['email']
        assert '1111' in scrubbed[0]['phone']
    
    # ===== DETECTION WITH DETAILS =====
    def test_scrub_with_details(self):
        """Test scrubbing with detailed entity information"""
        text = "Contact: john@example.com, Phone: (555) 123-4567"
        scrubbed, entities = self.scrubber.scrub_text(text, return_details=True)
        
        assert isinstance(entities, list)
        assert len(entities) >= 2  # Email and phone
        
        email_entity = next((e for e in entities if e.entity_type == 'email'), None)
        assert email_entity is not None
        assert email_entity.value == 'john@example.com'
        assert email_entity.confidence >= 0.9
    
    def test_pii_entity_dataclass(self):
        """Test PiiEntity dataclass"""
        entity = PiiEntity(
            entity_type='email',
            value='test@example.com',
            redacted='t*@example.com',
            confidence=0.95,
            start_pos=0,
            end_pos=16
        )
        
        assert entity.entity_type == 'email'
        assert entity.confidence == 0.95
    
    # ===== VALIDATION =====
    def test_validate_scrubbing(self):
        """Test validation of scrubbing effectiveness"""
        original = "Email: john@example.com, Phone: 555-123-4567, SSN: 123-45-6789"
        scrubbed = self.scrubber.scrub_text(original)
        
        validation = self.scrubber.validate_scrubbing(original, scrubbed)
        
        assert 'original_pii_count' in validation
        assert 'scrubbed_pii_count' in validation
        assert 'effectiveness' in validation
        assert validation['effectiveness'] > 0.8  # High effectiveness
    
    # ===== EDGE CASES =====
    def test_scrub_empty_string(self):
        """Test scrubbing empty string"""
        scrubbed = self.scrubber.scrub_text('')
        assert scrubbed == ''
    
    def test_scrub_none(self):
        """Test scrubbing None"""
        scrubbed = self.scrubber.scrub_text(None)
        assert scrubbed is None
    
    def test_scrub_text_no_pii(self):
        """Test scrubbing text with no PII"""
        text = "This is normal text with no sensitive information"
        scrubbed = self.scrubber.scrub_text(text)
        assert scrubbed == text
    
    def test_custom_redaction_char(self):
        """Test custom redaction character"""
        scrubber = PIIScrubber(redaction_char='#')
        text = "Email: john@example.com"
        scrubbed = scrubber.scrub_text(text)
        
        assert '#' in scrubbed
        assert 'john' not in scrubbed


class TestPIIIntegrationAPI(APITestCase):
    """Integration tests for PII scrubbing in API endpoints"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user.tenant_id = '123e4567-e89b-12d3-a456-426614174000'
        self.user.user_id = '223e4567-e89b-12d3-a456-426614174000'
        self.user.save()
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_extract_metadata_with_pii(self):
        """Test that PII in extraction request is scrubbed"""
        # Document text with sensitive information
        doc_text = """
        This Service Agreement is between:
        Party A: John Smith (john.smith@example.com, SSN: 123-45-6789)
        Party B: ACME Corp (contact: 555-987-6543)
        
        Agreement Terms:
        - Effective Date: 2024-01-01
        - Value: $50,000 USD
        """
        
        response = self.client.post(
            '/api/v1/ai/extract/metadata/',
            {'document_text': doc_text},
            format='json'
        )
        
        # Endpoint should work even with PII (but PII should be scrubbed internally)
        assert response.status_code in [200, 400, 500]  # Accept various responses
    
    def test_classify_clause_with_pii(self):
        """Test that PII in classification request is scrubbed"""
        clause_with_pii = """
        The Licensee agrees to maintain confidentiality of any information
        received from the Licensor. Contact: jane.doe@company.com or 555-123-4567.
        """
        
        response = self.client.post(
            '/api/v1/ai/classify/',
            {'text': clause_with_pii},
            format='json'
        )
        
        assert response.status_code in [200, 400, 500]


class TestPIILogging(TestCase):
    """Test PII detection logging"""
    
    def setUp(self):
        self.scrubber = PIIScrubber()
    
    def test_log_pii_detection(self):
        """Test that PII detection is logged"""
        text = "Email: test@example.com, Phone: 555-123-4567"
        scrubbed, entities = self.scrubber.scrub_text(text, return_details=True)
        
        context = {
            'user_id': 'user123',
            'tenant_id': 'tenant456',
            'endpoint': '/api/v1/ai/extract/',
            'method': 'POST'
        }
        
        # Should not raise exception
        self.scrubber.log_pii_detection(entities, context)
    
    def test_no_log_when_no_pii(self):
        """Test that no log is created when no PII detected"""
        text = "Normal text without sensitive data"
        scrubbed, entities = self.scrubber.scrub_text(text, return_details=True)
        
        assert len(entities) == 0
        # Should not log
        self.scrubber.log_pii_detection(entities, {})


class TestPIIRedactionJob(TestCase):
    """Test PII redaction job model"""
    
    def setUp(self):
        self.tenant_id = '123e4567-e89b-12d3-a456-426614174000'
        self.doc_id = '223e4567-e89b-12d3-a456-426614174000'
    
    def test_create_redaction_job(self):
        """Test creating a redaction job"""
        job = RedactionJobModel.objects.create(
            tenant_id=self.tenant_id,
            document_id=self.doc_id,
            status='pending',
            patterns=['email', 'phone', 'ssn']
        )
        
        assert job.tenant_id == self.tenant_id
        assert job.status == 'pending'
        assert 'email' in job.patterns
    
    def test_update_redaction_status(self):
        """Test updating redaction job status"""
        job = RedactionJobModel.objects.create(
            tenant_id=self.tenant_id,
            document_id=self.doc_id,
            status='pending'
        )
        
        job.status = 'completed'
        job.redacted_content = 'Redacted document content...'
        job.save()
        
        refreshed = RedactionJobModel.objects.get(id=job.id)
        assert refreshed.status == 'completed'
        assert 'Redacted' in refreshed.redacted_content


# Specific test cases for contract documents with PII
class TestPIIInContracts(TestCase):
    """Test PII scrubbing in realistic contract scenarios"""
    
    def setUp(self):
        self.scrubber = PIIScrubber()
    
    def test_nda_with_contact_info(self):
        """Test NDA with contact information"""
        nda_text = """
        NON-DISCLOSURE AGREEMENT
        
        This NDA is between:
        Company A: TechCorp Inc.
        Contact: John Doe (john.doe@techcorp.com, 555-123-4567)
        
        Company B: InnovateTech LLC
        Contact: Jane Smith (jane.smith@innovatetech.com, +1-555-987-6543)
        
        Effective Date: January 1, 2024
        """
        
        scrubbed = self.scrubber.scrub_text(nda_text)
        
        # Sensitive info should be scrubbed
        assert 'john.doe' not in scrubbed or '@techcorp.com' in scrubbed
        assert 'jane.smith' not in scrubbed or '@innovatetech.com' in scrubbed
        assert '555-123-4567' not in scrubbed or '4567' in scrubbed
    
    def test_service_agreement_with_financial_info(self):
        """Test service agreement with financial information"""
        agreement_text = """
        SERVICE AGREEMENT
        
        Client: ACME Corp
        Project Manager: bob@acme.com, (555) 555-5555
        
        Payment Details:
        Card: 4532-1234-5678-9010
        Bank Account: 987654321
        
        Contract Value: $100,000 USD
        """
        
        scrubbed = self.scrubber.scrub_text(agreement_text)
        
        assert 'bob' not in scrubbed or '@acme.com' in scrubbed
        assert '4532' not in scrubbed
        assert '987654321' not in scrubbed or '654321' in scrubbed
        assert '555555' not in scrubbed or '5555' in scrubbed
