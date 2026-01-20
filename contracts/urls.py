"""
URL configuration for contracts app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .generation_views import (
    ContractTemplateViewSet,
    ClauseViewSet,
    ContractViewSet,
    GenerationJobViewSet,
)
from .contract_generation_views import (
    create_contract_endpoint,
    get_contract_fields_endpoint,
    get_contract_templates_endpoint,
    get_contract_content_endpoint,
    download_contract_endpoint,
    get_contract_details_endpoint,
    send_to_signnow_endpoint,
    webhook_signnow_signed_endpoint,
)

router = DefaultRouter()
router.register(r'contract-templates', ContractTemplateViewSet, basename='contract-template')
router.register(r'clauses', ClauseViewSet, basename='clause')
router.register(r'contracts', ContractViewSet, basename='contract')
router.register(r'generation-jobs', GenerationJobViewSet, basename='generation-job')

urlpatterns = [
    path('', include(router.urls)),
    # Contract generation endpoints
    path('create/', create_contract_endpoint, name='create-contract'),
    path('fields/', get_contract_fields_endpoint, name='contract-fields'),
    path('templates/', get_contract_templates_endpoint, name='supported-templates'),
    path('content/', get_contract_content_endpoint, name='contract-content'),
    path('download/', download_contract_endpoint, name='download-contract'),
    path('details/', get_contract_details_endpoint, name='contract-details'),
    # SignNow integration endpoints
    path('send-to-signnow/', send_to_signnow_endpoint, name='send-to-signnow'),
    path('webhook/signnow/', webhook_signnow_signed_endpoint, name='webhook-signnow'),
]
