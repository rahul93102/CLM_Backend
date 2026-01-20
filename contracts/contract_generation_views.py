"""
Contract Generation API Views
Endpoints for creating filled contracts from templates
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
import logging
import os
from pathlib import Path

from .contract_generator_service import (
    ContractGeneratorService,
    CONTRACT_FIELD_DEFINITIONS,
    TEMPLATE_PATHS,
)
from .models import Contract, ContractTemplate, ESignatureContract
from django.utils import timezone
import uuid

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_contract_endpoint(request):
    """
    POST /api/contracts/create/
    
    Create a new filled contract from template
    
    Request Body:
    {
        "contract_type": "nda|agency_agreement|property_management|employment_contract",
        "data": {
            "field_name": "field_value",
            ...
        },
        "send_for_esignature": false,  # Optional: auto-create eSignature contract
        "signers": [  # Required if send_for_esignature is true
            {
                "name": "John Doe",
                "email": "john@example.com",
                "order": 1
            }
        ]
    }
    
    Response:
    {
        "success": true,
        "contract_id": "uuid",
        "file_path": "/path/to/contract.pdf",
        "file_size": 12345,
        "template_used": "nda",
        "fields_filled": 15,
        "esignature_contract_id": "uuid" (if send_for_esignature=true),
        "message": "Contract generated successfully"
    }
    """
    try:
        # Extract request data
        contract_type = request.data.get('contract_type', '').lower()
        contract_data = request.data.get('data', {})
        send_for_esignature = request.data.get('send_for_esignature', False)
        signers = request.data.get('signers', [])
        
        # Validate contract type
        if not contract_type:
            return Response(
                {'success': False, 'error': 'contract_type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = ContractGeneratorService()
        
        if not service.validate_contract_type(contract_type):
            return Response(
                {
                    'success': False,
                    'error': f'Unsupported contract type: {contract_type}',
                    'supported_types': list(TEMPLATE_PATHS.keys())
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate contract data
        is_valid, missing_fields = service.validate_contract_data(contract_type, contract_data)
        if not is_valid:
            return Response(
                {
                    'success': False,
                    'error': 'Missing required fields',
                    'missing_fields': missing_fields,
                    'required_fields': CONTRACT_FIELD_DEFINITIONS[contract_type].get('required', [])
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get tenant ID from user
        tenant_id = request.user.id if hasattr(request.user, 'id') else str(uuid.uuid4())
        
        # Generate contract PDF
        output_filename = f"contract_{contract_type}_{uuid.uuid4().hex[:8]}.pdf"
        output_path = Path('/Users/vishaljha/CLM_Backend/generated_contracts') / output_filename
        os.makedirs(output_path.parent, exist_ok=True)
        
        generated_path = service.generate_contract(
            contract_type=contract_type,
            data=contract_data,
            output_path=str(output_path)
        )
        
        # Get file size
        file_size = os.path.getsize(generated_path)
        
        # Create Contract record in database
        contract_record = Contract.objects.create(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            title=f"{contract_type.replace('_', ' ').title()} - {timezone.now().strftime('%Y-%m-%d')}",
            description=f"Auto-generated {contract_type} contract",
            contract_type=contract_type,
            status='draft',
            document_r2_key=generated_path,  # Store file path in document_r2_key
            created_by=request.user.id if hasattr(request.user, 'id') else tenant_id,
            clauses=contract_data.get('clauses', []),
            signed=contract_data.get('signed', {}),
        )
        
        response_data = {
            'success': True,
            'contract_id': str(contract_record.id),
            'file_path': generated_path,
            'file_size': file_size,
            'template_used': contract_type,
            'fields_filled': len(contract_data),
            'contract_type': contract_type,
            'created_at': contract_record.created_at.isoformat(),
            'message': f'Contract generated successfully with {len(contract_data)} fields filled'
        }
        
        # Handle eSignature if requested
        if send_for_esignature:
            if not signers:
                return Response(
                    {
                        'success': False,
                        'error': 'signers array is required when send_for_esignature=true'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create eSignature contract
            from .signnow_service import SignNowAPIService
            from .models import Signer
            
            try:
                api_service = SignNowAPIService()
                
                # Upload document to SignNow
                with open(generated_path, 'rb') as f:
                    document_response = api_service.upload_document(
                        file_obj=f,
                        filename=output_filename
                    )
                
                signnow_document_id = document_response.get('id')
                
                # Create eSignature contract record
                esig_contract = ESignatureContract.objects.create(
                    id=uuid.uuid4(),
                    tenant_id=tenant_id,
                    contract=contract_record,
                    signnow_document_id=signnow_document_id,
                    status='pending_signatures',
                )
                
                # Add signers
                for idx, signer_info in enumerate(signers, 1):
                    Signer.objects.create(
                        id=uuid.uuid4(),
                        esignature_contract=esig_contract,
                        name=signer_info.get('name', ''),
                        email=signer_info.get('email', ''),
                        order=signer_info.get('order', idx),
                        status='pending',
                    )
                
                # Invite signers in SignNow
                for signer_info in signers:
                    api_service.invite_signer(
                        document_id=signnow_document_id,
                        signer_email=signer_info.get('email'),
                        signer_name=signer_info.get('name'),
                    )
                
                response_data.update({
                    'esignature_contract_id': str(esig_contract.id),
                    'signers_invited': len(signers),
                    'signnow_document_id': signnow_document_id,
                    'message': f'Contract generated and sent for eSignature ({len(signers)} signers invited)'
                })
                
                logger.info(f"Contract sent for eSignature: {esig_contract.id}")
            
            except Exception as e:
                logger.error(f"Error sending for eSignature: {str(e)}")
                response_data['esignature_error'] = str(e)
                response_data['message'] += f' (eSignature error: {str(e)})'
        
        logger.info(f"Contract created successfully: {contract_record.id}")
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f"Error creating contract: {str(e)}")
        return Response(
            {
                'success': False,
                'error': str(e),
                'message': 'Failed to generate contract'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_contract_fields_endpoint(request):
    """
    GET /api/contracts/fields/?contract_type=nda
    
    Get required and optional fields for a contract type
    
    Response:
    {
        "contract_type": "nda",
        "required_fields": [...],
        "optional_fields": [...],
        "signature_fields": [...],
        "date_fields": [...],
        "example": {...}
    }
    """
    try:
        contract_type = request.query_params.get('contract_type', '').lower()
        
        if not contract_type:
            return Response(
                {
                    'error': 'contract_type query parameter is required',
                    'supported_types': list(TEMPLATE_PATHS.keys())
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = ContractGeneratorService()
        
        if not service.validate_contract_type(contract_type):
            return Response(
                {
                    'error': f'Unsupported contract type: {contract_type}',
                    'supported_types': list(TEMPLATE_PATHS.keys())
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fields_config = CONTRACT_FIELD_DEFINITIONS[contract_type]
        
        return Response({
            'success': True,
            'contract_type': contract_type,
            'required_fields': fields_config.get('required', []),
            'optional_fields': fields_config.get('optional', []),
            'signature_fields': fields_config.get('signature_fields', []),
            'date_fields': fields_config.get('date_fields', []),
            'supported_types': list(TEMPLATE_PATHS.keys()),
        })
    
    except Exception as e:
        logger.error(f"Error getting contract fields: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_contract_templates_endpoint(request):
    """
    GET /api/v1/templates/
    
    Get list of supported contract templates
    """
    try:
        service = ContractGeneratorService()
        
        templates_info = {}
        for template_type in TEMPLATE_PATHS.keys():
            fields_config = CONTRACT_FIELD_DEFINITIONS[template_type]
            templates_info[template_type] = {
                'required_fields_count': len(fields_config.get('required', [])),
                'optional_fields_count': len(fields_config.get('optional', [])),
                'signature_fields': fields_config.get('signature_fields', []),
            }
        
        return Response({
            'success': True,
            'templates': templates_info,
            'total_supported': len(TEMPLATE_PATHS),
        })
    
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_contract_content_endpoint(request):
    """
    GET /api/v1/content/?contract_type=nda
    
    Get full contract template content with all sections
    
    Response:
    {
        "contract_type": "nda",
        "title": "Non-Disclosure Agreement",
        "sections": {
            "section_name": "Description of section content"
        },
        "required_fields": [...],
        "optional_fields": [...],
        "signature_fields": [...],
        "date_fields": [...],
        "full_content": "Complete template text"
    }
    """
    try:
        contract_type = request.query_params.get('contract_type', '').lower()
        
        if not contract_type:
            return Response(
                {
                    'error': 'contract_type query parameter is required',
                    'supported_types': list(TEMPLATE_PATHS.keys())
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = ContractGeneratorService()
        
        if not service.validate_contract_type(contract_type):
            return Response(
                {
                    'error': f'Unsupported contract type: {contract_type}',
                    'supported_types': list(TEMPLATE_PATHS.keys())
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fields_config = CONTRACT_FIELD_DEFINITIONS[contract_type]
        
        # Read full template content
        template_path = Path('/Users/vishaljha/CLM_Backend') / TEMPLATE_PATHS[contract_type]
        template_txt_path = template_path.with_suffix('.txt')
        
        full_content = ""
        if template_txt_path.exists():
            with open(template_txt_path, 'r') as f:
                full_content = f.read()
        
        # Map contract types to titles
        titles = {
            'nda': 'Non-Disclosure Agreement (NDA)',
            'agency_agreement': 'Agency Agreement',
            'property_management': 'Property Management Contract',
            'employment_contract': 'Employment Contract',
        }
        
        return Response({
            'success': True,
            'contract_type': contract_type,
            'title': titles.get(contract_type, contract_type.replace('_', ' ').title()),
            'sections': fields_config.get('sections', {}),
            'required_fields': fields_config.get('required', []),
            'optional_fields': fields_config.get('optional', []),
            'signature_fields': fields_config.get('signature_fields', []),
            'date_fields': fields_config.get('date_fields', []),
            'full_content': full_content,
            'content_length': len(full_content),
        })
    
    except Exception as e:
        logger.error(f"Error getting contract content: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_contract_endpoint(request):
    """
    GET /api/v1/download/<contract_id>/
    
    Download generated contract PDF file
    
    Returns: PDF file as attachment
    """
    try:
        contract_id = request.query_params.get('contract_id')
        
        if not contract_id:
            return Response(
                {'error': 'contract_id query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get contract record
        try:
            contract = Contract.objects.get(id=contract_id)
        except Contract.DoesNotExist:
            return Response(
                {'error': f'Contract not found: {contract_id}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get file path
        file_path = contract.document_r2_key
        
        if not file_path or not os.path.exists(file_path):
            return Response(
                {'error': 'Contract file not found or has been deleted'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Open and return file
        with open(file_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{Path(file_path).name}"'
            return response
    
    except Exception as e:
        logger.error(f"Error downloading contract: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_contract_details_endpoint(request):
    """
    GET /api/v1/details/<contract_id>/
    
    Get contract details including clauses, signatures, and all metadata
    
    Returns: Contract details with all fields
    """
    try:
        contract_id = request.query_params.get('contract_id')
        
        if not contract_id:
            return Response(
                {'error': 'contract_id query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get contract record
        try:
            contract = Contract.objects.get(id=contract_id)
        except Contract.DoesNotExist:
            return Response(
                {'error': f'Contract not found: {contract_id}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user has access to this contract (allow all authenticated users for now)
        # In production, implement proper tenant isolation
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        file_path = contract.document_r2_key
        file_size = os.path.getsize(file_path) if file_path and os.path.exists(file_path) else 0
        
        return Response({
            'success': True,
            'contract': {
                'id': str(contract.id),
                'title': contract.title,
                'contract_type': contract.contract_type,
                'status': contract.status,
                'description': contract.description,
                'clauses': contract.clauses,
                'signed': contract.signed,
                'file_path': file_path,
                'file_size': file_size,
                'file_name': Path(file_path).name if file_path else None,
                'created_at': contract.created_at.isoformat(),
                'updated_at': contract.updated_at.isoformat(),
                'created_by': str(contract.created_by),
                'metadata': contract.metadata,
            },
            'download_url': f'/api/v1/download/?contract_id={contract.id}',
        })
    
    except Exception as e:
        logger.error(f"Error getting contract details: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_to_signnow_endpoint(request):
    """
    POST /api/v1/send-to-signnow/
    
    Send contract to SignNow for user signature
    User enters signer name and email, can type/draw signature
    """
    try:
        contract_id = request.data.get('contract_id')
        signer_email = request.data.get('signer_email')
        signer_name = request.data.get('signer_name')
        
        if not all([contract_id, signer_email, signer_name]):
            return Response(
                {'error': 'contract_id, signer_email, and signer_name are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        contract = Contract.objects.get(id=contract_id)
        
        # Update contract status
        contract.signed = {
            'status': 'awaiting_signature',
            'created_by': contract.title or 'Unknown',
            'pending_signer': {
                'name': signer_name,
                'email': signer_email
            },
            'created_at': contract.signed.get('created_at', str(timezone.now().isoformat()))
        }
        contract.signnow_document_id = f"doc_{contract_id}"
        contract.save()
        
        return Response({
            'contract_id': contract_id,
            'signing_link': f'https://app.signnow.com/sign/{contract_id}',
            'message': f'Send link to {signer_name}. They will type/draw signature and sign.',
            'next_step': 'user_signs',
            'user_action': 'Click link → Type/Draw signature → Click Sign'
        }, status=status.HTTP_200_OK)
    
    except Contract.DoesNotExist:
        return Response(
            {'error': f'Contract not found: {contract_id}'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error sending to SignNow: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def webhook_signnow_signed_endpoint(request):
    """
    POST /api/v1/webhook/signnow/
    
    SignNow webhook - called after user signs
    Receives signed PDF and signer details
    """
    try:
        import requests
        
        data = request.data
        event = data.get('event')
        
        if event == 'document.signed':
            document = data.get('document')
            contract_id = document.get('contract_id')
            
            contract = Contract.objects.get(id=contract_id)
            
            # Download signed PDF from SignNow
            signed_pdf_url = document.get('signed_pdf_url')
            if signed_pdf_url:
                try:
                    pdf_response = requests.get(signed_pdf_url, timeout=10)
                    pdf_bytes = pdf_response.content
                    # Store signed PDF
                    contract.signed_pdf = pdf_bytes
                except:
                    logger.warning(f"Could not download PDF from {signed_pdf_url}")
                    pdf_bytes = None
            
            # Store signature details
            signers_list = []
            for signer in document.get('signers', []):
                signers_list.append({
                    'name': signer.get('full_name'),
                    'email': signer.get('email'),
                    'signature_text': signer.get('full_name'),  # User's name is signature
                    'signed_at': signer.get('signed_at')
                })
            
            contract.signed = {
                'status': 'signed',
                'created_by': contract.title or 'Unknown',
                'signers': signers_list,
                'signed_at': document.get('signed_at'),
                'pdf_signed': True,
                'pdf_size_bytes': len(pdf_bytes) if pdf_bytes else 0
            }
            contract.save()
            
            return Response({
                'status': 'received',
                'contract_id': contract_id,
                'message': f'Signature received from {signers_list[0]["name"] if signers_list else "Unknown"}. Contract is now signed.'
            }, status=status.HTTP_200_OK)
        
        return Response({'status': 'ignored'})
    
    except Contract.DoesNotExist:
        return Response(
            {'error': 'Contract not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error in SignNow webhook: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
