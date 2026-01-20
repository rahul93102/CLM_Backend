"""
NDA GENERATION - Complete REST API Workflow
Demonstrates all steps from template selection to final document delivery
"""

# ==============================================================================
# STEP 1: TEMPLATE SELECTION - GET /api/nda/templates
# ==============================================================================

STEP_1_GET_TEMPLATES = """
╔════════════════════════════════════════════════════════════════════════════╗
║                          STEP 1: TEMPLATE SELECTION                        ║
║                      GET /api/nda/templates                                ║
╚════════════════════════════════════════════════════════════════════════════╝

REQUEST:
--------
GET /api/nda/templates
Host: api.clm-backend.com
Authorization: Bearer {token}
Accept: application/json


RESPONSE: 200 OK
-----------------
{
  "status": "success",
  "data": {
    "templates": [
      {
        "id": "tmpl_001",
        "name": "Standard Mutual NDA",
        "description": "Mutual Non-Disclosure Agreement for equal parties",
        "jurisdiction": "California",
        "default_duration_years": 5,
        "sections": 10,
        "appendices": 3,
        "character_count": 21146,
        "estimated_pages": 8,
        "tags": ["mutual", "california", "standard"],
        "use_cases": ["partnership", "collaboration", "technology"],
        "preview_url": "/api/nda/templates/tmpl_001/preview",
        "created_date": "2026-01-18",
        "last_updated": "2026-01-18"
      },
      {
        "id": "tmpl_002",
        "name": "Unilateral NDA - Discloser",
        "description": "One-way NDA where discloser protects information",
        "jurisdiction": "California",
        "default_duration_years": 3,
        "sections": 10,
        "appendices": 2,
        "character_count": 18541,
        "estimated_pages": 7,
        "tags": ["unilateral", "discloser", "california"],
        "use_cases": ["consulting", "vendor-evaluation", "job-interviews"],
        "preview_url": "/api/nda/templates/tmpl_002/preview",
        "created_date": "2026-01-18",
        "last_updated": "2026-01-18"
      },
      {
        "id": "tmpl_003",
        "name": "Unilateral NDA - Recipient",
        "description": "One-way NDA where recipient protects information",
        "jurisdiction": "California",
        "default_duration_years": 3,
        "sections": 10,
        "appendices": 2,
        "character_count": 18541,
        "estimated_pages": 7,
        "tags": ["unilateral", "recipient", "california"],
        "use_cases": ["supplier-evaluation", "candidate-briefing"],
        "preview_url": "/api/nda/templates/tmpl_003/preview",
        "created_date": "2026-01-18",
        "last_updated": "2026-01-18"
      },
      {
        "id": "tmpl_004",
        "name": "Multi-Party NDA",
        "description": "NDA involving multiple parties with confidentiality obligations",
        "jurisdiction": "New York",
        "default_duration_years": 7,
        "sections": 12,
        "appendices": 4,
        "character_count": 25000,
        "estimated_pages": 10,
        "tags": ["multiparty", "complex", "newyork"],
        "use_cases": ["consortium", "joint-venture", "merger"],
        "preview_url": "/api/nda/templates/tmpl_004/preview",
        "created_date": "2026-01-18",
        "last_updated": "2026-01-18"
      },
      {
        "id": "tmpl_005",
        "name": "Employee NDA",
        "description": "NDA for employment and contractor relationships",
        "jurisdiction": "California",
        "default_duration_years": 5,
        "sections": 9,
        "appendices": 2,
        "character_count": 15000,
        "estimated_pages": 6,
        "tags": ["employment", "contractor", "california"],
        "use_cases": ["new-hire", "contractor-agreement"],
        "preview_url": "/api/nda/templates/tmpl_005/preview",
        "created_date": "2026-01-18",
        "last_updated": "2026-01-18"
      }
    ],
    "total_templates": 5,
    "supported_jurisdictions": [
      "California",
      "New York",
      "Texas",
      "Federal",
      "United Kingdom",
      "Canada"
    ],
    "duration_options": [3, 5, 7, 10],
    "filters_available": {
      "jurisdiction": ["CA", "NY", "TX", "FED", "UK", "CA"],
      "party_type": ["mutual", "unilateral", "multiparty"],
      "use_case": ["partnership", "employment", "consulting"]
    }
  },
  "timestamp": "2026-01-18T15:30:00Z"
}
"""

# ==============================================================================
# STEP 2: GET TEMPLATE DETAILS & CLAUSES - GET /api/nda/templates/{id}/clauses
# ==============================================================================

STEP_2_GET_CLAUSES = """
╔════════════════════════════════════════════════════════════════════════════╗
║                       STEP 2: TEMPLATE CLAUSES & DETAILS                   ║
║                    GET /api/nda/templates/tmpl_001/clauses                 ║
╚════════════════════════════════════════════════════════════════════════════╝

REQUEST:
--------
GET /api/nda/templates/tmpl_001/clauses?include_text=true&format=detailed
Host: api.clm-backend.com
Authorization: Bearer {token}
Accept: application/json


RESPONSE: 200 OK
-----------------
{
  "status": "success",
  "template": {
    "id": "tmpl_001",
    "name": "Standard Mutual NDA",
    "sections": [
      {
        "section_id": "sec_001",
        "section_number": 1,
        "title": "Definitions and Interpretation",
        "mandatory": true,
        "clauses": [
          {
            "clause_id": "cl_001_001",
            "name": "Confidential Information",
            "description": "Definition of what constitutes confidential information",
            "customizable": true,
            "default_text": "All non-public information, technical data, know-how, research...",
            "variables": ["parties", "effective_date"],
            "preview_length": 250
          },
          {
            "clause_id": "cl_001_002",
            "name": "Exceptions",
            "description": "Standard exceptions to confidentiality (public domain, etc)",
            "customizable": false,
            "exceptions_count": 6,
            "exceptions": [
              "Information already public",
              "Third-party information",
              "Independently developed",
              "Prior knowledge",
              "Reverse engineering",
              "Legally required disclosure"
            ]
          },
          {
            "clause_id": "cl_001_003",
            "name": "Permitted Use",
            "description": "How information can be used",
            "customizable": true,
            "default_use_cases": ["evaluation", "partnership", "collaboration"],
            "variables": ["use_case"]
          }
        ]
      },
      {
        "section_id": "sec_002",
        "section_number": 2,
        "title": "Confidentiality Obligations",
        "mandatory": true,
        "clauses": [
          {
            "clause_id": "cl_002_001",
            "name": "Duty of Confidentiality",
            "description": "Standard of care for protecting information",
            "customizable": true,
            "standard_of_care": "commercially_reasonable",
            "variables": ["care_level"]
          },
          {
            "clause_id": "cl_002_002",
            "name": "Security Measures",
            "description": "Required security standards",
            "customizable": true,
            "includes": [
              "Physical security",
              "Encryption (TLS 1.2+, AES-256)",
              "Access controls",
              "Multi-factor authentication",
              "Security audits",
              "Incident response"
            ],
            "variables": ["security_level"]
          },
          {
            "clause_id": "cl_002_003",
            "name": "Return or Destruction",
            "description": "Procedures for returning information",
            "customizable": false,
            "options": ["return", "destruction", "legal_retention"]
          }
        ]
      },
      {
        "section_id": "sec_003",
        "section_number": 3,
        "title": "Permitted Disclosures",
        "mandatory": true,
        "clauses": [
          {
            "clause_id": "cl_003_001",
            "name": "Legally Compelled Disclosure",
            "description": "Handling of court orders and legal requirements",
            "customizable": false,
            "includes_notice_requirements": true,
            "notice_period_days": 10
          },
          {
            "clause_id": "cl_003_002",
            "name": "Employee Disclosure",
            "description": "Allowing disclosure to employees with confidentiality obligations",
            "customizable": true,
            "variables": ["need_to_know", "confidentiality_binding"]
          }
        ]
      },
      {
        "section_id": "sec_004",
        "section_number": 4,
        "title": "Intellectual Property Rights",
        "mandatory": true,
        "clauses": [
          {
            "clause_id": "cl_004_001",
            "name": "Ownership",
            "description": "IP ownership preservation",
            "customizable": false
          },
          {
            "clause_id": "cl_004_002",
            "name": "No License Grant",
            "description": "Clarification that no licenses are granted",
            "customizable": false
          },
          {
            "clause_id": "cl_004_003",
            "name": "Feedback License",
            "description": "Clause allowing use of feedback provided",
            "customizable": true,
            "variables": ["feedback_scope"]
          },
          {
            "clause_id": "cl_004_004",
            "name": "Pre-existing IP",
            "description": "Protection of pre-existing intellectual property",
            "customizable": false
          }
        ]
      },
      {
        "section_id": "sec_005",
        "section_number": 5,
        "title": "Representations & Warranties",
        "mandatory": true,
        "clauses": [
          {
            "clause_id": "cl_005_001",
            "name": "Authority",
            "description": "Authority to enter into agreement",
            "customizable": false
          },
          {
            "clause_id": "cl_005_002",
            "name": "No Conflict",
            "description": "No conflict with other obligations",
            "customizable": false
          },
          {
            "clause_id": "cl_005_003",
            "name": "Ownership Warranty",
            "description": "Warranty that information is owned by discloser",
            "customizable": true,
            "variables": ["warranty_scope"]
          },
          {
            "clause_id": "cl_005_004",
            "name": "Disclaimer",
            "description": "AS-IS disclaimer for information",
            "customizable": false
          }
        ]
      },
      {
        "section_id": "sec_006",
        "section_number": 6,
        "title": "Limitations on Liability",
        "mandatory": true,
        "clauses": [
          {
            "clause_id": "cl_006_001",
            "name": "Warranty Disclaimer",
            "description": "Complete warranty disclaimer",
            "customizable": false
          },
          {
            "clause_id": "cl_006_002",
            "name": "Consequential Damages",
            "description": "Exclusion of indirect damages",
            "customizable": false
          },
          {
            "clause_id": "cl_006_003",
            "name": "Direct Damages Cap",
            "description": "Cap on direct damages",
            "customizable": true,
            "default_cap_amount": 100,
            "variables": ["damage_cap", "damage_cap_type"]
          }
        ]
      },
      {
        "section_id": "sec_007",
        "section_number": 7,
        "title": "Term and Termination",
        "mandatory": true,
        "clauses": [
          {
            "clause_id": "cl_007_001",
            "name": "Term Duration",
            "description": "Duration of the agreement",
            "customizable": true,
            "default_duration": 5,
            "duration_options": [3, 5, 7, 10, 0],
            "variables": ["duration_years"]
          },
          {
            "clause_id": "cl_007_002",
            "name": "Termination for Cause",
            "description": "Material breach termination with cure period",
            "customizable": true,
            "default_cure_days": 30,
            "variables": ["cure_period_days"]
          },
          {
            "clause_id": "cl_007_003",
            "name": "Termination for Convenience",
            "description": "Either party can terminate with notice",
            "customizable": true,
            "default_notice_days": 30,
            "variables": ["notice_period_days"]
          },
          {
            "clause_id": "cl_007_004",
            "name": "Survival",
            "description": "Obligations survive termination",
            "customizable": true,
            "default_survival_years": 5,
            "variables": ["survival_years"]
          }
        ]
      },
      {
        "section_id": "sec_008",
        "section_number": 8,
        "title": "Remedies and Equitable Relief",
        "mandatory": true,
        "clauses": [
          {
            "clause_id": "cl_008_001",
            "name": "Equitable Relief",
            "description": "Availability of injunctive relief",
            "customizable": false
          },
          {
            "clause_id": "cl_008_002",
            "name": "No Bond Requirement",
            "description": "No bond required for injunctions",
            "customizable": false
          },
          {
            "clause_id": "cl_008_003",
            "name": "Cumulative Remedies",
            "description": "Remedies are cumulative, not exclusive",
            "customizable": false
          }
        ]
      },
      {
        "section_id": "sec_009",
        "section_number": 9,
        "title": "General Provisions",
        "mandatory": true,
        "clauses": [
          {
            "clause_id": "cl_009_001",
            "name": "Entire Agreement",
            "description": "This agreement is the entire agreement",
            "customizable": false
          },
          {
            "clause_id": "cl_009_002",
            "name": "Amendments",
            "description": "How agreement can be modified",
            "customizable": false
          },
          {
            "clause_id": "cl_009_003",
            "name": "Severability",
            "description": "Invalid provisions can be reformed",
            "customizable": false
          },
          {
            "clause_id": "cl_009_004",
            "name": "Governing Law",
            "description": "Jurisdiction-specific law applies",
            "customizable": true,
            "jurisdiction_options": ["CA", "NY", "TX", "FED", "UK", "CA"],
            "variables": ["jurisdiction"]
          },
          {
            "clause_id": "cl_009_005",
            "name": "Notices",
            "description": "How notices must be delivered",
            "customizable": false
          },
          {
            "clause_id": "cl_009_006",
            "name": "Electronic Signatures",
            "description": "Support for electronic signatures",
            "customizable": false
          }
        ]
      },
      {
        "section_id": "sec_010",
        "section_number": 10,
        "title": "Special Provisions",
        "mandatory": false,
        "clauses": [
          {
            "clause_id": "cl_010_001",
            "name": "Third-Party Information",
            "description": "Handling of third-party proprietary information",
            "customizable": true,
            "variables": ["third_party_handling"]
          },
          {
            "clause_id": "cl_010_002",
            "name": "Competition",
            "description": "Clarification that NDA doesn't prevent competition",
            "customizable": false
          },
          {
            "clause_id": "cl_010_003",
            "name": "Cooperation",
            "description": "Parties agree to cooperate in good faith",
            "customizable": true,
            "variables": ["cooperation_scope"]
          }
        ]
      }
    ],
    "appendices": [
      {
        "appendix_id": "app_001",
        "name": "Appendix A: Confidential Information Schedule",
        "description": "Table for listing specific confidential items",
        "mandatory": false,
        "customizable": true,
        "format": "table",
        "columns": ["Item No.", "Description", "Classification", "Date Disclosed", "Format"]
      },
      {
        "appendix_id": "app_002",
        "name": "Appendix B: Authorized Recipients",
        "description": "List of employees/contractors authorized to receive information",
        "mandatory": false,
        "customizable": true,
        "format": "table",
        "columns": ["Name", "Title", "Department", "Email", "Phone"]
      },
      {
        "appendix_id": "app_003",
        "name": "Appendix C: Data Security Requirements",
        "description": "Detailed security measures and compliance requirements",
        "mandatory": false,
        "customizable": true,
        "sections": [
          "Physical Security",
          "Electronic Security",
          "Personnel Security",
          "Audit and Compliance"
        ]
      }
    ],
    "customizable_variables": {
      "party_info": [
        "disclosing_party_legal_name",
        "disclosing_party_entity_type",
        "disclosing_party_state",
        "disclosing_party_address",
        "receiving_party_legal_name",
        "receiving_party_entity_type",
        "receiving_party_state",
        "receiving_party_address"
      ],
      "agreement_terms": [
        "effective_date",
        "jurisdiction",
        "duration_years",
        "cure_period_days",
        "survival_years",
        "standard_of_care"
      ],
      "optional_terms": [
        "security_level",
        "damage_cap",
        "use_cases",
        "special_provisions"
      ]
    }
  },
  "timestamp": "2026-01-18T15:30:30Z"
}
"""

# ==============================================================================
# STEP 3: VARIABLE INPUT - POST /api/nda/generate/preview
# ==============================================================================

STEP_3_VARIABLE_INPUT = """
╔════════════════════════════════════════════════════════════════════════════╗
║                          STEP 3: VARIABLE INPUT                            ║
║                        POST /api/nda/generate/preview                      ║
╚════════════════════════════════════════════════════════════════════════════╝

REQUEST:
--------
POST /api/nda/generate/preview
Host: api.clm-backend.com
Authorization: Bearer {token}
Content-Type: application/json

{
  "template_id": "tmpl_001",
  "variables": {
    "party_info": {
      "disclosing_party": {
        "legal_name": "TechCorp Innovations Inc.",
        "entity_type": "Corporation",
        "state_of_incorporation": "Delaware",
        "address": "123 Innovation Drive, San Francisco, CA 94102",
        "contact_name": "John Smith",
        "contact_title": "General Counsel",
        "contact_email": "john.smith@techcorp.com",
        "contact_phone": "+1-415-555-0100"
      },
      "receiving_party": {
        "legal_name": "Strategic Partners LLC",
        "entity_type": "Limited Liability Company",
        "state_of_incorporation": "California",
        "address": "456 Business Boulevard, Los Angeles, CA 90001",
        "contact_name": "Jane Doe",
        "contact_title": "VP Business Development",
        "contact_email": "jane.doe@strategicpartners.com",
        "contact_phone": "+1-310-555-0200"
      }
    },
    "agreement_terms": {
      "effective_date": "2026-01-20",
      "jurisdiction": "California",
      "duration_years": 5,
      "cure_period_days": 30,
      "survival_years": 5,
      "standard_of_care": "commercially_reasonable"
    },
    "optional_terms": {
      "security_level": "enterprise",
      "damage_cap": "100",
      "damage_cap_type": "dollars",
      "use_cases": ["partnership", "technology-evaluation", "collaboration"],
      "special_provisions": [
        "Third-party information will be treated with same confidentiality",
        "Cooperation in good faith for implementation"
      ]
    },
    "appendices": {
      "include_confidential_schedule": true,
      "include_recipients_list": true,
      "include_security_requirements": true
    }
  }
}


RESPONSE: 200 OK (PREVIEW - NOT FINAL)
--------------------------------------
{
  "status": "success",
  "action": "preview_generated",
  "preview": {
    "document_id": "doc_preview_001",
    "template_id": "tmpl_001",
    "status": "preview",
    "metadata": {
      "title": "Non-Disclosure Agreement (NDA)",
      "effective_date": "January 20, 2026",
      "disclosing_party": "TechCorp Innovations Inc.",
      "receiving_party": "Strategic Partners LLC",
      "jurisdiction": "California",
      "duration_years": 5,
      "total_sections": 10,
      "total_appendices": 3,
      "character_count": 21146,
      "estimated_pages": 8,
      "reading_time_minutes": 18
    },
    "content_preview": {
      "title_page": {
        "title": "NON-DISCLOSURE AGREEMENT (NDA)",
        "subtitle": "This Non-Disclosure Agreement ('Agreement') is entered into effective as of January 20, 2026 ('Effective Date')",
        "parties": {
          "disclosing": "TechCorp Innovations Inc., a Corporation organized and existing under the laws of Delaware, with principal place of business at 123 Innovation Drive, San Francisco, CA 94102 ('Disclosing Party')",
          "receiving": "Strategic Partners LLC, a Limited Liability Company organized and existing under the laws of California, with principal place of business at 456 Business Boulevard, Los Angeles, CA 90001 ('Receiving Party')"
        }
      },
      "sections_preview": [
        {
          "section": 1,
          "title": "Definitions and Interpretation",
          "preview_text": "All non-public information, technical data, know-how, research, product plans... (showing first 150 characters of section)",
          "preview_chars": 150
        },
        {
          "section": 2,
          "title": "Confidentiality Obligations",
          "preview_text": "The Receiving Party shall maintain the confidentiality of all Confidential Information... (showing first 150 characters)",
          "preview_chars": 150
        }
      ],
      "signature_section": {
        "title": "SIGNATURES",
        "format": "Professional signature blocks for both parties",
        "spaces_for_signatures": 2
      }
    },
    "variable_summary": {
      "parties": {
        "disclosing_party_name": "TechCorp Innovations Inc.",
        "receiving_party_name": "Strategic Partners LLC",
        "jurisdiction": "California",
        "entity_types_correct": true
      },
      "terms": {
        "duration": "5 years",
        "cure_period": "30 days",
        "survival": "5 years",
        "care_standard": "Commercially Reasonable"
      },
      "security": {
        "encryption_standard": "TLS 1.2+, AES-256",
        "mfa_required": true,
        "audit_frequency": "Quarterly"
      },
      "appendices_to_include": 3
    },
    "validation": {
      "all_required_variables_provided": true,
      "party_names_present": true,
      "jurisdiction_valid": true,
      "duration_within_limits": true,
      "security_standards_comprehensive": true,
      "ready_for_generation": true,
      "validation_warnings": []
    },
    "next_actions": [
      {
        "action": "preview_approved",
        "method": "POST",
        "endpoint": "/api/nda/generate",
        "description": "Proceed with final document generation"
      },
      {
        "action": "modify_variables",
        "method": "POST",
        "endpoint": "/api/nda/generate/preview",
        "description": "Adjust any variables and regenerate preview"
      },
      {
        "action": "cancel",
        "method": "DELETE",
        "endpoint": "/api/nda/preview/{preview_id}",
        "description": "Discard preview and start over"
      }
    ]
  },
  "expires_in_seconds": 300,
  "timestamp": "2026-01-18T15:31:00Z"
}
"""

# ==============================================================================
# STEP 4: ASYNC GENERATION - POST /api/nda/generate (with job tracking)
# ==============================================================================

STEP_4_ASYNC_GENERATION = """
╔════════════════════════════════════════════════════════════════════════════╗
║                          STEP 4: ASYNC GENERATION                          ║
║                         POST /api/nda/generate                             ║
╚════════════════════════════════════════════════════════════════════════════╝

REQUEST:
--------
POST /api/nda/generate
Host: api.clm-backend.com
Authorization: Bearer {token}
Content-Type: application/json

{
  "preview_id": "doc_preview_001",
  "async": true,
  "format_options": {
    "output_formats": ["markdown", "pdf"],
    "include_cover_page": true,
    "include_watermark": false,
    "page_headers": true,
    "page_footers": true
  },
  "delivery_options": {
    "send_to_email": "john.smith@techcorp.com",
    "add_to_document_library": true,
    "webhook_url": "https://webhook.yourapp.com/nda-generated"
  }
}


RESPONSE: 202 ACCEPTED (ASYNC JOB CREATED)
-------------------------------------------
{
  "status": "accepted",
  "job": {
    "job_id": "job_nda_20260118_001",
    "preview_id": "doc_preview_001",
    "status": "queued",
    "progress": {
      "stage": "queued",
      "percentage": 0,
      "message": "Waiting to begin generation process"
    },
    "estimated_completion_time": 5,
    "start_time": null,
    "completion_time": null,
    "created_at": "2026-01-18T15:31:30Z",
    "document_details": {
      "parties": "TechCorp Innovations Inc. vs Strategic Partners LLC",
      "jurisdiction": "California",
      "duration": "5 years"
    },
    "format_options": {
      "output_formats": ["markdown", "pdf"],
      "includes": ["cover_page", "page_headers", "page_footers"]
    },
    "polling_urls": {
      "status_check": "/api/nda/generate/job/job_nda_20260118_001/status",
      "webhook": "https://webhook.yourapp.com/nda-generated"
    }
  },
  "actions": {
    "check_status": {
      "method": "GET",
      "endpoint": "/api/nda/generate/job/job_nda_20260118_001/status",
      "interval_seconds": 2
    },
    "cancel_job": {
      "method": "DELETE",
      "endpoint": "/api/nda/generate/job/job_nda_20260118_001"
    }
  },
  "timestamp": "2026-01-18T15:31:30Z"
}


────────────────────────────────────────────────────────────────────────────


POLLING STATUS (Every 2 seconds):
──────────────────────────────────

GET /api/nda/generate/job/job_nda_20260118_001/status
Host: api.clm-backend.com
Authorization: Bearer {token}
Accept: application/json


RESPONSE 1 (After 1 second):
-
{
  "status": "in_progress",
  "job_id": "job_nda_20260118_001",
  "progress": {
    "stage": "generating_content",
    "percentage": 25,
    "message": "Generating document sections (2/10 complete)"
  },
  "elapsed_time_seconds": 1,
  "estimated_remaining_seconds": 3,
  "timestamp": "2026-01-18T15:31:31Z"
}


RESPONSE 2 (After 3 seconds):
-
{
  "status": "in_progress",
  "job_id": "job_nda_20260118_001",
  "progress": {
    "stage": "formatting",
    "percentage": 75,
    "message": "Formatting and applying security standards"
  },
  "elapsed_time_seconds": 3,
  "estimated_remaining_seconds": 1,
  "timestamp": "2026-01-18T15:31:33Z"
}


RESPONSE 3 (After 5 seconds - COMPLETE):
────────────────────────────────────────
{
  "status": "completed",
  "job_id": "job_nda_20260118_001",
  "progress": {
    "stage": "completed",
    "percentage": 100,
    "message": "Document generation completed successfully"
  },
  "elapsed_time_seconds": 5,
  "completed_at": "2026-01-18T15:31:35Z",
  "documents_generated": [
    {
      "format": "markdown",
      "filename": "TechCorp-StrategicPartners-NDA-2026-01-20.md",
      "size_bytes": 21146,
      "download_url": "/api/nda/download/doc_20260118_001/markdown"
    },
    {
      "format": "pdf",
      "filename": "TechCorp-StrategicPartners-NDA-2026-01-20.pdf",
      "size_bytes": 187234,
      "download_url": "/api/nda/download/doc_20260118_001/pdf"
    }
  ],
  "delivery_status": {
    "email_sent": {
      "status": "sent",
      "recipient": "john.smith@techcorp.com",
      "sent_at": "2026-01-18T15:31:35Z"
    },
    "document_library": {
      "status": "added",
      "document_id": "doc_20260118_001",
      "library_path": "/documents/agreements/nda/TechCorp-StrategicPartners-NDA-2026-01-20"
    },
    "webhook": {
      "status": "sent",
      "endpoint": "https://webhook.yourapp.com/nda-generated",
      "sent_at": "2026-01-18T15:31:35Z"
    }
  },
  "document_metadata": {
    "document_id": "doc_20260118_001",
    "template_id": "tmpl_001",
    "title": "Non-Disclosure Agreement (NDA)",
    "parties": {
      "disclosing": "TechCorp Innovations Inc.",
      "receiving": "Strategic Partners LLC"
    },
    "jurisdiction": "California",
    "effective_date": "2026-01-20",
    "duration_years": 5,
    "character_count": 21146,
    "page_count": 8,
    "sections": 10,
    "appendices": 3
  },
  "next_actions": [
    {
      "action": "download_document",
      "formats": ["markdown", "pdf"],
      "methods": ["direct_download", "email_link", "library_access"]
    },
    {
      "action": "view_document",
      "endpoint": "/api/nda/documents/doc_20260118_001/preview",
      "format": "html"
    },
    {
      "action": "request_signature",
      "endpoint": "/api/nda/documents/doc_20260118_001/request-signature",
      "providers": ["docusign", "adobe-sign"]
    },
    {
      "action": "export_document",
      "formats": ["word", "google-docs"],
      "endpoint": "/api/nda/export"
    }
  ],
  "timestamp": "2026-01-18T15:31:35Z"
}
"""

# ==============================================================================
# STEP 5: RESULT PREVIEW - GET /api/nda/documents/{id}/preview
# ==============================================================================

STEP_5_RESULT_PREVIEW = """
╔════════════════════════════════════════════════════════════════════════════╗
║                          STEP 5: RESULT PREVIEW                            ║
║                  GET /api/nda/documents/doc_20260118_001/preview           ║
╚════════════════════════════════════════════════════════════════════════════╝

REQUEST:
--------
GET /api/nda/documents/doc_20260118_001/preview?format=html&sections=1-3
Host: api.clm-backend.com
Authorization: Bearer {token}
Accept: text/html


RESPONSE: 200 OK (HTML PREVIEW)
---------------------------------
<!DOCTYPE html>
<html>
<head>
  <title>NDA Preview - TechCorp vs Strategic Partners</title>
  <meta name="document-id" content="doc_20260118_001">
  <meta name="template-id" content="tmpl_001">
  <meta name="jurisdiction" content="California">
  <style>
    body { font-family: Georgia, serif; line-height: 1.6; margin: 40px; }
    .document-header { border-bottom: 2px solid #333; padding-bottom: 20px; }
    .section { margin: 30px 0; page-break-inside: avoid; }
    .section-title { font-size: 18px; font-weight: bold; margin-top: 20px; }
    .subsection { margin-left: 20px; margin-top: 10px; }
  </style>
</head>
<body>

<div class="document-header">
  <h1>NON-DISCLOSURE AGREEMENT (NDA)</h1>
  <p><strong>This Non-Disclosure Agreement ("Agreement") is entered into effective as of 
  January 20, 2026 ("Effective Date")</strong></p>
</div>

<div class="parties">
  <p><strong>BETWEEN:</strong></p>
  <p><strong>TechCorp Innovations Inc.</strong>, a Corporation organized and existing under 
  the laws of Delaware, with principal place of business at 123 Innovation Drive, San Francisco, 
  CA 94102 ("Disclosing Party")</p>
  
  <p><strong>AND:</strong></p>
  
  <p><strong>Strategic Partners LLC</strong>, a Limited Liability Company organized and 
  existing under the laws of California, with principal place of business at 456 Business 
  Boulevard, Los Angeles, CA 90001 ("Receiving Party")</p>
</div>

<hr>

<div class="section">
  <div class="section-title">1. DEFINITIONS AND INTERPRETATION</div>
  
  <div class="subsection">
    <h4>1.1 Confidential Information</h4>
    <p>"Confidential Information" means all non-public information, technical data, know-how, 
    research, product plans, products, developments, inventions, processes, formulas, techniques, 
    designs, drawings, specifications, software code, source code, object code, documentation, 
    business plans, financial information, customer lists, supplier lists, market analysis, 
    pricing information, and any other proprietary or sensitive information, in any form or 
    medium (including oral, written, electronic, or visual), whether or not marked as confidential 
    or proprietary, that is disclosed by the Disclosing Party to the Receiving Party.</p>
  </div>
  
  <div class="subsection">
    <h4>1.2 Exceptions</h4>
    <p>Confidential Information does not include information that:</p>
    <ul>
      <li>(a) Is or becomes publicly available through no breach of this Agreement by the 
      Receiving Party;</li>
      
      <li>(b) Is rightfully received by the Receiving Party from a third party without breach 
      of any confidentiality obligation and with no obligation of secrecy toward the source;</li>
      
      <li>(c) Is independently developed by the Receiving Party without use of or reference to 
      the Confidential Information, as evidenced by written records created and maintained 
      contemporaneously during development;</li>
      
      <li>(d) Was known to the Receiving Party prior to disclosure, as evidenced by written 
      records dated prior to the date of disclosure;</li>
      
      <li>(e) Is rightfully reverse-engineered from a lawfully obtained product by the Receiving 
      Party without breach of any confidentiality obligation;</li>
      
      <li>(f) Is required to be disclosed by law, court order, regulatory requirement, or 
      governmental authority, provided the Receiving Party gives prompt written notice to the 
      Disclosing Party and cooperates in efforts to obtain protective orders.</li>
    </ul>
  </div>
  
  <div class="subsection">
    <h4>1.3 Permitted Use</h4>
    <p>"Permitted Use" means the evaluation of a potential business relationship, partnership, 
    joint development, strategic alliance, licensing opportunity, investment, acquisition, or 
    other collaborative arrangement between the parties, as mutually agreed in writing.</p>
  </div>
</div>

<div class="section">
  <div class="section-title">2. CONFIDENTIALITY OBLIGATIONS</div>
  
  <div class="subsection">
    <h4>2.1 Duty of Confidentiality</h4>
    <p>The Receiving Party agrees to:</p>
    <ul>
      <li>(a) Maintain the confidentiality of all Confidential Information using the same degree 
      of care it uses to protect its own confidential information of similar nature, but no less 
      than commercially reasonable care;</li>
      
      <li>(b) Limit access to Confidential Information to employees, contractors, and advisors 
      (including attorneys, accountants, and consultants) who have a legitimate need to know and 
      who are bound by written confidentiality obligations at least as restrictive as this 
      Agreement;</li>
      
      <li>(c) Use Confidential Information solely for the Permitted Use and not for any other 
      purpose without the prior written consent of the Disclosing Party;</li>
      
      <li>(d) Not disclose, publish, or distribute Confidential Information to any third party 
      without the prior written consent of the Disclosing Party;</li>
      
      <li>(e) Implement and maintain reasonable security measures to protect Confidential 
      Information against unauthorized access, disclosure, or use.</li>
    </ul>
  </div>
  
  <div class="subsection">
    <h4>2.2 Standard of Care</h4>
    <p>The Receiving Party shall protect Confidential Information using commercially reasonable 
    security measures appropriate to the nature of the information, including but not limited to:</p>
    <ul>
      <li>Physical security controls for documents and hardware containing Confidential Information</li>
      <li>Encryption for electronic data both in transit and at rest (TLS 1.2+, AES-256)</li>
      <li>Access controls, authentication mechanisms, and privilege restrictions</li>
      <li>Regular security audits, assessments, and vulnerability testing</li>
      <li>Training and awareness programs for authorized personnel</li>
      <li>Incident response procedures and breach notification protocols</li>
      <li>Compliance with applicable data protection laws and regulations</li>
    </ul>
  </div>
  
  <div class="subsection">
    <h4>2.3 Return or Destruction</h4>
    <p>Upon written request by the Disclosing Party, or upon termination or expiration of this 
    Agreement, the Receiving Party shall, at the Disclosing Party's election, either:</p>
    <ul>
      <li>(a) Return all Confidential Information in tangible form and certify in writing that 
      it has been returned in full; or</li>
      
      <li>(b) Destroy all Confidential Information in tangible form and certify in writing the 
      manner, date, and completeness of such destruction.</li>
    </ul>
    <p>Notwithstanding the foregoing, the Receiving Party may retain one copy of Confidential 
    Information in its legal files for compliance, archival, and record-keeping purposes, 
    subject to the confidentiality obligations herein.</p>
  </div>
</div>

<div class="section">
  <div class="section-title">3. PERMITTED DISCLOSURES</div>
  
  <div class="subsection">
    <h4>3.1 Legally Compelled Disclosure</h4>
    <p>[Content continues with complete legal text...]</p>
  </div>
  
  <!-- Additional sections preview continues... -->
</div>

<!-- Navigation -->
<div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc;">
  <p>
    <strong>Document Preview:</strong><br>
    Sections 1-3 of 10 shown | 
    <a href="/api/nda/documents/doc_20260118_001/preview?sections=4-6">View Sections 4-6</a> |
    <a href="/api/nda/documents/doc_20260118_001/preview?sections=all">View Full Document</a>
  </p>
  <p>
    <strong>Download:</strong><br>
    <a href="/api/nda/download/doc_20260118_001/markdown">Download Markdown</a> |
    <a href="/api/nda/download/doc_20260118_001/pdf">Download PDF</a> |
    <a href="/api/nda/download/doc_20260118_001/docx">Download Word</a>
  </p>
  <p>
    <strong>Actions:</strong><br>
    <a href="/api/nda/documents/doc_20260118_001/request-signature">Request Signature</a> |
    <a href="/api/nda/documents/doc_20260118_001/export">Export</a> |
    <a href="/api/nda/documents/doc_20260118_001/share">Share</a>
  </p>
</div>

</body>
</html>


────────────────────────────────────────────────────────────────────────────


METADATA RESPONSE (JSON Format):
─────────────────────────────────

GET /api/nda/documents/doc_20260118_001?format=json

{
  "status": "success",
  "document": {
    "document_id": "doc_20260118_001",
    "status": "generated",
    "created_at": "2026-01-18T15:31:35Z",
    "metadata": {
      "title": "Non-Disclosure Agreement (NDA)",
      "template_id": "tmpl_001",
      "template_name": "Standard Mutual NDA",
      "parties": {
        "disclosing": "TechCorp Innovations Inc.",
        "receiving": "Strategic Partners LLC"
      },
      "effective_date": "2026-01-20",
      "jurisdiction": "California",
      "governing_law": "California law",
      "duration_years": 5,
      "cure_period_days": 30,
      "survival_years": 5
    },
    "document_stats": {
      "total_characters": 21146,
      "total_words": 3485,
      "total_pages": 8,
      "total_sections": 10,
      "total_appendices": 3,
      "reading_time_minutes": 18,
      "estimated_signing_time_minutes": 5
    },
    "sections": [
      {
        "number": 1,
        "title": "Definitions and Interpretation",
        "subsections": 3,
        "character_count": 1850
      },
      {
        "number": 2,
        "title": "Confidentiality Obligations",
        "subsections": 3,
        "character_count": 2100
      },
      {
        "number": 3,
        "title": "Permitted Disclosures",
        "subsections": 2,
        "character_count": 1650
      }
      // ... remaining sections
    ],
    "appendices": [
      {
        "name": "Appendix A: Confidential Information Schedule",
        "type": "table",
        "rows": 0
      },
      {
        "name": "Appendix B: Authorized Recipients",
        "type": "table",
        "rows": 0
      },
      {
        "name": "Appendix C: Data Security Requirements",
        "type": "text",
        "subsections": 4
      }
    ],
    "available_formats": {
      "markdown": {
        "filename": "TechCorp-StrategicPartners-NDA-2026-01-20.md",
        "size_bytes": 21146,
        "download_url": "/api/nda/download/doc_20260118_001/markdown"
      },
      "pdf": {
        "filename": "TechCorp-StrategicPartners-NDA-2026-01-20.pdf",
        "size_bytes": 187234,
        "download_url": "/api/nda/download/doc_20260118_001/pdf"
      },
      "docx": {
        "filename": "TechCorp-StrategicPartners-NDA-2026-01-20.docx",
        "size_bytes": 245890,
        "download_url": "/api/nda/download/doc_20260118_001/docx"
      }
    },
    "actions_available": [
      {
        "action": "request_signature",
        "endpoint": "/api/nda/documents/doc_20260118_001/request-signature",
        "available_providers": ["docusign", "adobe-sign", "hellosign"]
      },
      {
        "action": "share_document",
        "endpoint": "/api/nda/documents/doc_20260118_001/share"
      },
      {
        "action": "export",
        "endpoint": "/api/nda/documents/doc_20260118_001/export",
        "available_formats": ["google-docs", "onedrive", "sharepoint"]
      },
      {
        "action": "download",
        "formats": ["markdown", "pdf", "docx"]
      },
      {
        "action": "regenerate",
        "endpoint": "/api/nda/documents/doc_20260118_001/regenerate"
      },
      {
        "action": "modify",
        "endpoint": "/api/nda/documents/doc_20260118_001/modify"
      }
    ],
    "audit_trail": {
      "created_by": "john.smith@techcorp.com",
      "created_at": "2026-01-18T15:31:35Z",
      "last_modified_at": null,
      "last_modified_by": null,
      "viewed_count": 1,
      "last_viewed_at": "2026-01-18T15:32:00Z"
    }
  },
  "timestamp": "2026-01-18T15:32:00Z"
}
"""

# ==============================================================================
# COMPLETE WORKFLOW VISUAL FLOW
# ==============================================================================

COMPLETE_WORKFLOW = """
╔════════════════════════════════════════════════════════════════════════════╗
║                   COMPLETE NDA GENERATION WORKFLOW                         ║
╚════════════════════════════════════════════════════════════════════════════╝

STEP 1: TEMPLATE SELECTION
────────────────────────────
┌─────────────────────────────────────────────────────────────┐
│  GET /api/nda/templates                                     │
│  └─ Browse available templates (5 templates shown)          │
│     ├─ Standard Mutual NDA (tmpl_001)                      │
│     ├─ Unilateral NDA - Discloser (tmpl_002)               │
│     ├─ Unilateral NDA - Recipient (tmpl_003)               │
│     ├─ Multi-Party NDA (tmpl_004)                          │
│     └─ Employee NDA (tmpl_005)                             │
│                                                             │
│  SELECT: tmpl_001 (Standard Mutual NDA)                     │
└─────────────────────────────────────────────────────────────┘
           ↓
STEP 2: VIEW TEMPLATE CLAUSES
──────────────────────────────
┌─────────────────────────────────────────────────────────────┐
│  GET /api/nda/templates/tmpl_001/clauses                   │
│  └─ Review sections and customizable clauses               │
│     ├─ Section 1: Definitions (3 clauses)                  │
│     ├─ Section 2: Confidentiality (3 clauses)              │
│     ├─ Section 3: Permitted Disclosures (2 clauses)        │
│     ├─ Section 4: IP Rights (4 clauses)                    │
│     ├─ Section 5: Representations (4 clauses)              │
│     ├─ Section 6: Liability Limits (3 clauses)             │
│     ├─ Section 7: Term & Termination (4 clauses)           │
│     ├─ Section 8: Remedies (3 clauses)                     │
│     ├─ Section 9: General Provisions (6 clauses)           │
│     ├─ Section 10: Special Provisions (3 clauses)          │
│     └─ Appendices (3 optional appendices)                  │
└─────────────────────────────────────────────────────────────┘
           ↓
STEP 3: PROVIDE VARIABLES & PREVIEW
────────────────────────────────────
┌─────────────────────────────────────────────────────────────┐
│  POST /api/nda/generate/preview                            │
│  ├─ Party Information (8 variables)                        │
│  │  ├─ Disclosing Party Details                            │
│  │  └─ Receiving Party Details                             │
│  ├─ Agreement Terms (6 variables)                          │
│  │  ├─ Effective Date: 2026-01-20                          │
│  │  ├─ Jurisdiction: California                            │
│  │  ├─ Duration: 5 years                                   │
│  │  ├─ Cure Period: 30 days                                │
│  │  ├─ Survival: 5 years                                   │
│  │  └─ Care Standard: Commercially Reasonable              │
│  └─ Optional Terms (4 variables)                           │
│     ├─ Security Level: Enterprise                          │
│     ├─ Damage Cap: $100                                    │
│     ├─ Use Cases: Partnership, Technology                  │
│     └─ Special Provisions: 2 items                         │
│                                                             │
│  ✓ PREVIEW GENERATED (expires in 5 minutes)               │
│    └─ 21,146 characters preview created                   │
│    └─ All variables validated                              │
│    └─ Ready for generation                                 │
└─────────────────────────────────────────────────────────────┘
           ↓
STEP 4: INITIATE ASYNC GENERATION
──────────────────────────────────
┌─────────────────────────────────────────────────────────────┐
│  POST /api/nda/generate (async=true)                       │
│  ├─ Output Formats: markdown, pdf                          │
│  ├─ Delivery: Email, Document Library, Webhook             │
│  └─ Response: 202 ACCEPTED                                 │
│                                                             │
│  JOB ID: job_nda_20260118_001                              │
│  STATUS: queued → in_progress → completed                  │
│                                                             │
│  POLLING (GET /api/nda/generate/job/{job_id}/status):     │
│  ├─ T+1s:  Stage: generating_content (25%)                │
│  ├─ T+3s:  Stage: formatting (75%)                        │
│  └─ T+5s:  Stage: completed (100%)                        │
│     └─ Documents Generated:                                │
│        ├─ markdown (21 KB)                                 │
│        └─ pdf (187 KB)                                     │
└─────────────────────────────────────────────────────────────┘
           ↓
STEP 5: PREVIEW & DOWNLOAD FINAL DOCUMENT
──────────────────────────────────────────
┌─────────────────────────────────────────────────────────────┐
│  GET /api/nda/documents/doc_20260118_001/preview           │
│  ├─ HTML Preview: Sections 1-3 displayed                  │
│  └─ Navigation: View more sections, full document          │
│                                                             │
│  GET /api/nda/documents/doc_20260118_001                   │
│  ├─ Document Metadata (JSON)                               │
│  ├─ Stats: 21,146 chars, 3,485 words, 8 pages            │
│  └─ Available Formats:                                     │
│     ├─ Markdown (21 KB)                                    │
│     ├─ PDF (187 KB)                                        │
│     └─ Word DOCX (245 KB)                                  │
│                                                             │
│  AVAILABLE ACTIONS:                                        │
│  ├─ Download document                                      │
│  ├─ Request signature (DocuSign, Adobe Sign)               │
│  ├─ Share with parties                                     │
│  ├─ Export to Google Docs / OneDrive                       │
│  ├─ Regenerate with changes                                │
│  └─ Modify and resubmit                                    │
└─────────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════════

TOTAL TIME: ~7 seconds (including 5-second async generation)
- Template Selection: <1 second
- Preview Generation: <1 second
- Async Generation: ~5 seconds
- Result Delivery: <1 second

API CALLS SUMMARY:
1. GET /api/nda/templates
2. GET /api/nda/templates/tmpl_001/clauses
3. POST /api/nda/generate/preview
4. POST /api/nda/generate
5. GET /api/nda/generate/job/{job_id}/status (polled 3 times)
6. GET /api/nda/documents/{doc_id}/preview
7. GET /api/nda/documents/{doc_id}

TOTAL ENDPOINTS: 5 unique endpoints + 1 polling endpoint
"""

# ==============================================================================
# PRINT ALL STEPS
# ==============================================================================

if __name__ == "__main__":
    print(STEP_1_GET_TEMPLATES)
    print("\n\n")
    print(STEP_2_GET_CLAUSES)
    print("\n\n")
    print(STEP_3_VARIABLE_INPUT)
    print("\n\n")
    print(STEP_4_ASYNC_GENERATION)
    print("\n\n")
    print(STEP_5_RESULT_PREVIEW)
    print("\n\n")
    print(COMPLETE_WORKFLOW)
