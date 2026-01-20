"""
NDA API URL Configuration
Maps all endpoints for the 5-step NDA workflow
Date: January 18, 2026
"""

from django.urls import path
from . import views

app_name = 'nda'

urlpatterns = [
    # STEP 1: Template Selection
    path('templates/', views.get_templates, name='get_templates'),
    
    # STEP 2: Clause Inspection
    path('templates/<str:template_id>/clauses/', views.get_template_clauses, name='get_clauses'),
    
    # STEP 3: Preview Generation
    path('generate/preview/', views.generate_preview, name='generate_preview'),
    
    # STEP 4: Async Generation
    path('generate/', views.generate_document, name='generate_document'),
    
    # STEP 4B: Job Polling
    path('job/<str:job_id>/status/', views.get_job_status, name='get_job_status'),
    
    # STEP 5A: Get Document
    path('documents/<str:document_id>/', views.get_document, name='get_document'),
    
    # STEP 5B: Document Preview
    path('documents/<str:document_id>/preview/', views.get_document_preview, name='get_document_preview'),
    
    # STEP 5C: Download Document
    path('documents/<str:document_id>/download/<str:format_type>/', views.download_document, name='download_document'),
]
