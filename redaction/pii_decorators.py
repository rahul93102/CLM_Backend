"""
Decorator and utilities for scrubbing PII from API requests/responses
"""

import logging
import json
from functools import wraps
from typing import Callable, Any
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status as http_status

from .pii_service import get_pii_scrubber, PIIScrubber

logger = logging.getLogger(__name__)


def scrub_request_pii(view_func: Callable) -> Callable:
    """
    Decorator to scrub PII from request data before processing
    
    Usage:
        @scrub_request_pii
        def extract_metadata(self, request):
            # request.data is already scrubbed
            ...
    """
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        scrubber = get_pii_scrubber()
        
        # Get original request data
        original_data = request.data.dict() if hasattr(request.data, 'dict') else dict(request.data)
        
        # Scrub PII from request
        scrubbed_data, pii_entities = scrubber.scrub_dict(original_data, return_details=True)
        
        # Log if PII was detected
        if pii_entities:
            context = {
                'user_id': str(request.user.user_id) if hasattr(request.user, 'user_id') else 'unknown',
                'tenant_id': str(request.user.tenant_id) if hasattr(request.user, 'tenant_id') else 'unknown',
                'endpoint': request.path,
                'method': request.method,
                'pii_count': sum(len(entities) for entities in pii_entities.values()),
            }
            scrubber.log_pii_detection(
                [e for entities in pii_entities.values() for e in entities],
                context
            )
        
        # Update request data with scrubbed version
        request._full_data = scrubbed_data
        
        # Call original view with scrubbed data
        return view_func(self, request, *args, **kwargs)
    
    return wrapper


def scrub_response_pii(view_func: Callable) -> Callable:
    """
    Decorator to scrub PII from response data
    
    Usage:
        @scrub_response_pii
        def get_document(self, request, pk):
            # response data is automatically scrubbed
            return Response({...})
    """
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        response = view_func(self, request, *args, **kwargs)
        scrubber = get_pii_scrubber()
        
        # Scrub response if it's JSON
        if isinstance(response, Response) and response.data:
            try:
                if isinstance(response.data, dict):
                    scrubbed_data, pii_entities = scrubber.scrub_dict(response.data, return_details=True)
                    response.data = scrubbed_data
                    
                    if pii_entities:
                        logger.warning(
                            f"PII detected in response from {request.path}: "
                            f"{sum(len(e) for e in pii_entities.values())} entities"
                        )
                elif isinstance(response.data, list):
                    scrubbed_data, pii_entities = scrubber.scrub_list(response.data, return_details=True)
                    response.data = scrubbed_data
                    
                    if pii_entities:
                        logger.warning(
                            f"PII detected in list response from {request.path}: "
                            f"{sum(len(e) for e in pii_entities.values())} entities"
                        )
            except Exception as e:
                logger.error(f"Error scrubbing response PII: {e}")
        
        return response
    
    return wrapper


def validate_no_pii(view_func: Callable) -> Callable:
    """
    Decorator to validate that no PII exists in request
    Returns 400 if PII is detected and enforcement is enabled
    
    Usage:
        @validate_no_pii
        def secure_endpoint(self, request):
            # Request will be rejected if PII is detected
            ...
    """
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        scrubber = get_pii_scrubber()
        
        # Check for PII in request data
        original_data = request.data.dict() if hasattr(request.data, 'dict') else dict(request.data)
        
        _, pii_entities = scrubber.scrub_dict(original_data, return_details=True)
        
        if pii_entities:
            pii_types = list(set(
                e.entity_type for entities in pii_entities.values() for e in entities
            ))
            
            logger.warning(
                f"PII validation failed for {request.path}: "
                f"Detected {len(pii_types)} types: {', '.join(pii_types)}"
            )
            
            return Response(
                {
                    'error': 'Request contains PII (Personally Identifiable Information)',
                    'detected_types': pii_types,
                    'action': 'Please remove sensitive data before submitting'
                },
                status=http_status.HTTP_400_BAD_REQUEST
            )
        
        return view_func(self, request, *args, **kwargs)
    
    return wrapper


class PIIScrubberMiddleware:
    """
    Middleware to log PII detection across all endpoints
    (non-blocking, for monitoring/auditing)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.scrubber = get_pii_scrubber()
    
    def __call__(self, request):
        # Process request
        try:
            if hasattr(request, 'body') and request.body:
                try:
                    data = json.loads(request.body)
                    _, pii_entities = self.scrubber.scrub_dict(data, return_details=True)
                    
                    if pii_entities:
                        context = {
                            'event': 'PII_DETECTED_IN_REQUEST',
                            'path': request.path,
                            'method': request.method,
                            'pii_types': list(set(
                                e.entity_type for entities in pii_entities.values() for e in entities
                            )),
                        }
                        logger.warning(f"PII detected in request: {context}")
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            logger.debug(f"Error processing PII middleware: {e}")
        
        # Get response
        response = self.get_response(request)
        
        return response
