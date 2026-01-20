"""
NDA API URL Configuration
Maps all endpoints for the 5-step NDA workflow
Date: January 18, 2026
"""

from django.urls import path
from . import nda_api_views

app_name = 'nda_api'

urlpatterns = [
    # STEP 1: Template Selection
    path('templates/', nda_api_views.get_templates, name='get_templates'),
    
    # STEP 2: Clause Inspection
    path('templates/<str:template_id>/clauses/', nda_api_views.get_template_clauses, name='get_clauses'),
    
    # STEP 3: Preview Generation
    path('generate/preview/', nda_api_views.generate_preview, name='generate_preview'),
    
    # STEP 4: Async Generation
    path('generate/', nda_api_views.generate_document, name='generate_document'),
    
    # STEP 4B: Job Polling
    path('job/<str:job_id>/status/', nda_api_views.get_job_status, name='get_job_status'),
    
    # STEP 5A: Get Document
    path('documents/<str:document_id>/', nda_api_views.get_document, name='get_document'),
    
    # STEP 5B: Document Preview
    path('documents/<str:document_id>/preview/', nda_api_views.get_document_preview, name='get_document_preview'),
    
    # STEP 5C: Download Document
    path('documents/<str:document_id>/download/<str:format_type>/', nda_api_views.download_document, name='download_document'),
]
