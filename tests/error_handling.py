"""
Phase 5 Error Handling & Rate Limiting

Implements:
- Retry logic for API calls with exponential backoff
- Graceful degradation (search falls back to keyword search)
- Rate limiting to prevent abuse
- Circuit breaker pattern for external APIs
"""

import logging
import time
import hashlib
from typing import Callable, Any, Optional, Tuple
from functools import wraps
from datetime import datetime, timedelta
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.throttling import BaseThrottle
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry logic"""
    
    def __init__(self,
                 max_retries: int = 3,
                 initial_delay: float = 0.5,
                 max_delay: float = 30.0,
                 exponential_base: float = 2.0,
                 jitter: bool = True):
        """
        Args:
            max_retries: Maximum number of retries
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay between retries
            exponential_base: Base for exponential backoff
            jitter: Add randomness to delays
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


def retry_on_exception(config: RetryConfig = None,
                      exceptions: Tuple = (Exception,)):
    """
    Decorator to retry function with exponential backoff
    
    Usage:
        @retry_on_exception(RetryConfig(max_retries=3))
        def call_gemini_api():
            ...
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_retries:
                        # Final attempt failed
                        logger.error(
                            f"{func.__name__} failed after {config.max_retries + 1} attempts: {e}"
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        config.initial_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )
                    
                    # Add jitter
                    if config.jitter:
                        import random
                        delay *= random.uniform(0.5, 1.5)
                    
                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1}/{config.max_retries + 1} failed, "
                        f"retrying in {delay:.2f}s: {e}"
                    )
                    
                    time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern for external API calls
    
    States: CLOSED (working) -> OPEN (failing) -> HALF_OPEN (testing)
    """
    
    CLOSED = 'closed'
    OPEN = 'open'
    HALF_OPEN = 'half_open'
    
    def __init__(self,
                 service_name: str,
                 failure_threshold: int = 5,
                 timeout: int = 60,
                 success_threshold: int = 2):
        """
        Args:
            service_name: Name of the service (for cache key)
            failure_threshold: Failures before opening
            timeout: Seconds before attempting half-open
            success_threshold: Successes in half-open to close
        """
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        self.cache_key = f"circuit_breaker:{service_name}"
    
    def get_state(self) -> str:
        """Get current circuit breaker state"""
        state_data = cache.get(self.cache_key)
        
        if state_data is None:
            return self.CLOSED
        
        # Check if timeout has expired
        if state_data['state'] == self.OPEN:
            if time.time() - state_data['opened_at'] > self.timeout:
                return self.HALF_OPEN
        
        return state_data['state']
    
    def record_success(self):
        """Record successful call"""
        state = self.get_state()
        
        if state == self.HALF_OPEN:
            state_data = cache.get(self.cache_key)
            state_data['successes'] += 1
            
            if state_data['successes'] >= self.success_threshold:
                # Close the circuit
                cache.delete(self.cache_key)
                logger.info(f"Circuit breaker for {self.service_name} CLOSED")
            else:
                cache.set(self.cache_key, state_data, self.timeout)
        
        elif state == self.CLOSED:
            # Reset failure count on success
            state_data = cache.get(self.cache_key, {
                'state': self.CLOSED,
                'failures': 0,
                'successes': 0
            })
            state_data['failures'] = 0
            cache.set(self.cache_key, state_data, self.timeout * 2)
    
    def record_failure(self):
        """Record failed call"""
        state_data = cache.get(self.cache_key, {
            'state': self.CLOSED,
            'failures': 0,
            'successes': 0,
            'opened_at': None
        })
        
        state_data['failures'] += 1
        
        if state_data['failures'] >= self.failure_threshold:
            # Open the circuit
            state_data['state'] = self.OPEN
            state_data['opened_at'] = time.time()
            state_data['successes'] = 0
            
            logger.error(
                f"Circuit breaker for {self.service_name} OPEN "
                f"after {state_data['failures']} failures"
            )
        
        cache.set(self.cache_key, state_data, self.timeout)
    
    def is_available(self) -> bool:
        """Check if service is available"""
        state = self.get_state()
        return state in [self.CLOSED, self.HALF_OPEN]
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Usage:
            breaker = CircuitBreaker('gemini_api')
            result = breaker.call(gemini_function, arg1, arg2)
        """
        if not self.is_available():
            raise Exception(f"Circuit breaker OPEN for {self.service_name}")
        
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise


# Global circuit breakers for external services
circuit_breakers = {
    'gemini': CircuitBreaker('gemini_api', failure_threshold=5),
    'voyage_ai': CircuitBreaker('voyage_ai', failure_threshold=5),
    'postgres': CircuitBreaker('postgres', failure_threshold=3),
}


class GracefulDegradation:
    """
    Provides fallback implementations when primary service fails
    """
    
    @staticmethod
    def fallback_semantic_search(query: str, documents: list) -> list:
        """
        Fallback to keyword search when semantic search fails
        
        Args:
            query: Search query
            documents: List of documents to search
        
        Returns:
            Documents matching keywords
        """
        logger.warning(f"Falling back to keyword search for query: {query}")
        
        query_keywords = query.lower().split()
        results = []
        
        for doc in documents:
            content = doc.get('text', '').lower()
            matches = sum(1 for keyword in query_keywords if keyword in content)
            
            if matches > 0:
                results.append({
                    **doc,
                    'keyword_matches': matches,
                    'degraded': True  # Mark as degraded result
                })
        
        # Sort by match count
        results.sort(key=lambda x: x['keyword_matches'], reverse=True)
        return results[:10]  # Return top 10
    
    @staticmethod
    def fallback_classification(text: str) -> dict:
        """
        Fallback classification when AI model fails
        
        Uses simple keyword-based classification
        """
        logger.warning(f"Falling back to keyword classification")
        
        categories = {
            'Confidentiality': ['confidential', 'secret', 'proprietary', 'nda'],
            'Payment': ['payment', 'price', 'cost', 'fee', 'compensation'],
            'Termination': ['terminate', 'termination', 'expiration', 'end', 'cancel'],
            'IP Rights': ['intellectual property', 'copyright', 'patent', 'trademark'],
            'Liability': ['liable', 'liability', 'damage', 'indemnif'],
        }
        
        text_lower = text.lower()
        
        best_category = 'Other'
        best_score = 0
        
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > best_score:
                best_category = category
                best_score = score
        
        confidence = min(0.6 + (best_score * 0.1), 0.95)  # Cap at 0.95
        
        return {
            'label': best_category,
            'confidence': confidence,
            'degraded': True,
            'method': 'keyword_fallback'
        }
    
    @staticmethod
    def fallback_summarization(text: str) -> dict:
        """
        Fallback summarization when AI fails
        
        Returns first and last paragraph
        """
        logger.warning(f"Falling back to simple summarization")
        
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Take first 2 and last paragraph
        summary_parts = []
        if paragraphs:
            summary_parts.append(paragraphs[0])
            if len(paragraphs) > 1:
                summary_parts.append(paragraphs[-1])
        
        summary = ' '.join(summary_parts)
        
        return {
            'summary': summary[:500],  # Max 500 chars
            'key_points': [p[:100] for p in paragraphs[:3]],
            'degraded': True,
            'method': 'simple_extraction'
        }


class RateLimiter(BaseThrottle):
    """
    Rate limiter to prevent API abuse
    
    Limits per user and per IP address
    """
    
    # Different limits for different endpoints
    RATE_LIMITS = {
        'ai_endpoints': {
            'calls': 100,
            'period': 3600  # Per hour
        },
        'search_endpoints': {
            'calls': 200,
            'period': 3600
        },
        'upload_endpoints': {
            'calls': 10,
            'period': 3600
        },
        'default': {
            'calls': 500,
            'period': 3600
        }
    }
    
    def get_cache_key(self, request) -> str:
        """Generate cache key for rate limiting"""
        # Use user ID if authenticated, IP if not
        identifier = None
        
        if hasattr(request.user, 'user_id') and request.user.user_id:
            identifier = f"user:{request.user.user_id}"
        else:
            ip = self._get_client_ip(request)
            identifier = f"ip:{ip}"
        
        return f"rate_limit:{identifier}:{request.path}"
    
    def get_rate_limit(self, request) -> Tuple[int, int]:
        """Get rate limit for this request"""
        path = request.path
        
        if '/ai/' in path:
            limit_config = self.RATE_LIMITS['ai_endpoints']
        elif '/search/' in path:
            limit_config = self.RATE_LIMITS['search_endpoints']
        elif 'upload' in path:
            limit_config = self.RATE_LIMITS['upload_endpoints']
        else:
            limit_config = self.RATE_LIMITS['default']
        
        return limit_config['calls'], limit_config['period']
    
    def throttle_success(self, request) -> bool:
        """Check if request is within rate limits"""
        cache_key = self.get_cache_key(request)
        calls_limit, period = self.get_rate_limit(request)
        
        current_calls = cache.get(cache_key, 0)
        
        if current_calls >= calls_limit:
            return False
        
        cache.set(cache_key, current_calls + 1, period)
        return True
    
    def throttle_failure(self, request):
        """Return throttle response"""
        return False
    
    def allow_request(self, request):
        """Check if request should be allowed"""
        return self.throttle_success(request)
    
    def throttle_scope(self):
        """Scope name for throttle messages"""
        return 'api'
    
    def _get_client_ip(self, request) -> str:
        """Extract client IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR', 'unknown')


class APIErrorHandler:
    """
    Centralized error handling for APIs
    Provides consistent error responses and logging
    """
    
    @staticmethod
    def handle_error(error: Exception,
                    endpoint: str,
                    user_id: str = None,
                    tenant_id: str = None) -> Response:
        """
        Handle API error and return appropriate response
        
        Args:
            error: Exception that occurred
            endpoint: API endpoint
            user_id: User making request
            tenant_id: Tenant context
        
        Returns:
            DRF Response with error details
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        # Log the error
        logger.error(
            f"API Error in {endpoint}: {error_type}: {error_message}",
            extra={
                'user_id': user_id,
                'tenant_id': tenant_id,
                'endpoint': endpoint
            },
            exc_info=True
        )
        
        # Map error types to status codes
        error_mapping = {
            'ValueError': status.HTTP_400_BAD_REQUEST,
            'KeyError': status.HTTP_400_BAD_REQUEST,
            'NotFound': status.HTTP_404_NOT_FOUND,
            'PermissionDenied': status.HTTP_403_FORBIDDEN,
            'ValidationError': status.HTTP_400_BAD_REQUEST,
            'TimeoutError': status.HTTP_504_GATEWAY_TIMEOUT,
            'ConnectionError': status.HTTP_503_SERVICE_UNAVAILABLE,
        }
        
        status_code = error_mapping.get(error_type, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(
            {
                'error': 'An error occurred processing your request',
                'error_type': error_type,
                'details': error_message if status.HTTP_400_BAD_REQUEST <= status_code < 500 else None,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            },
            status=status_code
        )


def handle_api_errors(view_func: Callable) -> Callable:
    """
    Decorator to wrap API endpoints with error handling
    
    Usage:
        @handle_api_errors
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Exception as e:
            return APIErrorHandler.handle_error(
                e,
                request.path,
                user_id=getattr(request.user, 'user_id', None),
                tenant_id=getattr(request.user, 'tenant_id', None)
            )
    return wrapper
