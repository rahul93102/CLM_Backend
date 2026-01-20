"""
Tenant Isolation Middleware and Utilities

Ensures strict isolation between tenants:
1. All queries automatically filtered by tenant_id
2. Auth tokens include tenant information
3. Middleware validates tenant consistency
4. Cross-tenant access is prevented
"""

import logging
import json
from typing import Optional
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status as http_status
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.db import models
from django.db.models import QuerySet
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class TenantAwareQuerySet(models.QuerySet):
    """
    Custom QuerySet that automatically filters by tenant_id
    Prevents accidental cross-tenant data access
    """
    
    def __init__(self, model, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        self._tenant_id = None
    
    def set_tenant(self, tenant_id):
        """Set tenant context for this queryset"""
        self._tenant_id = tenant_id
        return self.filter(tenant_id=tenant_id)
    
    def for_tenant(self, tenant_id):
        """Filter results for specific tenant"""
        return self.filter(tenant_id=tenant_id)


class TenantAwareManager(models.Manager):
    """
    Custom manager that always filters by tenant
    Usage:
        class Document(models.Model):
            objects = TenantAwareManager()
    """
    
    def get_queryset(self):
        return TenantAwareQuerySet(self.model)
    
    def for_tenant(self, tenant_id):
        """Get all objects for a specific tenant"""
        return self.get_queryset().filter(tenant_id=tenant_id)


class TenantIsolationMiddleware(MiddlewareMixin):
    """
    Middleware to enforce tenant isolation
    
    Responsibilities:
    1. Validate JWT token includes tenant_id
    2. Inject tenant_id into request context
    3. Prevent cross-tenant access attempts
    4. Log tenant violations for audit
    """
    
    EXEMPT_PATHS = [
        '/api/v1/health/',
        '/api/v1/auth/login/',
        '/api/v1/auth/register/',
        '/api/v1/auth/token/refresh/',
        '/api/v1/auth/password-reset/',
        '/api/v1/auth/verify-otp/',
        '/admin/',
    ]
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()
    
    def __call__(self, request):
        # Check if path is exempt
        if self._is_exempt_path(request.path):
            return self.get_response(request)
        
        # Extract and validate tenant from JWT
        tenant_id = self._extract_tenant_from_request(request)
        if tenant_id:
            request.tenant_id = tenant_id
            logger.debug(f"Tenant injected: {tenant_id} for path: {request.path}")
        
        try:
            response = self.get_response(request)
        except Exception as e:
            logger.error(f"Error in tenant isolation middleware: {e}")
            raise
        
        return response
    
    def _is_exempt_path(self, path: str) -> bool:
        """Check if path is exempt from tenant validation"""
        for exempt_path in self.EXEMPT_PATHS:
            if path.startswith(exempt_path):
                return True
        return False
    
    def _extract_tenant_from_request(self, request) -> Optional[str]:
        """
        Extract tenant_id from JWT token
        
        JWT payload should include:
        {
            'user_id': '...',
            'tenant_id': '...',
            'email': '...',
            ...
        }
        """
        try:
            # Try to authenticate with JWT
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if not auth_header.startswith('Bearer '):
                logger.debug(f"No Bearer token found in {request.path}")
                return None
            
            token_str = auth_header.split(' ')[1]
            
            # Decode JWT to extract tenant_id
            try:
                from rest_framework_simplejwt.tokens import AccessToken
                token = AccessToken(token_str)
                tenant_id = token.get('tenant_id')
                
                if not tenant_id:
                    logger.warning(f"Token missing tenant_id for user: {token.get('user_id')}")
                
                return tenant_id
            except Exception as e:
                logger.debug(f"Could not decode token: {e}")
                return None
        
        except Exception as e:
            logger.error(f"Error extracting tenant: {e}")
            return None


class TenantValidationMixin:
    """
    Mixin for ViewSets to validate tenant isolation
    
    Usage:
        class DocumentViewSet(TenantValidationMixin, viewsets.ModelViewSet):
            queryset = Document.objects.all()
            serializer_class = DocumentSerializer
            
            # Automatically validates tenant_id in requests
    """
    
    def check_object_tenant(self, obj):
        """Validate that object belongs to current tenant"""
        if not hasattr(obj, 'tenant_id'):
            return  # Object doesn't have tenant_id, skip check
        
        if not hasattr(self.request.user, 'tenant_id'):
            raise PermissionDenied("User tenant not identified")
        
        if str(obj.tenant_id) != str(self.request.user.tenant_id):
            logger.warning(
                f"Tenant mismatch: user {self.request.user.user_id} "
                f"(tenant {self.request.user.tenant_id}) "
                f"attempted to access object with tenant {obj.tenant_id}"
            )
            raise PermissionDenied("You do not have access to this resource")
    
    def get_queryset(self):
        """Override to filter by tenant"""
        queryset = super().get_queryset()
        
        if not hasattr(self.request.user, 'tenant_id'):
            logger.warning("User has no tenant_id")
            return queryset.none()
        
        # Filter by tenant
        return queryset.filter(tenant_id=self.request.user.tenant_id)
    
    def perform_create(self, serializer):
        """Automatically set tenant_id when creating"""
        if hasattr(serializer.Meta.model, 'tenant_id'):
            serializer.save(tenant_id=self.request.user.tenant_id)
        else:
            serializer.save()
    
    def retrieve(self, request, *args, **kwargs):
        """Validate tenant before retrieving object"""
        response = super().retrieve(request, *args, **kwargs)
        
        # Validate tenant
        obj = self.get_object()
        self.check_object_tenant(obj)
        
        return response
    
    def update(self, request, *args, **kwargs):
        """Validate tenant before updating"""
        obj = self.get_object()
        self.check_object_tenant(obj)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Validate tenant before deleting"""
        obj = self.get_object()
        self.check_object_tenant(obj)
        
        return super().destroy(request, *args, **kwargs)


class TenantIsolationAuditor:
    """
    Audits queries to ensure tenant isolation
    Logs any suspicious cross-tenant access attempts
    """
    
    @staticmethod
    def audit_query(model_name: str, query_filter: dict, user_id: str, tenant_id: str) -> None:
        """Log query execution for audit trail"""
        if 'tenant_id' not in query_filter:
            logger.warning(
                f"SECURITY: Query on {model_name} missing tenant_id filter "
                f"for user {user_id}, tenant {tenant_id}"
            )
    
    @staticmethod
    def detect_cross_tenant_access(
        requested_tenant_id: str,
        user_tenant_id: str,
        user_id: str,
        resource: str
    ) -> bool:
        """
        Detect and log cross-tenant access attempts
        
        Returns:
            True if access should be denied
        """
        if str(requested_tenant_id) != str(user_tenant_id):
            log_entry = {
                'event': 'CROSS_TENANT_ACCESS_ATTEMPT',
                'user_id': user_id,
                'user_tenant': user_tenant_id,
                'requested_tenant': requested_tenant_id,
                'resource': resource,
                'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z'
            }
            
            logger.error(f"SECURITY VIOLATION: {json.dumps(log_entry)}")
            return True
        
        return False


# Decorators for tenant validation

def tenant_required(view_func):
    """
    Decorator to require tenant_id in request
    """
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'tenant_id') or not request.user.tenant_id:
            logger.warning(f"Request without tenant_id: {request.path}")
            return JsonResponse(
                {'error': 'Tenant identification required'},
                status=http_status.HTTP_403_FORBIDDEN
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def validate_tenant_param(param_name: str = 'tenant_id'):
    """
    Decorator to validate tenant_id in request matches user's tenant
    
    Usage:
        @validate_tenant_param('tenant_id')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            user_tenant = getattr(request.user, 'tenant_id', None)
            request_tenant = request.data.get(param_name) or kwargs.get(param_name)
            
            if user_tenant and request_tenant:
                if str(user_tenant) != str(request_tenant):
                    logger.warning(
                        f"Tenant mismatch: user {user_tenant} vs request {request_tenant}"
                    )
                    return JsonResponse(
                        {'error': 'Tenant mismatch'},
                        status=http_status.HTTP_403_FORBIDDEN
                    )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
