"""
Comprehensive Audit Logging Middleware for CLM Backend

Logs all API requests with:
- Endpoint, HTTP method, user, timestamp
- Request hash (for deduplication)
- Response status, latency
- Automatically enforces retention policy
"""

import logging
import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest, HttpResponse
from django.db import models
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.conf import settings
import uuid

logger = logging.getLogger(__name__)


# ============================================================================
# AUDIT LOG MODELS
# ============================================================================

class AuditLogModel(models.Model):
    """
    Comprehensive audit log for all API requests
    
    Stores: endpoint, user, tenant, method, status, timestamp, hash, etc.
    """
    
    HTTP_METHODS = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
        ('HEAD', 'HEAD'),
        ('OPTIONS', 'OPTIONS'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant_id = models.UUIDField(null=True, blank=True, db_index=True)
    user_id = models.UUIDField(null=True, blank=True, db_index=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    
    # Request details
    endpoint = models.CharField(max_length=500, db_index=True)
    method = models.CharField(max_length=10, choices=HTTP_METHODS)
    request_hash = models.CharField(max_length=64, db_index=True, unique=True)
    
    # Request content
    request_body_hash = models.CharField(max_length=64, blank=True)
    request_headers_summary = models.JSONField(default=dict)
    
    # Response details
    status_code = models.IntegerField(db_index=True)
    response_body_hash = models.CharField(max_length=64, blank=True)
    
    # Performance
    latency_ms = models.IntegerField()  # Response time in milliseconds
    
    # Audit trail
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'audit_logs'
        app_label = 'audit_logs'
        indexes = [
            models.Index(fields=['tenant_id', 'created_at']),
            models.Index(fields=['user_id', 'created_at']),
            models.Index(fields=['endpoint', 'created_at']),
            models.Index(fields=['status_code', 'created_at']),
        ]
        verbose_name_plural = 'Audit Logs'
    
    def __str__(self):
        return f"{self.method} {self.endpoint} [{self.status_code}] ({self.latency_ms}ms)"
    
    @classmethod
    def log_request(cls, request_data: Dict[str, Any]) -> Optional['AuditLogModel']:
        """
        Create audit log entry
        
        Args:
            request_data: {
                'tenant_id': str,
                'user_id': str,
                'username': str,
                'endpoint': str,
                'method': str,
                'status_code': int,
                'latency_ms': int,
                'request_hash': str,
                'ip_address': str,
                'user_agent': str,
                'request_body_hash': str,
                'response_body_hash': str,
                'request_headers_summary': dict,
            }
        """
        try:
            log = cls.objects.create(**request_data)
            return log
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            return None


# ============================================================================
# AUDIT LOGGING MIDDLEWARE
# ============================================================================

class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all API requests to audit trail
    
    Tracks:
    - Endpoint (path)
    - HTTP method
    - User and tenant
    - Request/response hash
    - Status code
    - Response latency
    - IP address
    - Timestamp
    """
    
    # Paths to exclude from logging (reduce noise)
    EXEMPT_PATHS = [
        '/api/v1/health/',
        '/api/v1/health/check/',
        '/static/',
        '/admin/',
        '/api/v1/docs/',
        '/__debug__/',
    ]
    
    # Paths that shouldn't have request/response body hashed (large files)
    EXCLUDE_BODY_LOGGING = [
        '/api/v1/documents/upload/',
        '/api/v1/documents/download/',
        '/api/v1/ocr/',
        '/api/v1/files/',
    ]
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Log request and response"""
        
        # Skip exempt paths
        if self._is_exempt_path(request.path):
            return self.get_response(request)
        
        # Record start time
        start_time = time.time()
        
        # Extract request info
        request_data = self._extract_request_data(request)
        
        # Get response
        try:
            response = self.get_response(request)
        except Exception as e:
            # Log error response
            latency = int((time.time() - start_time) * 1000)
            request_data['status_code'] = 500
            request_data['latency_ms'] = latency
            request_data['error'] = str(e)
            
            AuditLogModel.log_request(request_data)
            raise
        
        # Update with response info
        latency = int((time.time() - start_time) * 1000)
        request_data['status_code'] = response.status_code
        request_data['latency_ms'] = latency
        request_data['response_body_hash'] = self._hash_response(response, request)
        
        # Log the request
        AuditLogModel.log_request(request_data)
        
        # Log slow requests
        if latency > settings.AUDIT_LOG_SLOW_REQUEST_THRESHOLD:
            logger.warning(
                f"SLOW_REQUEST: {request.method} {request.path} "
                f"took {latency}ms (user: {request_data.get('user_id')})"
            )
        
        return response
    
    def _is_exempt_path(self, path: str) -> bool:
        """Check if path should be excluded from audit logging"""
        for exempt_path in self.EXEMPT_PATHS:
            if path.startswith(exempt_path):
                return True
        return False
    
    def _extract_request_data(self, request: HttpRequest) -> Dict[str, Any]:
        """Extract and prepare request data for logging"""
        
        # Get user info
        tenant_id = getattr(request.user, 'tenant_id', None)
        user_id = getattr(request.user, 'user_id', None)
        username = getattr(request.user, 'username', 'anonymous')
        
        # Get IP address
        ip_address = self._get_client_ip(request)
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        # Build request hash (includes method, path, user, body)
        request_hash = self._generate_request_hash(
            method=request.method,
            path=request.path,
            user_id=user_id,
            body=request.body if not self._should_exclude_body(request.path) else b''
        )
        
        # Hash request body
        request_body_hash = ''
        if not self._should_exclude_body(request.path):
            try:
                request_body_hash = hashlib.sha256(request.body or b'').hexdigest()
            except:
                pass
        
        # Extract headers summary
        headers_summary = {
            'content_type': request.META.get('CONTENT_TYPE', ''),
            'accept': request.META.get('HTTP_ACCEPT', '')[:100],
            'authorization': 'Bearer ***' if request.META.get('HTTP_AUTHORIZATION') else None,
        }
        
        return {
            'tenant_id': tenant_id,
            'user_id': user_id,
            'username': username,
            'endpoint': request.path[:500],
            'method': request.method,
            'request_hash': request_hash,
            'request_body_hash': request_body_hash,
            'request_headers_summary': headers_summary,
            'ip_address': ip_address,
            'user_agent': user_agent,
        }
    
    def _should_exclude_body(self, path: str) -> bool:
        """Check if request body should be excluded from logging"""
        for exclude_path in self.EXCLUDE_BODY_LOGGING:
            if exclude_path in path:
                return True
        return False
    
    def _generate_request_hash(self, method: str, path: str, user_id: Optional[str], body: bytes) -> str:
        """Generate unique hash for request (for deduplication)"""
        hash_input = f"{method}:{path}:{user_id}:{hashlib.sha256(body or b'').hexdigest()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def _hash_response(self, response: HttpResponse, request: HttpRequest) -> str:
        """Hash response body"""
        if self._should_exclude_body(request.path):
            return ''
        
        try:
            content = response.content if hasattr(response, 'content') else b''
            # Only hash first 10KB to avoid large response logging
            content = content[:10240]
            return hashlib.sha256(content).hexdigest()
        except:
            return ''
    
    def _get_client_ip(self, request: HttpRequest) -> Optional[str]:
        """Extract client IP address from request"""
        # Check X-Forwarded-For first (proxy)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
            return ip
        
        # Fall back to REMOTE_ADDR
        return request.META.get('REMOTE_ADDR')


# ============================================================================
# AUDIT LOG RETENTION POLICY
# ============================================================================

class AuditLogRetentionPolicy:
    """
    Implements log retention policy
    
    Configuration in settings.py:
    AUDIT_LOG_RETENTION_DAYS = 90  # Keep logs for 90 days
    AUDIT_LOG_CLEANUP_BATCH_SIZE = 1000  # Delete 1000 at a time
    AUDIT_LOG_SLOW_REQUEST_THRESHOLD = 5000  # 5 seconds in ms
    """
    
    @staticmethod
    def cleanup_old_logs(retention_days: int = None) -> int:
        """
        Delete logs older than retention period
        
        Args:
            retention_days: Days to keep (uses settings if not provided)
        
        Returns:
            Number of logs deleted
        """
        if retention_days is None:
            retention_days = getattr(settings, 'AUDIT_LOG_RETENTION_DAYS', 90)
        
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        
        try:
            deleted_count, _ = AuditLogModel.objects.filter(
                created_at__lt=cutoff_date
            ).delete()
            
            logger.info(f"Deleted {deleted_count} old audit logs (older than {cutoff_date})")
            return deleted_count
        
        except Exception as e:
            logger.error(f"Error cleaning up audit logs: {e}")
            return 0
    
    @staticmethod
    def cleanup_by_batch(batch_size: int = None, retention_days: int = None) -> int:
        """
        Delete logs in batches to avoid locking database
        
        Args:
            batch_size: Size of each batch
            retention_days: Days to keep
        
        Returns:
            Total deleted
        """
        batch_size = batch_size or getattr(settings, 'AUDIT_LOG_CLEANUP_BATCH_SIZE', 1000)
        retention_days = retention_days or getattr(settings, 'AUDIT_LOG_RETENTION_DAYS', 90)
        
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        total_deleted = 0
        
        while True:
            # Delete in small batches
            logs_to_delete = AuditLogModel.objects.filter(
                created_at__lt=cutoff_date
            )[:batch_size]
            
            if not logs_to_delete.exists():
                break
            
            ids = list(logs_to_delete.values_list('id', flat=True))
            deleted_count, _ = AuditLogModel.objects.filter(id__in=ids).delete()
            total_deleted += deleted_count
            
            logger.info(f"Deleted batch of {deleted_count} logs, total: {total_deleted}")
        
        return total_deleted


# ============================================================================
# AUDIT LOG QUERIES AND ANALYSIS
# ============================================================================

class AuditLogAnalyzer:
    """
    Analyze audit logs for security insights
    """
    
    @staticmethod
    def get_user_activity(user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get user activity summary"""
        cutoff = timezone.now() - timedelta(days=days)
        
        logs = AuditLogModel.objects.filter(
            user_id=user_id,
            created_at__gte=cutoff
        )
        
        return {
            'user_id': user_id,
            'total_requests': logs.count(),
            'unique_endpoints': logs.values('endpoint').distinct().count(),
            'last_activity': logs.order_by('-created_at').first().created_at if logs.exists() else None,
            'by_method': dict(logs.values('method').annotate(count=models.Count('*')).values_list('method', 'count')),
            'by_status': dict(logs.values('status_code').annotate(count=models.Count('*')).values_list('status_code', 'count')),
            'avg_latency_ms': logs.aggregate(avg=models.Avg('latency_ms'))['avg'] or 0,
        }
    
    @staticmethod
    def get_tenant_activity(tenant_id: str, days: int = 7) -> Dict[str, Any]:
        """Get tenant activity summary"""
        cutoff = timezone.now() - timedelta(days=days)
        
        logs = AuditLogModel.objects.filter(
            tenant_id=tenant_id,
            created_at__gte=cutoff
        )
        
        return {
            'tenant_id': tenant_id,
            'total_requests': logs.count(),
            'unique_users': logs.values('user_id').distinct().count(),
            'unique_endpoints': logs.values('endpoint').distinct().count(),
            'error_rate': (logs.filter(status_code__gte=400).count() / max(1, logs.count())) * 100,
            'avg_latency_ms': logs.aggregate(avg=models.Avg('latency_ms'))['avg'] or 0,
            'most_accessed_endpoints': list(
                logs.values('endpoint')
                .annotate(count=models.Count('*'))
                .order_by('-count')[:5]
                .values_list('endpoint', 'count')
            ),
        }
    
    @staticmethod
    def get_error_summary(days: int = 7) -> Dict[str, Any]:
        """Get error summary"""
        cutoff = timezone.now() - timedelta(days=days)
        
        error_logs = AuditLogModel.objects.filter(
            status_code__gte=400,
            created_at__gte=cutoff
        )
        
        return {
            'total_errors': error_logs.count(),
            'by_status': dict(
                error_logs.values('status_code')
                .annotate(count=models.Count('*'))
                .values_list('status_code', 'count')
            ),
            'by_endpoint': dict(
                error_logs.values('endpoint')
                .annotate(count=models.Count('*'))
                .order_by('-count')[:10]
                .values_list('endpoint', 'count')
            ),
        }
    
    @staticmethod
    def find_suspicious_activity(days: int = 7) -> Dict[str, Any]:
        """Find potentially suspicious activity"""
        cutoff = timezone.now() - timedelta(days=days)
        
        # Find users with many 401/403 errors
        suspicious_users = AuditLogModel.objects.filter(
            status_code__in=[401, 403],
            created_at__gte=cutoff
        ).values('user_id').annotate(
            count=models.Count('*')
        ).filter(count__gte=5).order_by('-count')
        
        # Find IP addresses with many failures
        suspicious_ips = AuditLogModel.objects.filter(
            status_code__gte=400,
            created_at__gte=cutoff
        ).values('ip_address').annotate(
            count=models.Count('*')
        ).filter(count__gte=10).order_by('-count')
        
        return {
            'suspicious_users': list(suspicious_users),
            'suspicious_ips': list(suspicious_ips),
            'high_error_endpoints': AuditLogAnalyzer.get_error_summary(days),
        }


# ============================================================================
# MANAGEMENT COMMAND FOR CLEANUP
# ============================================================================

class Command(BaseCommand):
    """
    Django management command for audit log cleanup
    
    Usage: python manage.py cleanup_audit_logs
    """
    
    help = 'Clean up old audit logs based on retention policy'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Keep logs from last N days (default: 90)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Delete in batches of N records (default: 1000)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
    
    def handle(self, *args, **options):
        retention_days = options['days']
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        
        if dry_run:
            count = AuditLogModel.objects.filter(created_at__lt=cutoff_date).count()
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would delete {count} logs older than {cutoff_date}'
                )
            )
        else:
            deleted = AuditLogRetentionPolicy.cleanup_by_batch(batch_size, retention_days)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {deleted} audit logs'
                )
            )
