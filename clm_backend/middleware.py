"""
Middleware for tenant isolation and audit logging
"""
import logging
import json
import hashlib
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone

logger = logging.getLogger(__name__)
audit_logger = logging.getLogger('audit')


class TenantIsolationMiddleware(MiddlewareMixin):
    """
    Middleware to inject tenant_id from JWT token into request
    Ensures all queries are tenant-isolated
    """
    
    def process_request(self, request):
        """
        Extract tenant_id from authenticated user and add to request
        """
        try:
            if hasattr(request, 'user') and request.user.is_authenticated:
                # Add tenant_id to request for use in views/queries
                request.tenant_id = getattr(request.user, 'tenant_id', None)
                
                if not request.tenant_id:
                    logger.warning(f"User {request.user.id} has no tenant_id")
                else:
                    logger.debug(f"Tenant {request.tenant_id} injected for user {request.user.id}")
            
            return None
        except Exception as e:
            logger.error(f"Error in TenantIsolationMiddleware: {str(e)}")
            return None


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all API requests for audit trail
    """
    
    # Endpoints to exclude from logging (noisy/frequent)
    EXCLUDED_PATHS = [
        '/api/health/',
        '/static/',
        '/media/',
    ]
    
    def should_log(self, path):
        """Check if this path should be logged"""
        for excluded in self.EXCLUDED_PATHS:
            if path.startswith(excluded):
                return False
        return True
    
    def get_request_hash(self, request):
        """Create hash of request for integrity checking"""
        try:
            data = {
                'method': request.method,
                'path': request.path,
                'timestamp': timezone.now().isoformat(),
            }
            
            # Add body for POST/PUT requests
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    body = request.body.decode('utf-8') if request.body else ''
                    if len(body) < 1000:  # Only hash if small enough
                        data['body'] = body
                except:
                    pass
            
            json_str = json.dumps(data, sort_keys=True)
            return hashlib.sha256(json_str.encode()).hexdigest()
        except Exception as e:
            logger.warning(f"Could not generate request hash: {e}")
            return None
    
    def process_request(self, request):
        """Store request info for later logging"""
        if self.should_log(request.path):
            # Store info on request object for access in process_response
            request._audit_log_data = {
                'method': request.method,
                'path': request.path,
                'remote_addr': self.get_client_ip(request),
                'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') and request.user.is_authenticated else None,
                'tenant_id': getattr(request.user, 'tenant_id', None) if hasattr(request, 'user') and request.user.is_authenticated else None,
                'request_hash': self.get_request_hash(request),
                'timestamp': timezone.now(),
            }
        
        return None
    
    def process_response(self, request, response):
        """Log the API response"""
        if hasattr(request, '_audit_log_data'):
            try:
                audit_data = request._audit_log_data
                
                # Only log API endpoints
                if audit_data['path'].startswith('/api/'):
                    # Log to audit logger
                    audit_logger.info(
                        f"API_CALL|method={audit_data['method']}|endpoint={audit_data['path']}|"
                        f"status={response.status_code}|user_id={audit_data['user_id']}|"
                        f"tenant_id={audit_data['tenant_id']}|ip={audit_data['remote_addr']}|"
                        f"hash={audit_data['request_hash']}"
                    )
                    
                    # Log errors to warning
                    if response.status_code >= 400:
                        logger.warning(
                            f"API Error: {audit_data['method']} {audit_data['path']} - "
                            f"Status: {response.status_code} - User: {audit_data['user_id']}"
                        )
            except Exception as e:
                logger.error(f"Failed to log API call: {str(e)}")
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PIIProtectionLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log PII redaction operations
    """
    
    def process_request(self, request):
        """Log PII operations"""
        try:
            if request.path.startswith('/api/') and 'redaction' in request.path.lower():
                user_id = getattr(request.user, 'id', None) if hasattr(request, 'user') and request.user.is_authenticated else 'unknown'
                logger.info(
                    f"PII Redaction operation by user {user_id}: "
                    f"{request.method} {request.path}"
                )
        except Exception as e:
            logger.warning(f"Error in PIIProtectionLoggingMiddleware: {e}")
        
        return None
