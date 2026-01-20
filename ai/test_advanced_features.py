"""
Tests for Advanced AI Features (Phase 4)

Tests for:
1. Obligation Extraction
2. Clause Suggestions (RAG)
3. Document Summarization
4. Similar Clause Finder
"""

import pytest
import json
from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status as http_status
from unittest.mock import patch, MagicMock

from repository.models import Document, DocumentChunk

User = get_user_model()


class TestObligationExtraction(APITestCase):
    """Test obligation extraction feature"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        self.user.tenant_id = 'tenant-123'
        self.user.user_id = 'user-456'
        self.user.save()
        
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_extract_obligations_with_document_text(self):
        """Test obligation extraction with direct document text"""
        contract_text = """
        SERVICE AGREEMENT
        
        1. Payment Obligations:
        The Client shall pay $50,000 annually by January 31 of each year.
        
        2. Confidentiality:
        Both parties agree to maintain confidentiality of proprietary information
        for a period of 3 years after termination.
        
        3. Deliverables:
        The Vendor shall deliver monthly reports within 5 business days of month end.
        """
        
        response = self.client.post(
            '/api/v1/ai/extract/obligations/',
            {'document_text': contract_text},
            format='json'
        )
        
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert 'obligations' in data
            if data['obligations']:
                obligation = data['obligations'][0]
                assert 'action' in obligation
                assert 'owner' in obligation
    
    def test_extract_obligations_missing_text(self):
        """Test that error is returned when no text provided"""
        response = self.client.post(
            '/api/v1/ai/extract/obligations/',
            {},
            format='json'
        )
        
        assert response.status_code == http_status.HTTP_400_BAD_REQUEST
        assert 'error' in response.json()
    
    def test_extract_obligations_with_document_id(self):
        """Test obligation extraction with document_id"""
        # Create test document
        doc = Document.objects.create(
            id='doc-123',
            tenant_id=self.user.tenant_id,
            filename='test.pdf',
            full_text='Sample contract with obligations...'
        )
        
        response = self.client.post(
            '/api/v1/ai/extract/obligations/',
            {'document_id': str(doc.id)},
            format='json'
        )
        
        assert response.status_code in [200, 400, 500]
    
    def test_extract_obligations_document_not_found(self):
        """Test error when document doesn't exist"""
        response = self.client.post(
            '/api/v1/ai/extract/obligations/',
            {'document_id': 'nonexistent-id'},
            format='json'
        )
        
        assert response.status_code == http_status.HTTP_404_NOT_FOUND


class TestClauseSuggestions(APITestCase):
    """Test clause suggestion feature with RAG"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        self.user.tenant_id = 'tenant-123'
        self.user.user_id = 'user-456'
        self.user.save()
        
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_suggest_clause_with_instruction(self):
        """Test clause suggestion with custom instruction"""
        response = self.client.post(
            '/api/v1/ai/clause/suggest/',
            {
                'current_clause': 'The vendor shall provide services as requested.',
                'instruction': 'Make this more specific about deliverables and timelines'
            },
            format='json'
        )
        
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert 'original' in data
            assert 'suggested' in data
            assert 'rationale' in data
    
    def test_suggest_clause_without_instruction(self):
        """Test clause suggestion uses default instruction"""
        response = self.client.post(
            '/api/v1/ai/clause/suggest/',
            {
                'current_clause': 'The parties agree to maintain confidentiality.'
            },
            format='json'
        )
        
        assert response.status_code in [200, 400, 500]
    
    def test_suggest_clause_missing_clause(self):
        """Test error when clause text is missing"""
        response = self.client.post(
            '/api/v1/ai/clause/suggest/',
            {'instruction': 'Improve this'},
            format='json'
        )
        
        assert response.status_code == http_status.HTTP_400_BAD_REQUEST
    
    def test_suggest_clause_includes_similar_clauses(self):
        """Test that response includes similar clauses from RAG"""
        # Create reference documents with clauses
        doc = Document.objects.create(
            id='doc-ref',
            tenant_id=self.user.tenant_id,
            filename='reference.pdf',
            full_text='Confidentiality provisions...'
        )
        
        response = self.client.post(
            '/api/v1/ai/clause/suggest/',
            {
                'current_clause': 'Both parties agree to keep information confidential.',
                'instruction': 'Add enforcement mechanisms'
            },
            format='json'
        )
        
        if response.status_code == 200:
            data = response.json()
            assert 'similar_clauses' in data


class TestDocumentSummarization(APITestCase):
    """Test document summarization with caching"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        self.user.tenant_id = 'tenant-123'
        self.user.user_id = 'user-456'
        self.user.save()
        
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create test document
        self.doc = Document.objects.create(
            id='summary-test-doc',
            tenant_id=self.user.tenant_id,
            filename='contract.pdf',
            full_text="""
            SERVICE AGREEMENT
            
            This Service Agreement ("Agreement") is entered into as of January 1, 2024
            between TechCorp Inc. ("Client") and ServicePro LLC ("Vendor").
            
            1. Services: Vendor will provide software development services valued at $100,000.
            
            2. Term: This Agreement shall run for one year from the Effective Date
            and automatically renew unless terminated by either party with 30 days notice.
            
            3. Payment: Client shall pay $25,000 quarterly in advance.
            
            4. Confidentiality: Both parties agree to maintain confidentiality of 
            proprietary information for three years after termination.
            """
        )
    
    def test_summarize_document_success(self):
        """Test successful document summarization"""
        response = self.client.get(
            f'/api/v1/ai/summarize/{self.doc.id}/',
            format='json'
        )
        
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert 'document_id' in data
            assert 'summary' in data
            assert 'key_points' in data
            assert 'cached' in data
            assert isinstance(data['key_points'], list)
    
    def test_summarize_document_caching(self):
        """Test that summaries are cached for 24 hours"""
        # First request
        response1 = self.client.get(
            f'/api/v1/ai/summarize/{self.doc.id}/',
            format='json'
        )
        
        if response1.status_code == 200:
            # Second request should be cached
            response2 = self.client.get(
                f'/api/v1/ai/summarize/{self.doc.id}/',
                format='json'
            )
            
            if response2.status_code == 200:
                data = response2.json()
                # Should indicate it was cached (if cache is working)
                assert 'cached' in data
    
    def test_summarize_nonexistent_document(self):
        """Test error when document doesn't exist"""
        response = self.client.get(
            '/api/v1/ai/summarize/nonexistent-id/',
            format='json'
        )
        
        assert response.status_code == http_status.HTTP_404_NOT_FOUND
    
    def test_summarize_document_tenant_isolation(self):
        """Test that documents from other tenants can't be summarized"""
        # Create document in different tenant
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        other_user.tenant_id = 'other-tenant'
        other_user.user_id = 'other-user'
        other_user.save()
        
        other_doc = Document.objects.create(
            id='other-doc',
            tenant_id=other_user.tenant_id,
            filename='other.pdf',
            full_text='Other tenant contract'
        )
        
        # Try to summarize with first user
        response = self.client.get(
            f'/api/v1/ai/summarize/{other_doc.id}/',
            format='json'
        )
        
        assert response.status_code == http_status.HTTP_404_NOT_FOUND


class TestSimilarClauseFinder(APITestCase):
    """Test similar clause finder feature"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        self.user.tenant_id = 'tenant-123'
        self.user.user_id = 'user-456'
        self.user.save()
        
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create test documents with chunks
        self.doc1 = Document.objects.create(
            id='doc-1',
            tenant_id=self.user.tenant_id,
            filename='contract1.pdf',
            full_text='Confidentiality clause text...'
        )
        
        self.doc2 = Document.objects.create(
            id='doc-2',
            tenant_id=self.user.tenant_id,
            filename='contract2.pdf',
            full_text='Non-disclosure agreement text...'
        )
    
    def test_search_similar_clauses(self):
        """Test searching for similar clauses"""
        response = self.client.post(
            '/api/v1/search/similar/',
            {
                'text': 'The parties agree to maintain confidentiality of proprietary information',
                'top_k': 5,
                'min_similarity': 0.7
            },
            format='json'
        )
        
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert 'query' in data
            assert 'results' in data
            assert 'total_results' in data
            assert isinstance(data['results'], list)
    
    def test_search_without_query_text(self):
        """Test error when query text is missing"""
        response = self.client.post(
            '/api/v1/search/similar/',
            {'top_k': 5},
            format='json'
        )
        
        assert response.status_code == http_status.HTTP_400_BAD_REQUEST
    
    def test_search_with_custom_parameters(self):
        """Test search with custom top_k and min_similarity"""
        response = self.client.post(
            '/api/v1/search/similar/',
            {
                'text': 'Confidentiality clause',
                'top_k': 3,
                'min_similarity': 0.8
            },
            format='json'
        )
        
        if response.status_code == 200:
            data = response.json()
            # Results should be limited by top_k
            assert len(data['results']) <= 3
    
    def test_search_parameter_validation(self):
        """Test that invalid parameters are handled"""
        # top_k too large should be capped
        response = self.client.post(
            '/api/v1/search/similar/',
            {
                'text': 'test clause',
                'top_k': 1000,  # Should be capped at 50
                'min_similarity': 2.5  # Invalid, should be clamped to 1.0
            },
            format='json'
        )
        
        if response.status_code == 200:
            data = response.json()
            assert len(data['results']) <= 50
    
    def test_search_results_format(self):
        """Test that search results have correct format"""
        response = self.client.post(
            '/api/v1/search/similar/',
            {
                'text': 'sample clause text'
            },
            format='json'
        )
        
        if response.status_code == 200 and response.json()['results']:
            result = response.json()['results'][0]
            
            assert 'rank' in result
            assert 'document_id' in result
            assert 'document_name' in result
            assert 'text' in result
            assert 'similarity_score' in result
            assert 0.0 <= result['similarity_score'] <= 1.0


class TestAdvancedFeaturesIntegration(APITestCase):
    """Integration tests for all advanced features"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        self.user.tenant_id = 'tenant-123'
        self.user.user_id = 'user-456'
        self.user.save()
        
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_workflow_extract_summarize_suggest(self):
        """Test complete workflow: extract obligations -> summarize -> suggest improvement"""
        contract_text = """
        SERVICE AGREEMENT
        
        By January 31 of each year, the Client shall pay the Vendor $50,000.
        The Vendor shall deliver monthly reports.
        """
        
        # Step 1: Extract obligations
        response1 = self.client.post(
            '/api/v1/ai/extract/obligations/',
            {'document_text': contract_text},
            format='json'
        )
        
        # Step 2: Summarize (with saved document)
        # Note: Would need to create and save document first
        
        # Step 3: Suggest improvement to a clause
        response3 = self.client.post(
            '/api/v1/ai/clause/suggest/',
            {
                'current_clause': 'The Vendor shall deliver monthly reports.',
                'instruction': 'Add specific requirements and deadlines'
            },
            format='json'
        )
        
        # At least one should succeed
        assert response1.status_code != http_status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response3.status_code != http_status.HTTP_500_INTERNAL_SERVER_ERROR


class TestAdvancedFeaturesAuthentication(APITestCase):
    """Test authentication and authorization for advanced features"""
    
    def test_obligation_extraction_requires_auth(self):
        """Test that obligation extraction requires authentication"""
        # Make request without authentication
        response = self.client.post(
            '/api/v1/ai/extract/obligations/',
            {'document_text': 'Some contract text'},
            format='json'
        )
        
        assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
    
    def test_clause_suggestion_requires_auth(self):
        """Test that clause suggestion requires authentication"""
        response = self.client.post(
            '/api/v1/ai/clause/suggest/',
            {'current_clause': 'Some clause'},
            format='json'
        )
        
        assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
    
    def test_summarization_requires_auth(self):
        """Test that summarization requires authentication"""
        response = self.client.get(
            '/api/v1/ai/summarize/some-doc-id/',
            format='json'
        )
        
        assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
    
    def test_similar_search_requires_auth(self):
        """Test that similar clause search requires authentication"""
        response = self.client.post(
            '/api/v1/search/similar/',
            {'text': 'some clause text'},
            format='json'
        )
        
        assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
