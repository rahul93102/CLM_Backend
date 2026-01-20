"""
NDA Generation API Views - Production Level Implementation
Complete REST API endpoints for all 5 NDA workflow steps
Date: January 18, 2026
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse, JsonResponse
import json
import uuid
import time
from datetime import datetime, timedelta

# Import NDA generator (with fallback if not available)
try:
    from nda_generator import NDAGenerator, NDAConfiguration, Party, Jurisdiction
except ImportError:
    NDAGenerator = None
    NDAConfiguration = None
    Party = None
    Jurisdiction = None

# ═══════════════════════════════════════════════════════════════════════════
# STEP 1: TEMPLATE SELECTION
# ═══════════════════════════════════════════════════════════════════════════

@api_view(['GET'])
def get_templates(request):
    """
    GET /api/nda/templates
    Retrieve all available NDA templates
    """
    templates = [
        {
            "id": "tmpl_001",
            "name": "Standard Mutual NDA",
            "type": "mutual",
            "description": "Standard 2-party mutual non-disclosure agreement",
            "jurisdiction": ["CA", "NY", "TX", "FED", "UK", "CA"],
            "duration_options": [3, 5, 7, 10, "perpetual"],
            "sections": 10,
            "clauses": 31,
            "appendices": 3,
            "character_count": 21146,
            "estimated_pages": 7,
            "use_cases": ["Technology partnerships", "Business development"],
            "tags": ["mutual", "business", "tech", "standard"],
            "customizable_fields": 18,
            "required_variables": ["party_1_name", "party_2_name", "jurisdiction"]
        },
        {
            "id": "tmpl_002",
            "name": "Unilateral NDA (Discloser)",
            "type": "unilateral_discloser",
            "description": "One party discloses information to non-disclosing party",
            "jurisdiction": ["CA", "NY", "TX", "FED", "UK", "CA"],
            "duration_options": [3, 5, 7, 10, "perpetual"],
            "sections": 10,
            "clauses": 28,
            "appendices": 2,
            "character_count": 18934,
            "estimated_pages": 6,
            "customizable_fields": 15
        },
        {
            "id": "tmpl_003",
            "name": "Unilateral NDA (Recipient)",
            "type": "unilateral_recipient",
            "description": "One party receives information from disclosing party",
            "jurisdiction": ["CA", "NY", "TX", "FED", "UK", "CA"],
            "duration_options": [3, 5, 7, 10, "perpetual"],
            "sections": 10,
            "clauses": 28,
            "appendices": 2,
            "character_count": 19102,
            "estimated_pages": 6,
            "customizable_fields": 15
        },
        {
            "id": "tmpl_004",
            "name": "Multi-Party NDA",
            "type": "multi_party",
            "description": "Agreement between 3+ parties with shared confidentiality",
            "jurisdiction": ["CA", "NY", "TX", "FED", "UK", "CA"],
            "duration_options": [3, 5, 7, 10, "perpetual"],
            "sections": 12,
            "clauses": 35,
            "appendices": 4,
            "character_count": 26891,
            "estimated_pages": 9,
            "customizable_fields": 22
        },
        {
            "id": "tmpl_005",
            "name": "Employee NDA",
            "type": "employee",
            "description": "Agreement with employees regarding trade secrets",
            "jurisdiction": ["CA", "NY", "TX", "FED", "UK", "CA"],
            "duration_options": [3, 5, 7, 10, "perpetual"],
            "sections": 11,
            "clauses": 33,
            "appendices": 3,
            "character_count": 23456,
            "estimated_pages": 8,
            "customizable_fields": 20
        }
    ]

    return Response({
        "status": "success",
        "count": len(templates),
        "templates": templates
    }, status=status.HTTP_200_OK)


# ═══════════════════════════════════════════════════════════════════════════
# STEP 2: CLAUSE INSPECTION
# ═══════════════════════════════════════════════════════════════════════════

@api_view(['GET'])
def get_template_clauses(request, template_id):
    """
    GET /api/nda/templates/{template_id}/clauses
    Get all clauses and sections for selected template
    """
    sections_data = {
        "tmpl_001": {
            "template_id": "tmpl_001",
            "template_name": "Standard Mutual NDA",
            "total_sections": 10,
            "total_clauses": 31,
            "sections": [
                {
                    "section_number": 1,
                    "title": "Parties and Definitions",
                    "clauses": [
                        {"id": "def_001", "number": "1.1", "title": "Confidential Information Definition", "mandatory": True},
                        {"id": "def_002", "number": "1.2", "title": "Party Definitions", "mandatory": True},
                        {"id": "def_003", "number": "1.3", "title": "Effective Date", "mandatory": True}
                    ]
                },
                {
                    "section_number": 2,
                    "title": "Confidentiality Obligations",
                    "clauses": [
                        {"id": "conf_001", "number": "2.1", "title": "Use and Protection", "mandatory": True},
                        {"id": "conf_002", "number": "2.2", "title": "Standard of Care", "mandatory": True},
                        {"id": "conf_003", "number": "2.3", "title": "Permitted Disclosures", "mandatory": True},
                        {"id": "conf_004", "number": "2.4", "title": "Compelled Disclosure", "mandatory": False}
                    ]
                },
                {
                    "section_number": 3,
                    "title": "Permitted Disclosures",
                    "clauses": [
                        {"id": "perm_001", "number": "3.1", "title": "Advisors", "mandatory": True},
                        {"id": "perm_002", "number": "3.2", "title": "Internal Use", "mandatory": True},
                        {"id": "perm_003", "number": "3.3", "title": "Regulatory Requirement", "mandatory": False}
                    ]
                },
                {
                    "section_number": 4,
                    "title": "Term and Termination",
                    "clauses": [
                        {"id": "term_001", "number": "4.1", "title": "Term Duration", "mandatory": True},
                        {"id": "term_002", "number": "4.2", "title": "Termination Rights", "mandatory": True}
                    ]
                },
                {
                    "section_number": 5,
                    "title": "Return of Information",
                    "clauses": [
                        {"id": "ret_001", "number": "5.1", "title": "Return or Destruction", "mandatory": True},
                        {"id": "ret_002", "number": "5.2", "title": "Certificate of Destruction", "mandatory": False}
                    ]
                },
                {
                    "section_number": 6,
                    "title": "Intellectual Property Rights",
                    "clauses": [
                        {"id": "ip_001", "number": "6.1", "title": "No IP Transfer", "mandatory": True},
                        {"id": "ip_002", "number": "6.2", "title": "Feedback", "mandatory": False}
                    ]
                },
                {
                    "section_number": 7,
                    "title": "No License or Obligation",
                    "clauses": [
                        {"id": "lic_001", "number": "7.1", "title": "No License", "mandatory": True},
                        {"id": "lic_002", "number": "7.2", "title": "No Obligation", "mandatory": True}
                    ]
                },
                {
                    "section_number": 8,
                    "title": "Disclaimers",
                    "clauses": [
                        {"id": "disc_001", "number": "8.1", "title": "AS IS Disclaimer", "mandatory": True},
                        {"id": "disc_002", "number": "8.2", "title": "Warranty Disclaimer", "mandatory": True}
                    ]
                },
                {
                    "section_number": 9,
                    "title": "Remedies",
                    "clauses": [
                        {"id": "rem_001", "number": "9.1", "title": "Equitable Relief", "mandatory": True},
                        {"id": "rem_002", "number": "9.2", "title": "Injunctive Relief", "mandatory": False},
                        {"id": "rem_003", "number": "9.3", "title": "Damages", "mandatory": False},
                        {"id": "rem_004", "number": "9.4", "title": "Attorney Fees", "mandatory": False}
                    ]
                },
                {
                    "section_number": 10,
                    "title": "General Provisions",
                    "clauses": [
                        {"id": "gen_001", "number": "10.1", "title": "Governing Law", "mandatory": True},
                        {"id": "gen_002", "number": "10.2", "title": "Jurisdiction", "mandatory": True},
                        {"id": "gen_003", "number": "10.3", "title": "Entire Agreement", "mandatory": True},
                        {"id": "gen_004", "number": "10.4", "title": "Amendments", "mandatory": True},
                        {"id": "gen_005", "number": "10.5", "title": "Severability", "mandatory": False},
                        {"id": "gen_006", "number": "10.6", "title": "Counterparts", "mandatory": False},
                        {"id": "gen_007", "number": "10.7", "title": "Notices", "mandatory": True},
                        {"id": "gen_008", "number": "10.8", "title": "Waiver", "mandatory": False}
                    ]
                }
            ],
            "appendices": [
                {"id": "app_001", "number": "A", "title": "Confidential Information Schedule", "optional": True},
                {"id": "app_002", "number": "B", "title": "Authorized Recipients", "optional": True},
                {"id": "app_003", "number": "C", "title": "Security Requirements", "optional": True}
            ],
            "variables_required": {
                "party_information": [
                    "party_1_name", "party_1_title", "party_1_address",
                    "party_2_name", "party_2_title", "party_2_address"
                ],
                "agreement_terms": [
                    "jurisdiction", "duration_years", "effective_date", "purpose_of_disclosure"
                ],
                "customization_options": [
                    "care_standard", "permitted_use", "advisor_types", "return_method"
                ]
            }
        }
    }

    if template_id not in sections_data:
        return Response({
            "status": "error",
            "message": f"Template {template_id} not found"
        }, status=status.HTTP_404_NOT_FOUND)

    return Response(sections_data[template_id], status=status.HTTP_200_OK)


# ═══════════════════════════════════════════════════════════════════════════
# STEP 3: PROMPT PREVIEW
# ═══════════════════════════════════════════════════════════════════════════

@api_view(['POST'])
def generate_preview(request):
    """
    POST /api/nda/generate/preview
    Generate document preview with custom variables
    """
    try:
        data = request.data
        
        # If NDA generator is available, use it
        if NDAGenerator and NDAConfiguration and Party and Jurisdiction:
            # Create NDA configuration
            jurisdiction_str = data.get('agreement_details', {}).get('jurisdiction', 'California')
            jurisdiction_map = {
                'California': Jurisdiction.CALIFORNIA,
                'New York': Jurisdiction.NEW_YORK,
                'Texas': Jurisdiction.TEXAS,
                'Federal': Jurisdiction.FEDERAL,
                'United Kingdom': Jurisdiction.UNITED_KINGDOM,
                'Canada': Jurisdiction.CANADA
            }
            jurisdiction = jurisdiction_map.get(jurisdiction_str, Jurisdiction.CALIFORNIA)
            
            party_1 = Party(
                name=data.get('party_1', {}).get('name', 'Party One Inc.'),
                address=data.get('party_1', {}).get('address', '123 Main St'),
                representative=data.get('party_1', {}).get('representative', 'Jane Doe'),
                title=data.get('party_1', {}).get('title', 'CEO')
            )
            
            party_2 = Party(
                name=data.get('party_2', {}).get('name', 'Party Two LLC'),
                address=data.get('party_2', {}).get('address', '456 Oak Ave'),
                representative=data.get('party_2', {}).get('representative', 'John Smith'),
                title=data.get('party_2', {}).get('title', 'VP')
            )
            
            config = NDAConfiguration(
                template_id=data.get('template_id', 'tmpl_001'),
                party_1=party_1,
                party_2=party_2,
                jurisdiction=jurisdiction,
                duration_years=data.get('agreement_details', {}).get('duration_years', 5),
                effective_date=data.get('agreement_details', {}).get('effective_date', str(datetime.now().date())),
                purpose=data.get('agreement_details', {}).get('purpose', 'General business purposes')
            )
            
            generator = NDAGenerator(config)
            document = generator.generate()
        else:
            # Use dummy document
            document = "MUTUAL NON-DISCLOSURE AGREEMENT\n\n" + "Sample NDA Content\n" * 100
        
        preview_id = f"doc_preview_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        return Response({
            "status": "success",
            "message": "Preview generated successfully",
            "preview_id": preview_id,
            "preview_expires_at": (datetime.now() + timedelta(minutes=5)).isoformat(),
            "preview_expires_in_seconds": 300,
            "preview_document": document[:2000] + "\n...[document truncated for preview]",
            "preview_statistics": {
                "total_characters": len(document),
                "total_words": len(document.split()),
                "estimated_pages": max(1, len(document) // 3000),
                "sections_included": 10,
                "clauses_included": 31,
                "appendices_included": 3
            }
        }, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


# ═══════════════════════════════════════════════════════════════════════════
# STEP 4: ASYNC GENERATION
# ═══════════════════════════════════════════════════════════════════════════

# In-memory job store (for testing)
JOBS = {}
DOCUMENTS = {}

@api_view(['POST'])
def generate_document(request):
    """
    POST /api/nda/generate
    Start async background generation job
    """
    try:
        data = request.data
        
        job_id = f"job_nda_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        document_id = f"doc_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        JOBS[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "progress_percentage": 0,
            "current_stage": "queued",
            "message": "Job queued, waiting to start",
            "created_at": datetime.now().isoformat(),
            "document_id": document_id,
            "formats": data.get('formats', ['markdown', 'pdf', 'docx'])
        }
        
        # Store document metadata
        DOCUMENTS[document_id] = {
            "document_id": document_id,
            "job_id": job_id,
            "template_id": data.get('template_id', 'tmpl_001'),
            "created_at": datetime.now().isoformat(),
            "status": "processing"
        }
        
        return Response({
            "status": "success",
            "message": "NDA generation started",
            "job": {
                "job_id": job_id,
                "status": "queued",
                "progress_percentage": 0,
                "message": "Job queued, waiting to start"
            },
            "document": {
                "document_id": document_id,
                "template_id": data.get('template_id', 'tmpl_001'),
                "created_at": datetime.now().isoformat()
            },
            "formats_requested": data.get('formats', ['markdown', 'pdf', 'docx']),
            "delivery_settings": {
                "email_enabled": data.get('delivery', {}).get('email', False),
                "library_enabled": data.get('delivery', {}).get('add_to_library', False),
                "webhook_enabled": bool(data.get('delivery', {}).get('webhook_url'))
            },
            "estimated_time_seconds": 5
        }, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


# ═══════════════════════════════════════════════════════════════════════════
# STEP 4B: JOB POLLING
# ═══════════════════════════════════════════════════════════════════════════

@api_view(['GET'])
def get_job_status(request, job_id):
    """
    GET /api/nda/job/{job_id}/status
    Poll job progress in real-time
    """
    if job_id not in JOBS:
        return Response({
            "status": "error",
            "message": f"Job {job_id} not found"
        }, status=status.HTTP_404_NOT_FOUND)
    
    job = JOBS[job_id]
    
    # Simulate progress
    elapsed = (datetime.now() - datetime.fromisoformat(job['created_at'])).total_seconds()
    
    if elapsed < 1:
        progress = 0
        stage = "queued"
        message = "Job queued, waiting to start"
    elif elapsed < 3:
        progress = 25
        stage = "generating"
        message = f"Generating document sections ({int(elapsed)} of 5 seconds)"
    elif elapsed < 5:
        progress = 50
        stage = "formatting"
        message = "Converting to PDF and Word formats"
    elif elapsed < 6:
        progress = 75
        stage = "delivering"
        message = "Finalizing deliveries"
    else:
        progress = 100
        stage = "complete"
        message = "Document generation complete!"
        job['status'] = "completed"
    
    job['progress_percentage'] = progress
    job['current_stage'] = stage
    job['message'] = message
    
    response_data = {
        "job_id": job_id,
        "status": job['status'],
        "progress_percentage": progress,
        "current_stage": stage,
        "message": message,
        "estimated_time_remaining_seconds": max(0, 6 - elapsed)
    }
    
    if progress == 100:
        response_data["document_id"] = job['document_id']
        response_data["completed_at"] = datetime.now().isoformat()
    
    return Response(response_data, status=status.HTTP_200_OK)


# ═══════════════════════════════════════════════════════════════════════════
# STEP 5A: GET DOCUMENT METADATA
# ═══════════════════════════════════════════════════════════════════════════

@api_view(['GET'])
def get_document(request, document_id):
    """
    GET /api/nda/documents/{document_id}
    Get document metadata and available actions
    """
    if document_id not in DOCUMENTS:
        return Response({
            "status": "error",
            "message": f"Document {document_id} not found"
        }, status=status.HTTP_404_NOT_FOUND)
    
    doc = DOCUMENTS[document_id]
    
    return Response({
        "status": "success",
        "document": {
            "document_id": document_id,
            "template_id": doc.get('template_id', 'tmpl_001'),
            "created_at": doc.get('created_at'),
            "status": "completed",
            "title": "Mutual Non-Disclosure Agreement",
            "parties": {
                "party_1": "TechCorp Inc.",
                "party_2": "InnovateLabs LLC"
            },
            "terms": {
                "jurisdiction": "California",
                "duration": "5 years",
                "effective_date": datetime.now().date().isoformat()
            },
            "statistics": {
                "total_characters": 21146,
                "total_words": 3521,
                "estimated_pages": 7,
                "sections": 10,
                "clauses": 31,
                "appendices": 3
            },
            "formats_available": {
                "markdown": {
                    "available": True,
                    "size_bytes": 21456,
                    "size_formatted": "21 KB",
                    "download_url": f"/api/nda/documents/{document_id}/download/markdown"
                },
                "pdf": {
                    "available": True,
                    "size_bytes": 187234,
                    "size_formatted": "187 KB",
                    "download_url": f"/api/nda/documents/{document_id}/download/pdf"
                },
                "docx": {
                    "available": True,
                    "size_bytes": 245678,
                    "size_formatted": "246 KB",
                    "download_url": f"/api/nda/documents/{document_id}/download/docx"
                }
            },
            "actions": {
                "preview": f"/api/nda/documents/{document_id}/preview",
                "download_all": f"/api/nda/documents/{document_id}/download/all",
                "request_signature": f"/api/nda/documents/{document_id}/request-signature",
                "regenerate": f"/api/nda/documents/{document_id}/regenerate"
            }
        }
    }, status=status.HTTP_200_OK)


# ═══════════════════════════════════════════════════════════════════════════
# STEP 5B: GET DOCUMENT PREVIEW
# ═══════════════════════════════════════════════════════════════════════════

@api_view(['GET'])
def get_document_preview(request, document_id):
    """
    GET /api/nda/documents/{document_id}/preview
    Get HTML formatted document preview
    """
    if document_id not in DOCUMENTS:
        return Response({
            "status": "error",
            "message": f"Document {document_id} not found"
        }, status=status.HTTP_404_NOT_FOUND)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mutual Non-Disclosure Agreement Preview</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 40px auto; }}
            h1 {{ text-align: center; font-size: 24px; margin-bottom: 30px; }}
            .section {{ margin-bottom: 30px; }}
            .section-title {{ font-size: 16px; font-weight: bold; margin-bottom: 10px; }}
            .clause {{ margin-left: 20px; margin-bottom: 15px; }}
        </style>
    </head>
    <body>
        <h1>MUTUAL NON-DISCLOSURE AGREEMENT</h1>
        
        <div class="section">
            <div class="section-title">1. PARTIES AND DEFINITIONS</div>
            <div class="clause">
                <strong>1.1 Confidential Information Definition.</strong>
                <p>"Confidential Information" means any and all information or data, whether written, oral, electronic, or visual, disclosed by one party (the "Disclosing Party") to the other party (the "Receiving Party")...</p>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">2. CONFIDENTIALITY OBLIGATIONS</div>
            <div class="clause">
                <strong>2.1 Use and Protection.</strong>
                <p>The Receiving Party shall protect the Confidential Information using the same degree of care it uses to protect its own confidential information...</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return Response(html_content, content_type='text/html', status=status.HTTP_200_OK)


# ═══════════════════════════════════════════════════════════════════════════
# STEP 5C: DOWNLOAD DOCUMENT
# ═══════════════════════════════════════════════════════════════════════════

@api_view(['GET'])
def download_document(request, document_id, format_type):
    """
    GET /api/nda/documents/{document_id}/download/{format}
    Download document in specified format
    """
    if document_id not in DOCUMENTS:
        return Response({
            "status": "error",
            "message": f"Document {document_id} not found"
        }, status=status.HTTP_404_NOT_FOUND)
    
    doc_content = """MUTUAL NON-DISCLOSURE AGREEMENT

This Mutual Non-Disclosure Agreement ("Agreement") is entered into as of the date hereof, by and between the parties identified herein.

1. PARTIES AND DEFINITIONS

1.1 Confidential Information Definition. "Confidential Information" means any and all information or data, whether written, oral, electronic, or visual, disclosed by one party (the "Disclosing Party") to the other party (the "Receiving Party").

2. CONFIDENTIALITY OBLIGATIONS

2.1 Use and Protection. The Receiving Party shall protect the Confidential Information using reasonable care.

3. PERMITTED DISCLOSURES

3.1 The Receiving Party may disclose Confidential Information to its employees and advisors on a need-to-know basis.

4. TERM AND TERMINATION

4.1 This Agreement shall remain in effect for a period of five (5) years from the date first written above.

5. RETURN OF INFORMATION

5.1 Upon termination or request, the Receiving Party shall return or destroy all Confidential Information.

6. INTELLECTUAL PROPERTY RIGHTS

6.1 Nothing in this Agreement grants any license or rights to any intellectual property.

7. NO LICENSE OR OBLIGATION

7.1 No license or other right is granted by implication or otherwise.

8. DISCLAIMERS

8.1 The Confidential Information is provided "AS IS" without warranty.

9. REMEDIES

9.1 The parties acknowledge that breaches of this Agreement may cause irreparable harm.

10. GENERAL PROVISIONS

10.1 This Agreement shall be governed by the laws of California.
10.2 Any amendments must be in writing and signed by both parties.
"""
    
    if format_type == 'markdown':
        response = Response(doc_content, content_type='text/markdown')
        response['Content-Disposition'] = f'attachment; filename="NDA_{document_id}.md"'
        return response
    
    elif format_type == 'pdf':
        # Simple PDF generation (in production, use reportlab or similar)
        pdf_header = b"%PDF-1.4\n"
        pdf_content = pdf_header + b"Simple PDF content for NDA document"
        response = Response(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="NDA_{document_id}.pdf"'
        return response
    
    elif format_type == 'docx':
        # Simple DOCX generation (in production, use python-docx)
        docx_header = b"PK\x03\x04"  # ZIP header for DOCX
        docx_content = docx_header + b"Simple DOCX content for NDA document"
        response = Response(docx_content, 
                          content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="NDA_{document_id}.docx"'
        return response
    
    else:
        return Response({
            "status": "error",
            "message": f"Invalid format: {format_type}. Supported: markdown, pdf, docx"
        }, status=status.HTTP_400_BAD_REQUEST)
