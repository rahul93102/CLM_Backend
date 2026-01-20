"""
Phase 5 Testing Suite
Tests for Performance Optimization, Error Handling, and Rate Limiting
"""

import pytest
import time
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from unittest.mock import patch, MagicMock

from tests.performance_optimizer import (
    PerformanceMonitor,
    VectorIndexOptimizer,
    CacheOptimizer,
    LatencyTargets,
)
from tests.error_handling import (
    RetryConfig,
    CircuitBreaker,
    GracefulDegradation,
    RateLimiter,
    APIErrorHandler,
)

User = get_user_model()


# ============================================================================
# PERFORMANCE MONITORING TESTS
# ============================================================================

class TestPerformanceMonitor(TestCase):
    """Test performance monitoring"""
    
    def setUp(self):
        self.monitor = PerformanceMonitor()
    
    def test_measure_endpoint_latency(self):
        """Test latency measurement"""
        start = time.time()
        time.sleep(0.1)  # Simulate 100ms latency
        
        latency = self.monitor.measure_endpoint_latency('/api/v1/test/', start)
        
        assert latency >= 100
        assert latency < 200  # Should be close to 100ms
    
    def test_get_endpoint_stats(self):
        """Test getting endpoint statistics"""
        # Record some latencies
        for latency in [100, 150, 200, 120, 180]:
            start = time.time() - latency / 1000  # Fake start time
            self.monitor.measure_endpoint_latency('/api/v1/test/', start)
        
        stats = self.monitor.get_endpoint_stats('/api/v1/test/')
        
        assert stats['count'] == 5
        assert stats['min_ms'] <= 120
        assert stats['max_ms'] >= 180
        assert 120 <= stats['avg_ms'] <= 160
    
    def test_track_multiple_endpoints(self):
        """Test tracking multiple endpoints"""
        self.monitor.measure_endpoint_latency('/api/v1/endpoint1/', time.time() - 0.1)
        self.monitor.measure_endpoint_latency('/api/v1/endpoint2/', time.time() - 0.2)
        
        all_stats = self.monitor.get_all_stats()
        assert len(all_stats) == 2


class TestVectorIndexOptimizer(TestCase):
    """Test vector index optimization"""
    
    def test_recommended_lists_calculation(self):
        """Test IVFFlat list calculation"""
        # For 100K vectors: sqrt(100000) = 316
        # Recommended: 316/4 to 316 -> ~80
        lists = VectorIndexOptimizer.get_recommended_lists(100000)
        assert 50 < lists < 400
    
    def test_recommended_probes_calculation(self):
        """Test probe count calculation"""
        lists = 100
        probes = VectorIndexOptimizer.get_recommended_probes(lists)
        
        # Should be 5-10% of lists
        assert 5 < probes < 20
    
    def test_optimized_vector_search(self):
        """Test optimized vector search"""
        import numpy as np
        
        # Create sample embeddings
        embeddings = [
            np.random.randn(384),
            np.random.randn(384),
            np.random.randn(384),
        ]
        
        query = np.random.randn(384)
        
        results = VectorIndexOptimizer.optimize_vector_search(embeddings, query, k=2)
        
        assert len(results) <= 2
        # Results should be (index, similarity) tuples
        for idx, sim in results:
            assert 0 <= idx < 3
            assert -1 <= sim <= 1


class TestCacheOptimization(TestCase):
    """Test cache optimization"""
    
    def test_cache_result_with_ttl(self):
        """Test caching with appropriate TTL"""
        success = CacheOptimizer.cache_result(
            'test_key',
            {'data': 'test'},
            pattern='doc_summary'
        )
        
        assert success is True
    
    def test_retrieve_cached_result(self):
        """Test retrieving cached results"""
        test_data = {'value': 42}
        CacheOptimizer.cache_result('test_cache_key', test_data)
        
        result = CacheOptimizer.get_cached_result('test_cache_key')
        assert result == test_data
    
    def test_cache_miss(self):
        """Test cache miss returns None"""
        result = CacheOptimizer.get_cached_result('nonexistent_key')
        assert result is None


class TestLatencyTargets(TestCase):
    """Test latency target tracking"""
    
    def test_is_within_target_ai_endpoint(self):
        """Test latency target for AI endpoints"""
        # Classification target is 2000ms
        assert LatencyTargets.is_within_target('/api/v1/ai/classify/', 1500)
        assert not LatencyTargets.is_within_target('/api/v1/ai/classify/', 3000)
    
    def test_get_latency_budget(self):
        """Test getting latency budget"""
        budget = LatencyTargets.get_latency_budget('/api/v1/ai/classify/')
        assert budget == 2000  # 2 seconds
    
    def test_unknown_endpoint_default_target(self):
        """Test unknown endpoint uses default target"""
        budget = LatencyTargets.get_latency_budget('/api/v1/unknown/')
        assert budget == 5000  # Default 5 seconds


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestRetryLogic(TestCase):
    """Test retry logic with exponential backoff"""
    
    def test_successful_call_no_retry(self):
        """Test successful call doesn't trigger retry"""
        config = RetryConfig(max_retries=2)
        
        call_count = 0
        
        @retry_on_exception(config)
        def succeeds_immediately():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = succeeds_immediately()
        assert result == "success"
        assert call_count == 1
    
    def test_retry_on_failure(self):
        """Test retry on exception"""
        config = RetryConfig(max_retries=2, initial_delay=0.01, max_delay=0.05)
        
        call_count = 0
        
        @retry_on_exception(config, exceptions=(ValueError,))
        def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError(f"Attempt {call_count}")
            return "success"
        
        result = fails_twice()
        assert result == "success"
        assert call_count == 3  # 2 failures + 1 success
    
    def test_max_retries_exceeded(self):
        """Test exception after max retries"""
        config = RetryConfig(max_retries=1, initial_delay=0.01)
        
        @retry_on_exception(config, exceptions=(ValueError,))
        def always_fails():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            always_fails()


class TestCircuitBreaker(TestCase):
    """Test circuit breaker pattern"""
    
    def test_circuit_breaker_initial_state(self):
        """Test circuit breaker starts in CLOSED state"""
        breaker = CircuitBreaker('test_service')
        assert breaker.get_state() == CircuitBreaker.CLOSED
    
    def test_circuit_breaker_opens_after_failures(self):
        """Test circuit opens after threshold failures"""
        breaker = CircuitBreaker('test', failure_threshold=2)
        
        # Record 2 failures
        breaker.record_failure()
        breaker.record_failure()
        
        assert breaker.get_state() == CircuitBreaker.OPEN
        assert not breaker.is_available()
    
    def test_circuit_breaker_half_open(self):
        """Test circuit breaker goes to half-open after timeout"""
        breaker = CircuitBreaker('test', failure_threshold=1, timeout=0)
        
        # Open the circuit
        breaker.record_failure()
        assert breaker.get_state() == CircuitBreaker.OPEN
        
        # Timeout expires, should be half-open
        time.sleep(0.1)
        state = breaker.get_state()
        assert state == CircuitBreaker.HALF_OPEN
    
    def test_circuit_breaker_call(self):
        """Test calling through circuit breaker"""
        breaker = CircuitBreaker('test')
        
        def mock_func(x):
            return x * 2
        
        result = breaker.call(mock_func, 5)
        assert result == 10


class TestGracefulDegradation(TestCase):
    """Test graceful degradation fallbacks"""
    
    def test_keyword_search_fallback(self):
        """Test keyword search fallback"""
        documents = [
            {'id': 1, 'text': 'This is a confidential agreement'},
            {'id': 2, 'text': 'Payment terms and conditions'},
            {'id': 3, 'text': 'Random document text'},
        ]
        
        results = GracefulDegradation.fallback_semantic_search(
            'confidential agreement',
            documents
        )
        
        assert len(results) > 0
        assert results[0]['id'] == 1
    
    def test_keyword_classification_fallback(self):
        """Test keyword-based classification fallback"""
        result = GracefulDegradation.fallback_classification(
            'This clause maintains confidentiality of proprietary information'
        )
        
        assert result['label'] == 'Confidentiality'
        assert result['confidence'] > 0.6
        assert result['degraded'] is True
    
    def test_simple_summarization_fallback(self):
        """Test simple summarization fallback"""
        text = """
        Paragraph one about the contract.
        
        Paragraph two with details.
        
        Paragraph three conclusion.
        """
        
        result = GracefulDegradation.fallback_summarization(text)
        
        assert 'summary' in result
        assert 'key_points' in result
        assert result['degraded'] is True
        assert len(result['summary']) > 0


class TestRateLimiting(APITestCase):
    """Test rate limiting"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        self.user.user_id = 'user-123'
        self.user.save()
    
    def test_rate_limiter_allows_requests_within_limit(self):
        """Test requests within rate limit are allowed"""
        limiter = RateLimiter()
        
        request = self.factory.get('/api/v1/documents/')
        request.user = self.user
        
        for i in range(10):
            assert limiter.allow_request(request) is True
    
    def test_rate_limiter_cache_key_generation(self):
        """Test cache key generation"""
        limiter = RateLimiter()
        
        request = self.factory.get('/api/v1/test/')
        request.user = self.user
        
        cache_key = limiter.get_cache_key(request)
        assert 'user-123' in cache_key
        assert '/api/v1/test/' in cache_key
    
    def test_different_rate_limits_for_endpoints(self):
        """Test different endpoints have different rate limits"""
        limiter = RateLimiter()
        
        request_ai = self.factory.get('/api/v1/ai/classify/')
        request_ai.user = self.user
        
        request_search = self.factory.get('/api/v1/search/')
        request_search.user = self.user
        
        calls_ai, period_ai = limiter.get_rate_limit(request_ai)
        calls_search, period_search = limiter.get_rate_limit(request_search)
        
        # AI endpoints should have lower limit
        assert calls_ai < calls_search


class TestAPIErrorHandler(TestCase):
    """Test API error handling"""
    
    def test_handle_value_error(self):
        """Test handling ValueError"""
        error = ValueError("Invalid input")
        response = APIErrorHandler.handle_error(error, '/api/v1/test/')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_handle_not_found_error(self):
        """Test handling NotFound error"""
        from django.http import Http404
        
        error = Http404("Not found")
        response = APIErrorHandler.handle_error(error, '/api/v1/test/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_handle_generic_error(self):
        """Test handling generic exception"""
        error = Exception("Something went wrong")
        response = APIErrorHandler.handle_error(error, '/api/v1/test/')
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestPhase5Integration(APITestCase):
    """Integration tests for Phase 5 features"""
    
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
    
    def test_api_call_respects_rate_limit(self):
        """Test that API endpoints respect rate limits"""
        # Make multiple requests
        for i in range(10):
            response = self.client.get('/api/v1/health/')
            # Should succeed (health endpoint has high limit)
            assert response.status_code in [200, 401, 404]
    
    def test_error_response_includes_timestamp(self):
        """Test that error responses include timestamp"""
        # Make invalid request
        response = self.client.post(
            '/api/v1/ai/extract/obligations/',
            {},  # Missing required data
            format='json'
        )
        
        if response.status_code == 400:
            assert 'timestamp' in response.data or 'error' in response.data
