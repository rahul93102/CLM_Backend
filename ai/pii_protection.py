"""
PII Protection and Scrubbing Service
"""
import logging
import re
from typing import Tuple, Dict, List

logger = logging.getLogger(__name__)


class PIIScrubber:
    """
    Service to detect and redact Personally Identifiable Information (PII)
    from contract text before sending to AI APIs
    """
    
    # Regex patterns for common PII
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'date_of_birth': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        'passport': r'\b[A-Z]{2}\d{6,9}\b',
        'address': r'\b\d+\s+[A-Z][a-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr)\b',
    }
    
    REDACTION_MARKER = '[REDACTED]'
    
    @classmethod
    def scrub(cls, text: str, log_redactions: bool = True) -> Tuple[str, Dict[str, List[str]]]:
        """
        Scrub PII from text
        
        Args:
            text: Text to scrub
            log_redactions: Whether to log what was redacted
            
        Returns:
            Tuple of (scrubbed_text, redactions_dict)
            redactions_dict: {pii_type: [found_values]}
        """
        scrubbed_text = text
        redactions = {}
        
        for pii_type, pattern in cls.PII_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            if matches:
                redactions[pii_type] = matches
                
                # Replace all occurrences
                scrubbed_text = re.sub(
                    pattern,
                    cls.REDACTION_MARKER,
                    scrubbed_text,
                    flags=re.IGNORECASE
                )
                
                if log_redactions:
                    logger.info(
                        f"Scrubbed {len(matches)} {pii_type} instances"
                    )
        
        return scrubbed_text, redactions
    
    @classmethod
    def is_safe_for_api(cls, text: str, threshold: float = 0.0) -> bool:
        """
        Check if text is safe to send to external AI APIs
        
        Args:
            text: Text to check
            threshold: Minimum acceptable safety (0.0 = any PII is unsafe, 1.0 = all PII allowed)
            
        Returns:
            Boolean indicating if text is safe
        """
        _, redactions = cls.scrub(text, log_redactions=False)
        
        if not redactions and threshold >= 0.0:
            return True
        
        if threshold < 1.0:
            return False
        
        return True
    
    @classmethod
    def get_redaction_summary(cls, redactions: Dict[str, List[str]]) -> str:
        """
        Create human-readable summary of redactions
        """
        if not redactions:
            return "No PII detected"
        
        summary = "PII Redaction Summary:\n"
        for pii_type, values in redactions.items():
            summary += f"  - {pii_type}: {len(values)} instance(s)\n"
        
        return summary


class ScrubberAuditLog:
    """
    Log all scrubbing operations for compliance
    """
    
    @classmethod
    def log_scrub_operation(cls, user_id: str, tenant_id: str, 
                           text_length: int, redactions: Dict[str, List[str]],
                           operation_type: str = 'pre_api_call'):
        """
        Log a scrubbing operation
        
        Args:
            user_id: User performing the operation
            tenant_id: Tenant for which operation occurred
            text_length: Length of original text
            redactions: Redactions that were made
            operation_type: Type of operation (pre_api_call, manual_redaction, etc)
        """
        redaction_count = sum(len(v) for v in redactions.values())
        
        logger.info(
            f"PII Scrub [{operation_type}] - User: {user_id}, Tenant: {tenant_id}, "
            f"Text Length: {text_length}, Redactions: {redaction_count}"
        )
        
        # TODO: Store in audit_logs table for compliance reports
