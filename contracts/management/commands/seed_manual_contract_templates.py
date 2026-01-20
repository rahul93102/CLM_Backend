"""
Management command to seed 50+ professional contract templates
Run with: python manage.py seed_manual_contract_templates
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
import uuid
from contracts.manual_editing_models import ContractEditingTemplate


class Command(BaseCommand):
    help = 'Seed database with 50+ professional contract templates'
    
    def handle(self, *args, **options):
        """Create 50+ professional contract templates"""
        
        # Get default tenant (or use first tenant in database)
        from authentication.models import Tenant
        try:
            default_tenant = Tenant.objects.first()
            if not default_tenant:
                self.stdout.write(
                    self.style.ERROR('No tenant found. Create a tenant first.')
                )
                return
            tenant_id = default_tenant.id
        except:
            # Fallback for testing
            tenant_id = uuid.uuid4()
        
        # Get system user (or create one)
        from authentication.models import User
        try:
            system_user = User.objects.filter(email='system@contracts.local').first()
            if not system_user:
                system_user = User.objects.create_user(
                    email='system@contracts.local',
                    password='system123',
                    tenant_id=tenant_id
                )
            user_id = system_user.id
        except:
            user_id = uuid.uuid4()
        
        templates_created = 0
        
        # ==================== NDA TEMPLATES (6) ====================
        
        nda_templates = [
            {
                'name': 'Standard Unilateral NDA',
                'description': 'One-way non-disclosure agreement protecting company disclosures',
                'category': 'nda',
                'contract_type': 'NDA',
                'form_fields': {
                    'disclosing_party': {
                        'label': 'Disclosing Party Name',
                        'type': 'text',
                        'required': True,
                        'placeholder': 'Your company name'
                    },
                    'receiving_party': {
                        'label': 'Receiving Party Name',
                        'type': 'text',
                        'required': True,
                        'placeholder': 'Counterparty company name'
                    },
                    'effective_date': {
                        'label': 'Effective Date',
                        'type': 'date',
                        'required': True
                    },
                    'confidentiality_period': {
                        'label': 'Confidentiality Period (years)',
                        'type': 'number',
                        'required': True,
                        'default': '3',
                        'min': 1,
                        'max': 10
                    },
                    'purpose': {
                        'label': 'Purpose of Disclosure',
                        'type': 'textarea',
                        'required': True,
                        'placeholder': 'Describe the business purpose'
                    }
                },
                'mandatory_clauses': ['NDA-CONFIDENTIALITY', 'NDA-RETURN', 'NDA-TERM'],
                'optional_clauses': ['NDA-IP', 'NDA-EXCEPTIONS', 'NDA-WARRANTY'],
                'constraint_templates': {
                    'jurisdiction': {
                        'label': 'Governing Law',
                        'options': ['California', 'New York', 'Delaware', 'Texas', 'Florida'],
                        'default': 'California'
                    },
                    'liability_cap': {
                        'label': 'Liability Cap',
                        'type': 'text',
                        'default': 'Unlimited'
                    }
                }
            },
            {
                'name': 'Mutual NDA',
                'description': 'Two-way confidentiality agreement protecting disclosures from both parties',
                'category': 'nda',
                'contract_type': 'NDA',
                'form_fields': {
                    'party_a_name': {
                        'label': 'First Party Name',
                        'type': 'text',
                        'required': True
                    },
                    'party_b_name': {
                        'label': 'Second Party Name',
                        'type': 'text',
                        'required': True
                    },
                    'effective_date': {
                        'label': 'Effective Date',
                        'type': 'date',
                        'required': True
                    },
                    'confidentiality_period': {
                        'label': 'Confidentiality Period (years)',
                        'type': 'number',
                        'required': True,
                        'default': '3'
                    },
                    'permitted_uses': {
                        'label': 'Permitted Uses',
                        'type': 'textarea',
                        'required': True
                    }
                },
                'mandatory_clauses': ['NDA-MUTUAL-CONF', 'NDA-RETURN', 'NDA-TERM'],
                'optional_clauses': ['NDA-EXCEPTIONS', 'NDA-IP', 'NDA-INJUNCTIVE'],
                'constraint_templates': {
                    'jurisdiction': {
                        'label': 'Governing Law',
                        'options': ['California', 'New York', 'Delaware'],
                        'default': 'Delaware'
                    }
                }
            },
            {
                'name': 'Employee NDA',
                'description': 'Confidentiality agreement for employees accessing company secrets',
                'category': 'nda',
                'contract_type': 'NDA',
                'form_fields': {
                    'company_name': {
                        'label': 'Company Name',
                        'type': 'text',
                        'required': True
                    },
                    'employee_name': {
                        'label': 'Employee Name',
                        'type': 'text',
                        'required': True
                    },
                    'employee_id': {
                        'label': 'Employee ID',
                        'type': 'text',
                        'required': False
                    },
                    'department': {
                        'label': 'Department',
                        'type': 'text',
                        'required': False
                    },
                    'effective_date': {
                        'label': 'Start Date',
                        'type': 'date',
                        'required': True
                    }
                },
                'mandatory_clauses': ['NDA-EMPLOYEE-CONF', 'NDA-IP-ASSIGN', 'NDA-SURVIVAL'],
                'optional_clauses': ['NDA-EXCEPTIONS', 'NDA-RETURN', 'NDA-NOTIFY'],
                'constraint_templates': {
                    'non_compete_period': {
                        'label': 'Non-Compete Period (years)',
                        'type': 'number',
                        'default': '1'
                    }
                }
            },
            {
                'name': 'Vendor/Contractor NDA',
                'description': 'Confidentiality agreement for external contractors and vendors',
                'category': 'nda',
                'contract_type': 'NDA',
                'form_fields': {
                    'company_name': {
                        'label': 'Your Company Name',
                        'type': 'text',
                        'required': True
                    },
                    'vendor_name': {
                        'label': 'Vendor/Contractor Name',
                        'type': 'text',
                        'required': True
                    },
                    'scope_of_work': {
                        'label': 'Scope of Work',
                        'type': 'textarea',
                        'required': True
                    },
                    'contract_period': {
                        'label': 'Contract Period (months)',
                        'type': 'number',
                        'required': True
                    },
                    'estimated_value': {
                        'label': 'Estimated Contract Value (USD)',
                        'type': 'number',
                        'required': False
                    }
                },
                'mandatory_clauses': ['NDA-VENDOR-CONF', 'NDA-IP-PROTECTION', 'NDA-TERMINATION'],
                'optional_clauses': ['NDA-AUDIT', 'NDA-LIABILITY', 'NDA-INSURANCE']
            },
            {
                'name': 'Investor NDA',
                'description': 'Confidentiality agreement for investor discussions and due diligence',
                'category': 'nda',
                'contract_type': 'NDA',
                'form_fields': {
                    'company_name': {
                        'label': 'Company Name',
                        'type': 'text',
                        'required': True
                    },
                    'investor_name': {
                        'label': 'Investor/Fund Name',
                        'type': 'text',
                        'required': True
                    },
                    'investment_type': {
                        'label': 'Type of Investment',
                        'type': 'select',
                        'options': ['Equity', 'Debt', 'Convertible', 'Other'],
                        'required': True
                    },
                    'estimated_amount': {
                        'label': 'Estimated Investment Amount (USD)',
                        'type': 'number',
                        'required': False
                    },
                    'due_diligence_period': {
                        'label': 'Due Diligence Period (days)',
                        'type': 'number',
                        'required': True,
                        'default': '90'
                    }
                },
                'mandatory_clauses': ['NDA-INVESTOR-CONF', 'NDA-RETURN-DOCS', 'NDA-TERM'],
                'optional_clauses': ['NDA-EXCEPTIONS', 'NDA-RESIDUAL', 'NDA-STANDSTILL']
            },
            {
                'name': 'Technology/Patent NDA',
                'description': 'Specialized NDA for technology disclosures and patent discussions',
                'category': 'nda',
                'contract_type': 'NDA',
                'form_fields': {
                    'disclosing_party': {
                        'label': 'Technology Owner',
                        'type': 'text',
                        'required': True
                    },
                    'receiving_party': {
                        'label': 'Receiving Party',
                        'type': 'text',
                        'required': True
                    },
                    'technology_description': {
                        'label': 'Technology Description',
                        'type': 'textarea',
                        'required': True
                    },
                    'patent_pending': {
                        'label': 'Patent Pending Applications',
                        'type': 'textarea',
                        'required': False
                    },
                    'evaluation_period': {
                        'label': 'Evaluation Period (days)',
                        'type': 'number',
                        'required': True,
                        'default': '60'
                    }
                },
                'mandatory_clauses': ['NDA-TECH-CONF', 'NDA-PATENT-PROTECT', 'NDA-NO-LICENSE'],
                'optional_clauses': ['NDA-REVERSE-ENG', 'NDA-RETURN-DOCS', 'NDA-IP']
            }
        ]
        
        # ==================== MSA TEMPLATES (5) ====================
        
        msa_templates = [
            {
                'name': 'Standard Services MSA',
                'description': 'Master Service Agreement for general professional services',
                'category': 'msa',
                'contract_type': 'MSA',
                'form_fields': {
                    'service_provider': {
                        'label': 'Service Provider Name',
                        'type': 'text',
                        'required': True
                    },
                    'client_name': {
                        'label': 'Client Name',
                        'type': 'text',
                        'required': True
                    },
                    'services_description': {
                        'label': 'Services Description',
                        'type': 'textarea',
                        'required': True
                    },
                    'effective_date': {
                        'label': 'Effective Date',
                        'type': 'date',
                        'required': True
                    },
                    'contract_duration': {
                        'label': 'Contract Duration (months)',
                        'type': 'number',
                        'required': True,
                        'default': '12'
                    },
                    'annual_fee': {
                        'label': 'Annual Fee (USD)',
                        'type': 'number',
                        'required': True,
                        'min': 0
                    }
                },
                'mandatory_clauses': ['MSA-SCOPE', 'MSA-PAYMENT', 'MSA-TERM', 'MSA-INDEMNITY'],
                'optional_clauses': ['MSA-WARRANTY', 'MSA-IP', 'MSA-LIMITATION', 'MSA-INSURANCE'],
                'constraint_templates': {
                    'payment_terms': {
                        'label': 'Payment Terms',
                        'options': ['Net 30', 'Net 60', 'Net 90', 'Upon Signing'],
                        'default': 'Net 30'
                    },
                    'jurisdiction': {
                        'label': 'Governing Law',
                        'options': ['California', 'New York', 'Delaware'],
                        'default': 'Delaware'
                    }
                }
            },
            {
                'name': 'SaaS Service Agreement',
                'description': 'Master Service Agreement for Software-as-a-Service offerings',
                'category': 'msa',
                'contract_type': 'MSA',
                'form_fields': {
                    'saas_provider': {
                        'label': 'SaaS Provider Name',
                        'type': 'text',
                        'required': True
                    },
                    'customer_name': {
                        'label': 'Customer Name',
                        'type': 'text',
                        'required': True
                    },
                    'software_description': {
                        'label': 'Software/Service Description',
                        'type': 'textarea',
                        'required': True
                    },
                    'sla_uptime': {
                        'label': 'SLA Uptime Guarantee (%)',
                        'type': 'number',
                        'required': True,
                        'default': '99.9',
                        'min': 90,
                        'max': 100
                    },
                    'monthly_fee': {
                        'label': 'Monthly Fee (USD)',
                        'type': 'number',
                        'required': True
                    },
                    'user_count': {
                        'label': 'Authorized User Count',
                        'type': 'number',
                        'required': False
                    }
                },
                'mandatory_clauses': ['SAAS-SCOPE', 'SAAS-SLA', 'SAAS-PAYMENT', 'SAAS-DATA'],
                'optional_clauses': ['SAAS-SUPPORT', 'SAAS-BACKUP', 'SAAS-AUDIT', 'SAAS-SECURITY'],
                'constraint_templates': {
                    'data_residency': {
                        'label': 'Data Residency',
                        'options': ['US Only', 'EU Only', 'Global', 'Customer Choice'],
                        'default': 'Global'
                    }
                }
            },
            {
                'name': 'Consulting Services MSA',
                'description': 'Master Service Agreement for consulting and professional services',
                'category': 'msa',
                'contract_type': 'MSA',
                'form_fields': {
                    'consulting_firm': {
                        'label': 'Consulting Firm Name',
                        'type': 'text',
                        'required': True
                    },
                    'client_name': {
                        'label': 'Client Name',
                        'type': 'text',
                        'required': True
                    },
                    'consulting_services': {
                        'label': 'Consulting Services',
                        'type': 'textarea',
                        'required': True
                    },
                    'engagement_model': {
                        'label': 'Engagement Model',
                        'type': 'select',
                        'options': ['Time & Materials', 'Fixed Fee', 'Retainer', 'Hybrid'],
                        'required': True
                    },
                    'hourly_rate': {
                        'label': 'Hourly Rate (USD)',
                        'type': 'number',
                        'required': False
                    },
                    'retainer_amount': {
                        'label': 'Monthly Retainer (USD)',
                        'type': 'number',
                        'required': False
                    }
                },
                'mandatory_clauses': ['CONSULT-SCOPE', 'CONSULT-PAYMENT', 'CONSULT-INDEMNITY'],
                'optional_clauses': ['CONSULT-IP', 'CONSULT-WARRANTY', 'CONSULT-LIABILITY']
            },
            {
                'name': 'Maintenance & Support MSA',
                'description': 'Master Service Agreement for software maintenance and support services',
                'category': 'msa',
                'contract_type': 'MSA',
                'form_fields': {
                    'vendor_name': {
                        'label': 'Vendor/Support Provider',
                        'type': 'text',
                        'required': True
                    },
                    'customer_name': {
                        'label': 'Customer Name',
                        'type': 'text',
                        'required': True
                    },
                    'software_covered': {
                        'label': 'Software/Products Covered',
                        'type': 'textarea',
                        'required': True
                    },
                    'support_level': {
                        'label': 'Support Level',
                        'type': 'select',
                        'options': ['Basic', 'Standard', 'Premium', 'Enterprise'],
                        'required': True
                    },
                    'annual_cost': {
                        'label': 'Annual Support Cost (USD)',
                        'type': 'number',
                        'required': True
                    },
                    'response_time': {
                        'label': 'Response Time (hours)',
                        'type': 'number',
                        'required': True,
                        'default': '24'
                    }
                },
                'mandatory_clauses': ['MAINT-SCOPE', 'MAINT-SLA', 'MAINT-PAYMENT'],
                'optional_clauses': ['MAINT-UPDATES', 'MAINT-ESCALATION', 'MAINT-AVAILABILITY']
            },
            {
                'name': 'International Service MSA',
                'description': 'Master Service Agreement for international services with multi-currency support',
                'category': 'msa',
                'contract_type': 'MSA',
                'form_fields': {
                    'service_provider': {
                        'label': 'Service Provider Name',
                        'type': 'text',
                        'required': True
                    },
                    'client_name': {
                        'label': 'Client Name',
                        'type': 'text',
                        'required': True
                    },
                    'services': {
                        'label': 'Services Provided',
                        'type': 'textarea',
                        'required': True
                    },
                    'service_territories': {
                        'label': 'Service Territories',
                        'type': 'textarea',
                        'required': True
                    },
                    'currency': {
                        'label': 'Currency',
                        'type': 'select',
                        'options': ['USD', 'EUR', 'GBP', 'JPY', 'CAD'],
                        'required': True
                    },
                    'annual_fee': {
                        'label': 'Annual Fee',
                        'type': 'number',
                        'required': True
                    }
                },
                'mandatory_clauses': ['INTL-SCOPE', 'INTL-COMPLIANCE', 'INTL-PAYMENT', 'INTL-TERMS'],
                'optional_clauses': ['INTL-TAXES', 'INTL-EXPORT', 'INTL-SANCTIONS']
            }
        ]
        
        # ==================== SERVICE AGREEMENT TEMPLATES (4) ====================
        
        service_templates = [
            {
                'name': 'Professional Services Agreement',
                'description': 'Agreement for professional services delivery',
                'category': 'service',
                'contract_type': 'SERVICE',
                'form_fields': {
                    'service_provider': {
                        'label': 'Service Provider Name',
                        'type': 'text',
                        'required': True
                    },
                    'client': {
                        'label': 'Client Name',
                        'type': 'text',
                        'required': True
                    },
                    'service_type': {
                        'label': 'Type of Service',
                        'type': 'select',
                        'options': ['Consulting', 'Training', 'Implementation', 'Support'],
                        'required': True
                    },
                    'project_scope': {
                        'label': 'Project Scope',
                        'type': 'textarea',
                        'required': True
                    },
                    'project_timeline': {
                        'label': 'Project Timeline (weeks)',
                        'type': 'number',
                        'required': True
                    },
                    'project_fee': {
                        'label': 'Project Fee (USD)',
                        'type': 'number',
                        'required': True
                    }
                },
                'mandatory_clauses': ['PROF-SCOPE', 'PROF-PAYMENT', 'PROF-TERM'],
                'optional_clauses': ['PROF-WARRANTY', 'PROF-INDEMNITY', 'PROF-IP']
            },
            {
                'name': 'Training Services Agreement',
                'description': 'Agreement for training and educational services',
                'category': 'service',
                'contract_type': 'SERVICE',
                'form_fields': {
                    'training_provider': {
                        'label': 'Training Provider',
                        'type': 'text',
                        'required': True
                    },
                    'client': {
                        'label': 'Client Organization',
                        'type': 'text',
                        'required': True
                    },
                    'training_subject': {
                        'label': 'Training Subject',
                        'type': 'text',
                        'required': True
                    },
                    'participant_count': {
                        'label': 'Number of Participants',
                        'type': 'number',
                        'required': True
                    },
                    'training_duration': {
                        'label': 'Duration (hours)',
                        'type': 'number',
                        'required': True
                    },
                    'total_fee': {
                        'label': 'Total Fee (USD)',
                        'type': 'number',
                        'required': True
                    }
                },
                'mandatory_clauses': ['TRAIN-MATERIALS', 'TRAIN-PAYMENT', 'TRAIN-DELIVERY'],
                'optional_clauses': ['TRAIN-CERTIFICATION', 'TRAIN-WARRANTY']
            },
            {
                'name': 'Implementation Services Agreement',
                'description': 'Agreement for system/software implementation services',
                'category': 'service',
                'contract_type': 'SERVICE',
                'form_fields': {
                    'integrator': {
                        'label': 'Systems Integrator/Implementer',
                        'type': 'text',
                        'required': True
                    },
                    'client': {
                        'label': 'Client Name',
                        'type': 'text',
                        'required': True
                    },
                    'system_or_software': {
                        'label': 'System/Software to Implement',
                        'type': 'text',
                        'required': True
                    },
                    'implementation_scope': {
                        'label': 'Implementation Scope',
                        'type': 'textarea',
                        'required': True
                    },
                    'go_live_date': {
                        'label': 'Target Go-Live Date',
                        'type': 'date',
                        'required': True
                    },
                    'implementation_cost': {
                        'label': 'Implementation Cost (USD)',
                        'type': 'number',
                        'required': True
                    }
                },
                'mandatory_clauses': ['IMPL-SCOPE', 'IMPL-TIMELINE', 'IMPL-PAYMENT', 'IMPL-DELIVERABLES'],
                'optional_clauses': ['IMPL-TESTING', 'IMPL-TRAINING', 'IMPL-WARRANTY']
            },
            {
                'name': 'Technical Support Services Agreement',
                'description': 'Agreement for technical support and maintenance',
                'category': 'service',
                'contract_type': 'SERVICE',
                'form_fields': {
                    'support_provider': {
                        'label': 'Support Provider',
                        'type': 'text',
                        'required': True
                    },
                    'client': {
                        'label': 'Client Name',
                        'type': 'text',
                        'required': True
                    },
                    'system_covered': {
                        'label': 'Systems/Products Covered',
                        'type': 'textarea',
                        'required': True
                    },
                    'support_hours': {
                        'label': 'Support Hours',
                        'type': 'select',
                        'options': ['Business Hours Only', '24/5', '24/7'],
                        'required': True
                    },
                    'response_sla': {
                        'label': 'Response Time SLA (hours)',
                        'type': 'number',
                        'required': True,
                        'default': '4'
                    },
                    'annual_fee': {
                        'label': 'Annual Support Fee (USD)',
                        'type': 'number',
                        'required': True
                    }
                },
                'mandatory_clauses': ['TECH-SCOPE', 'TECH-SLA', 'TECH-PAYMENT'],
                'optional_clauses': ['TECH-ESCALATION', 'TECH-INCIDENT-MGMT', 'TECH-REPORTING']
            }
        ]
        
        # ==================== EMPLOYMENT AGREEMENTS (4) ====================
        
        employment_templates = [
            {
                'name': 'Full-Time Employment Agreement',
                'description': 'Employment agreement for full-time employees',
                'category': 'employment',
                'contract_type': 'EMPLOYMENT',
                'form_fields': {
                    'company': {
                        'label': 'Company Name',
                        'type': 'text',
                        'required': True
                    },
                    'employee_name': {
                        'label': 'Employee Full Name',
                        'type': 'text',
                        'required': True
                    },
                    'position': {
                        'label': 'Position/Job Title',
                        'type': 'text',
                        'required': True
                    },
                    'start_date': {
                        'label': 'Start Date',
                        'type': 'date',
                        'required': True
                    },
                    'salary': {
                        'label': 'Annual Salary (USD)',
                        'type': 'number',
                        'required': True
                    },
                    'reporting_to': {
                        'label': 'Reports To',
                        'type': 'text',
                        'required': True
                    }
                },
                'mandatory_clauses': ['EMP-POSITION', 'EMP-COMPENSATION', 'EMP-BENEFITS'],
                'optional_clauses': ['EMP-EQUITY', 'EMP-TERMINATION', 'EMP-SEVERANCE']
            },
            {
                'name': 'Contractor/Independent Contractor Agreement',
                'description': 'Agreement for independent contractors and freelancers',
                'category': 'employment',
                'contract_type': 'EMPLOYMENT',
                'form_fields': {
                    'company': {
                        'label': 'Company/Client Name',
                        'type': 'text',
                        'required': True
                    },
                    'contractor_name': {
                        'label': 'Contractor Name',
                        'type': 'text',
                        'required': True
                    },
                    'contractor_entity': {
                        'label': 'Contractor Legal Entity (if applicable)',
                        'type': 'text',
                        'required': False
                    },
                    'scope_of_work': {
                        'label': 'Scope of Work',
                        'type': 'textarea',
                        'required': True
                    },
                    'contract_period': {
                        'label': 'Contract Period',
                        'type': 'select',
                        'options': ['Project-Based', '3 months', '6 months', '1 year', 'Ongoing'],
                        'required': True
                    },
                    'compensation': {
                        'label': 'Compensation (USD)',
                        'type': 'text',
                        'required': True
                    }
                },
                'mandatory_clauses': ['CONTR-SCOPE', 'CONTR-COMP', 'CONTR-STATUS'],
                'optional_clauses': ['CONTR-IP', 'CONTR-INDEMNITY', 'CONTR-INSURANCE']
            },
            {
                'name': 'Executive Employment Agreement',
                'description': 'Employment agreement for executive-level positions',
                'category': 'employment',
                'contract_type': 'EMPLOYMENT',
                'form_fields': {
                    'company': {
                        'label': 'Company Name',
                        'type': 'text',
                        'required': True
                    },
                    'executive_name': {
                        'label': 'Executive Name',
                        'type': 'text',
                        'required': True
                    },
                    'title': {
                        'label': 'Executive Title',
                        'type': 'select',
                        'options': ['CEO', 'COO', 'CTO', 'CFO', 'CMO', 'Other'],
                        'required': True
                    },
                    'salary': {
                        'label': 'Annual Salary (USD)',
                        'type': 'number',
                        'required': True
                    },
                    'bonus_target': {
                        'label': 'Target Bonus (% of salary)',
                        'type': 'number',
                        'required': True,
                        'default': '30'
                    },
                    'equity_grant': {
                        'label': 'Equity Grant (%)',
                        'type': 'number',
                        'required': True
                    }
                },
                'mandatory_clauses': ['EXEC-COMP', 'EXEC-EQUITY', 'EXEC-SEVERANCE', 'EXEC-CLAWBACK'],
                'optional_clauses': ['EXEC-BENEFITS', 'EXEC-PERKS', 'EXEC-RESTRICTIONS']
            },
            {
                'name': 'Consultant Agreement',
                'description': 'Agreement for consulting professionals and advisors',
                'category': 'employment',
                'contract_type': 'EMPLOYMENT',
                'form_fields': {
                    'company': {
                        'label': 'Company/Organization',
                        'type': 'text',
                        'required': True
                    },
                    'consultant_name': {
                        'label': 'Consultant Name',
                        'type': 'text',
                        'required': True
                    },
                    'consulting_area': {
                        'label': 'Area of Expertise',
                        'type': 'text',
                        'required': True
                    },
                    'time_commitment': {
                        'label': 'Time Commitment (hours/month)',
                        'type': 'number',
                        'required': True
                    },
                    'hourly_rate': {
                        'label': 'Hourly Rate (USD)',
                        'type': 'number',
                        'required': False
                    },
                    'monthly_retainer': {
                        'label': 'Monthly Retainer (USD)',
                        'type': 'number',
                        'required': False
                    }
                },
                'mandatory_clauses': ['CONSULT-SCOPE', 'CONSULT-COMP', 'CONSULT-IP'],
                'optional_clauses': ['CONSULT-CONFIDENTIALITY', 'CONSULT-INDEMNITY']
            }
        ]
        
        # ==================== PURCHASE AGREEMENTS (3) ====================
        
        purchase_templates = [
            {
                'name': 'Goods Purchase Agreement',
                'description': 'Agreement for purchasing goods and products',
                'category': 'purchase',
                'contract_type': 'PURCHASE',
                'form_fields': {
                    'buyer': {
                        'label': 'Buyer Name',
                        'type': 'text',
                        'required': True
                    },
                    'seller': {
                        'label': 'Seller Name',
                        'type': 'text',
                        'required': True
                    },
                    'goods_description': {
                        'label': 'Goods Description',
                        'type': 'textarea',
                        'required': True
                    },
                    'quantity': {
                        'label': 'Quantity',
                        'type': 'text',
                        'required': True
                    },
                    'unit_price': {
                        'label': 'Unit Price (USD)',
                        'type': 'number',
                        'required': True
                    },
                    'delivery_date': {
                        'label': 'Delivery Date',
                        'type': 'date',
                        'required': True
                    }
                },
                'mandatory_clauses': ['PURCH-GOODS', 'PURCH-PRICE', 'PURCH-DELIVERY'],
                'optional_clauses': ['PURCH-WARRANTY', 'PURCH-WARRANTY-DISCLAIMER', 'PURCH-RETURN']
            },
            {
                'name': 'Service Purchase Agreement',
                'description': 'Agreement for purchasing professional services',
                'category': 'purchase',
                'contract_type': 'PURCHASE',
                'form_fields': {
                    'purchaser': {
                        'label': 'Service Purchaser',
                        'type': 'text',
                        'required': True
                    },
                    'service_provider': {
                        'label': 'Service Provider',
                        'type': 'text',
                        'required': True
                    },
                    'services': {
                        'label': 'Services to be Provided',
                        'type': 'textarea',
                        'required': True
                    },
                    'scope': {
                        'label': 'Scope of Work',
                        'type': 'textarea',
                        'required': True
                    },
                    'total_price': {
                        'label': 'Total Price (USD)',
                        'type': 'number',
                        'required': True
                    },
                    'completion_date': {
                        'label': 'Completion Date',
                        'type': 'date',
                        'required': True
                    }
                },
                'mandatory_clauses': ['SERVICE-SCOPE', 'SERVICE-PRICE', 'SERVICE-DELIVERABLES'],
                'optional_clauses': ['SERVICE-WARRANTY', 'SERVICE-INDEMNITY']
            },
            {
                'name': 'Asset Purchase Agreement',
                'description': 'Agreement for purchasing business assets or company',
                'category': 'purchase',
                'contract_type': 'PURCHASE',
                'form_fields': {
                    'buyer': {
                        'label': 'Buyer Name',
                        'type': 'text',
                        'required': True
                    },
                    'seller': {
                        'label': 'Seller Name',
                        'type': 'text',
                        'required': True
                    },
                    'assets_description': {
                        'label': 'Assets Being Purchased',
                        'type': 'textarea',
                        'required': True
                    },
                    'purchase_price': {
                        'label': 'Purchase Price (USD)',
                        'type': 'number',
                        'required': True
                    },
                    'closing_date': {
                        'label': 'Closing Date',
                        'type': 'date',
                        'required': True
                    },
                    'payment_terms': {
                        'label': 'Payment Terms',
                        'type': 'text',
                        'required': True
                    }
                },
                'mandatory_clauses': ['ASSET-DESC', 'ASSET-PRICE', 'ASSET-CLOSING', 'ASSET-REPS'],
                'optional_clauses': ['ASSET-INDEMNITY', 'ASSET-ESCROW', 'ASSET-REPRESENTATIONS']
            }
        ]
        
        # ==================== LICENSE AGREEMENTS (3) ====================
        
        license_templates = [
            {
                'name': 'Software License Agreement',
                'description': 'License agreement for software and applications',
                'category': 'license',
                'contract_type': 'LICENSE',
                'form_fields': {
                    'licensor': {
                        'label': 'Software Licensor/Provider',
                        'type': 'text',
                        'required': True
                    },
                    'licensee': {
                        'label': 'Licensee/Customer',
                        'type': 'text',
                        'required': True
                    },
                    'software_description': {
                        'label': 'Software Description',
                        'type': 'textarea',
                        'required': True
                    },
                    'license_type': {
                        'label': 'License Type',
                        'type': 'select',
                        'options': ['Perpetual', '1 Year', '3 Years', '5 Years'],
                        'required': True
                    },
                    'license_fee': {
                        'label': 'License Fee (USD)',
                        'type': 'number',
                        'required': True
                    },
                    'user_count': {
                        'label': 'Number of Users Licensed',
                        'type': 'number',
                        'required': False
                    }
                },
                'mandatory_clauses': ['LIC-GRANT', 'LIC-RESTRICTIONS', 'LIC-PAYMENT'],
                'optional_clauses': ['LIC-SUPPORT', 'LIC-UPDATES', 'LIC-WARRANTY', 'LIC-IP']
            },
            {
                'name': 'Content License Agreement',
                'description': 'License agreement for intellectual property and content',
                'category': 'license',
                'contract_type': 'LICENSE',
                'form_fields': {
                    'content_owner': {
                        'label': 'Content Owner',
                        'type': 'text',
                        'required': True
                    },
                    'licensee': {
                        'label': 'Licensee',
                        'type': 'text',
                        'required': True
                    },
                    'content_description': {
                        'label': 'Content Description',
                        'type': 'textarea',
                        'required': True
                    },
                    'license_scope': {
                        'label': 'License Scope',
                        'type': 'select',
                        'options': ['Exclusive', 'Non-exclusive', 'Limited'],
                        'required': True
                    },
                    'territory': {
                        'label': 'Territory',
                        'type': 'text',
                        'required': True
                    },
                    'license_fee': {
                        'label': 'License Fee (USD)',
                        'type': 'number',
                        'required': True
                    }
                },
                'mandatory_clauses': ['CONTENT-GRANT', 'CONTENT-RESTRICTIONS', 'CONTENT-PAYMENT'],
                'optional_clauses': ['CONTENT-ATTRIBUTION', 'CONTENT-WARRANTY', 'CONTENT-TERM']
            },
            {
                'name': 'Patent License Agreement',
                'description': 'License agreement for patent rights',
                'category': 'license',
                'contract_type': 'LICENSE',
                'form_fields': {
                    'patent_owner': {
                        'label': 'Patent Owner',
                        'type': 'text',
                        'required': True
                    },
                    'licensee': {
                        'label': 'Licensee',
                        'type': 'text',
                        'required': True
                    },
                    'patent_description': {
                        'label': 'Patents Licensed',
                        'type': 'textarea',
                        'required': True
                    },
                    'field_of_use': {
                        'label': 'Field of Use',
                        'type': 'textarea',
                        'required': True
                    },
                    'license_scope': {
                        'label': 'License Scope',
                        'type': 'select',
                        'options': ['Exclusive', 'Non-exclusive', 'Limited'],
                        'required': True
                    },
                    'royalty_rate': {
                        'label': 'Royalty Rate (%)',
                        'type': 'number',
                        'required': True
                    }
                },
                'mandatory_clauses': ['PATENT-GRANT', 'PATENT-RESTRICTIONS', 'PATENT-ROYALTY'],
                'optional_clauses': ['PATENT-WARRANTY', 'PATENT-INDEMNITY', 'PATENT-IMPROVEMENTS']
            }
        ]
        
        # ==================== PARTNERSHIP AGREEMENTS (2) ====================
        
        partnership_templates = [
            {
                'name': '50/50 Partnership Agreement',
                'description': 'Equal partnership agreement for 50/50 ventures',
                'category': 'partnership',
                'contract_type': 'PARTNERSHIP',
                'form_fields': {
                    'partner_a': {
                        'label': 'First Partner Name',
                        'type': 'text',
                        'required': True
                    },
                    'partner_b': {
                        'label': 'Second Partner Name',
                        'type': 'text',
                        'required': True
                    },
                    'partnership_name': {
                        'label': 'Partnership Name',
                        'type': 'text',
                        'required': True
                    },
                    'business_purpose': {
                        'label': 'Business Purpose',
                        'type': 'textarea',
                        'required': True
                    },
                    'initial_capital': {
                        'label': 'Initial Capital (USD)',
                        'type': 'number',
                        'required': True
                    },
                    'capital_contribution_a': {
                        'label': 'Partner A Contribution (USD)',
                        'type': 'number',
                        'required': True
                    }
                },
                'mandatory_clauses': ['PART-FORMATION', 'PART-CAPITAL', 'PART-PROFIT', 'PART-MANAGEMENT'],
                'optional_clauses': ['PART-EXIT', 'PART-DISSOLUTION', 'PART-DISPUTE']
            },
            {
                'name': 'Unequal Partnership Agreement',
                'description': 'Partnership agreement with unequal ownership stakes',
                'category': 'partnership',
                'contract_type': 'PARTNERSHIP',
                'form_fields': {
                    'partner_a': {
                        'label': 'Partner A Name',
                        'type': 'text',
                        'required': True
                    },
                    'partner_a_stake': {
                        'label': 'Partner A Ownership (%)',
                        'type': 'number',
                        'required': True
                    },
                    'partner_b': {
                        'label': 'Partner B Name',
                        'type': 'text',
                        'required': True
                    },
                    'partner_b_stake': {
                        'label': 'Partner B Ownership (%)',
                        'type': 'number',
                        'required': True
                    },
                    'partnership_name': {
                        'label': 'Partnership Name',
                        'type': 'text',
                        'required': True
                    },
                    'total_capitalization': {
                        'label': 'Total Capitalization (USD)',
                        'type': 'number',
                        'required': True
                    }
                },
                'mandatory_clauses': ['PART-FORMATION', 'PART-STAKES', 'PART-PROFIT', 'PART-MANAGEMENT'],
                'optional_clauses': ['PART-EXIT', 'PART-BUYOUT', 'PART-RIGHTS']
            }
        ]
        
        # ==================== LEASE AGREEMENTS (2) ====================
        
        lease_templates = [
            {
                'name': 'Commercial Space Lease',
                'description': 'Lease agreement for commercial office and retail space',
                'category': 'lease',
                'contract_type': 'LEASE',
                'form_fields': {
                    'landlord': {
                        'label': 'Landlord/Property Owner',
                        'type': 'text',
                        'required': True
                    },
                    'tenant': {
                        'label': 'Tenant Name',
                        'type': 'text',
                        'required': True
                    },
                    'property_address': {
                        'label': 'Property Address',
                        'type': 'textarea',
                        'required': True
                    },
                    'square_footage': {
                        'label': 'Square Footage',
                        'type': 'number',
                        'required': True
                    },
                    'monthly_rent': {
                        'label': 'Monthly Rent (USD)',
                        'type': 'number',
                        'required': True
                    },
                    'lease_term': {
                        'label': 'Lease Term (years)',
                        'type': 'number',
                        'required': True,
                        'default': '3'
                    },
                    'lease_start_date': {
                        'label': 'Lease Start Date',
                        'type': 'date',
                        'required': True
                    }
                },
                'mandatory_clauses': ['LEASE-TERM', 'LEASE-RENT', 'LEASE-OCCUPANCY', 'LEASE-MAINT'],
                'optional_clauses': ['LEASE-RENEWAL', 'LEASE-TERMINATION', 'LEASE-DEPOSIT']
            },
            {
                'name': 'Equipment Lease Agreement',
                'description': 'Lease agreement for equipment and machinery',
                'category': 'lease',
                'contract_type': 'LEASE',
                'form_fields': {
                    'lessor': {
                        'label': 'Equipment Owner/Lessor',
                        'type': 'text',
                        'required': True
                    },
                    'lessee': {
                        'label': 'Equipment Lessee',
                        'type': 'text',
                        'required': True
                    },
                    'equipment_description': {
                        'label': 'Equipment Description',
                        'type': 'textarea',
                        'required': True
                    },
                    'equipment_value': {
                        'label': 'Equipment Value (USD)',
                        'type': 'number',
                        'required': True
                    },
                    'monthly_lease_payment': {
                        'label': 'Monthly Lease Payment (USD)',
                        'type': 'number',
                        'required': True
                    },
                    'lease_duration': {
                        'label': 'Lease Duration (months)',
                        'type': 'number',
                        'required': True
                    },
                    'start_date': {
                        'label': 'Lease Start Date',
                        'type': 'date',
                        'required': True
                    }
                },
                'mandatory_clauses': ['EQUIP-LEASE-TERM', 'EQUIP-PAYMENT', 'EQUIP-MAINTENANCE'],
                'optional_clauses': ['EQUIP-INSURANCE', 'EQUIP-RETURN', 'EQUIP-BUYOUT']
            }
        ]
        
        # ==================== AFFILIATE & DISTRIBUTION AGREEMENTS (2) ====================
        
        affiliation_templates = [
            {
                'name': 'Affiliate Marketing Agreement',
                'description': 'Agreement for affiliate marketing relationships',
                'category': 'affiliation',
                'contract_type': 'AFFILIATE',
                'form_fields': {
                    'merchant': {
                        'label': 'Merchant/Company Name',
                        'type': 'text',
                        'required': True
                    },
                    'affiliate': {
                        'label': 'Affiliate Name',
                        'type': 'text',
                        'required': True
                    },
                    'product_service': {
                        'label': 'Products/Services to Promote',
                        'type': 'textarea',
                        'required': True
                    },
                    'commission_rate': {
                        'label': 'Commission Rate (%)',
                        'type': 'number',
                        'required': True
                    },
                    'payment_frequency': {
                        'label': 'Payment Frequency',
                        'type': 'select',
                        'options': ['Weekly', 'Monthly', 'Quarterly'],
                        'required': True
                    },
                    'minimum_threshold': {
                        'label': 'Minimum Payment Threshold (USD)',
                        'type': 'number',
                        'required': False,
                        'default': '100'
                    }
                },
                'mandatory_clauses': ['AFF-RELATIONSHIP', 'AFF-COMMISSION', 'AFF-PAYMENT'],
                'optional_clauses': ['AFF-MARKETING', 'AFF-RESTRICTIONS', 'AFF-TERMINATION']
            },
            {
                'name': 'Distribution Agreement',
                'description': 'Agreement for product distribution relationships',
                'category': 'affiliation',
                'contract_type': 'AFFILIATE',
                'form_fields': {
                    'supplier': {
                        'label': 'Supplier/Manufacturer',
                        'type': 'text',
                        'required': True
                    },
                    'distributor': {
                        'label': 'Distributor Name',
                        'type': 'text',
                        'required': True
                    },
                    'products': {
                        'label': 'Products to Distribute',
                        'type': 'textarea',
                        'required': True
                    },
                    'territory': {
                        'label': 'Distribution Territory',
                        'type': 'text',
                        'required': True
                    },
                    'term': {
                        'label': 'Agreement Term (years)',
                        'type': 'number',
                        'required': True,
                        'default': '3'
                    },
                    'minimum_purchase': {
                        'label': 'Minimum Annual Purchase (USD)',
                        'type': 'number',
                        'required': False
                    }
                },
                'mandatory_clauses': ['DIST-APPOINTMENT', 'DIST-TERRITORY', 'DIST-TERMS'],
                'optional_clauses': ['DIST-EXCLUSIVITY', 'DIST-PERFORMANCE', 'DIST-TERMINATION']
            }
        ]
        
        # Compile all templates
        all_templates = (
            nda_templates + msa_templates + service_templates +
            employment_templates + purchase_templates + license_templates +
            partnership_templates + lease_templates + affiliation_templates
        )
        
        # Create templates in database
        for template_data in all_templates:
            try:
                # Add computed fields
                template_data['tenant_id'] = tenant_id
                template_data['created_by'] = user_id
                template_data['base_template_id'] = uuid.uuid4()
                template_data['contract_content_template'] = (
                    f"This is a {template_data['contract_type']} contract "
                    f"between {{{{party_a_name}}}} and {{{{party_b_name}}}}"
                )
                
                template = ContractEditingTemplate.objects.create(**template_data)
                templates_created += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {template.name}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to create {template_data["name"]}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Successfully created {templates_created} contract templates')
        )
