#!/usr/bin/env python3
"""
Real-Time Signature Polling Service
Polls SignNow API for signature updates and updates database in real-time
"""
import os
import sys
import django
import time
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.utils import timezone
from contracts.models import ESignatureContract, Signer, SigningAuditLog, SignNowCredential
from contracts.signnow_service import SignNowAPIService
import logging

logger = logging.getLogger(__name__)

class RealTimeSignaturePoller:
    """
    Polls SignNow API for real-time signature updates
    """
    
    def __init__(self):
        self.api_service = SignNowAPIService()
        self.poll_interval = 5  # Poll every 5 seconds
        
    def poll_signnow_for_updates(self):
        """
        Poll all contracts for signature updates from SignNow
        """
        print("\n" + "=" * 80)
        print("REAL-TIME SIGNATURE POLLING SERVICE")
        print("=" * 80)
        
        # Get all non-completed contracts
        contracts = ESignatureContract.objects.exclude(status='completed')
        
        print(f"\n🔄 Polling {contracts.count()} active contracts for updates...")
        
        for contract in contracts:
            print(f"\n📋 Contract: {contract.contract_id}")
            
            # Skip if no valid SignNow document ID
            if not contract.signnow_document_id or contract.signnow_document_id.startswith('signnow_'):
                print(f"   ⚠️  Skipping: Invalid SignNow document ID (test data)")
                continue
            
            try:
                # Poll SignNow for document status
                print(f"   🔍 Polling SignNow API...")
                status = self.api_service.get_document_status(contract.signnow_document_id)
                
                print(f"   ✅ Status from SignNow: {status.get('status')}")
                
                # Update contract status if changed
                old_status = contract.status
                new_status = self._map_status(status.get('status'))
                
                if old_status != new_status:
                    print(f"   📝 Updating contract status: {old_status} → {new_status}")
                    contract.status = new_status
                    contract.save()
                    
                    # Log status change
                    SigningAuditLog.objects.create(
                        esignature_contract=contract,
                        event='status_updated',
                        message=f'Status updated: {old_status} → {new_status}',
                        old_status=old_status,
                        new_status=new_status
                    )
                
                # Update signers with new signature data
                self._update_signers(contract, status.get('signers', []))
                
            except Exception as e:
                print(f"   ❌ Error polling SignNow: {str(e)}")
                # Use cached data
                print(f"   💾 Using cached data from database")
        
        print("\n" + "=" * 80)
        print("✅ POLLING CYCLE COMPLETE")
        print("=" * 80)
    
    def _map_status(self, signnow_status):
        """Map SignNow status to internal status"""
        mapping = {
            'pending': 'sent',
            'viewed': 'in_progress',
            'in_progress': 'in_progress',
            'completed': 'completed',
            'declined': 'declined',
            'expired': 'expired',
        }
        return mapping.get(signnow_status, signnow_status)
    
    def _update_signers(self, contract, signers_data):
        """Update signer records with latest data from SignNow"""
        for signer_data in signers_data:
            # Find matching signer by email
            try:
                signer = Signer.objects.get(
                    esignature_contract=contract,
                    email=signer_data.get('email')
                )
                
                old_status = signer.status
                new_status = signer_data.get('status', 'pending')
                
                # Update signer data
                signer.status = new_status
                if signer_data.get('signed_at'):
                    signer.signed_at = signer_data['signed_at']
                if signer_data.get('status') == 'signed':
                    signer.has_signed = True
                
                signer.save()
                
                # Log if status changed
                if old_status != new_status:
                    print(f"      ✓ Signer {signer.name} updated: {old_status} → {new_status}")
                    
                    SigningAuditLog.objects.create(
                        esignature_contract=contract,
                        signer=signer,
                        event='signer_status_updated',
                        message=f'{signer.name} status: {old_status} → {new_status}',
                        old_status=old_status,
                        new_status=new_status
                    )
                
            except Signer.DoesNotExist:
                print(f"      ⚠️  Signer {signer_data.get('email')} not found in contract")
    
    def continuous_poll(self, duration_seconds=None):
        """
        Continuously poll SignNow for updates
        
        Args:
            duration_seconds: How long to poll (None = infinite)
        """
        print("\n🚀 Starting Real-Time Signature Polling Service...")
        print(f"   Poll interval: {self.poll_interval} seconds")
        
        start_time = time.time()
        poll_count = 0
        
        try:
            while True:
                poll_count += 1
                print(f"\n[Poll #{poll_count}] {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                self.poll_signnow_for_updates()
                
                # Check if duration exceeded
                if duration_seconds and (time.time() - start_time) > duration_seconds:
                    print(f"\n⏱️  Poll duration exceeded ({duration_seconds}s). Stopping.")
                    break
                
                # Wait before next poll
                print(f"⏳ Waiting {self.poll_interval}s until next poll...")
                time.sleep(self.poll_interval)
                
        except KeyboardInterrupt:
            print(f"\n\n⛔ Polling stopped by user")
        except Exception as e:
            print(f"\n\n❌ Polling error: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    poller = RealTimeSignaturePoller()
    
    # Parse arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Single poll
        print("Running single poll cycle...")
        poller.poll_signnow_for_updates()
    elif len(sys.argv) > 1 and sys.argv[1].isdigit():
        # Poll for N seconds
        duration = int(sys.argv[1])
        print(f"Polling for {duration} seconds...")
        poller.continuous_poll(duration_seconds=duration)
    else:
        # Continuous polling
        print("Starting continuous polling (press Ctrl+C to stop)...")
        poller.continuous_poll()
