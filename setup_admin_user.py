#!/usr/bin/env python
"""
Setup admin user for testing
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from authentication.models import User
from tenants.models import TenantModel

# Create tenant
tenant, created = TenantModel.objects.get_or_create(
    name="CLM Default",
    defaults={
        "domain": "clm.local",
        "status": "active",
        "subscription_plan": "enterprise"
    }
)

if created:
    print(f"✓ Created tenant: {tenant.name} (ID: {tenant.id})")
else:
    print(f"✓ Tenant exists: {tenant.name} (ID: {tenant.id})")

# Create/Update admin user
user, created = User.objects.get_or_create(
    email="admin@clm.local",
    defaults={
        "first_name": "Admin",
        "last_name": "User",
        "is_staff": True,
        "is_superuser": True,
        "is_active": True,
        "tenant_id": tenant.id
    }
)

# Always set password
user.set_password("Admin@123")
user.save()

print(f"✓ Admin user: {user.email}")
print(f"  Password: Admin@123")
print(f"  Tenant: {tenant.name}")
print(f"  Is Staff: {user.is_staff}")
print(f"  Is Superuser: {user.is_superuser}")

# Create/Update Rahul admin user
rahul, _rahul_created = User.objects.get_or_create(
    email="rahuljha93102@gmail.com",
    defaults={
        "first_name": "Rahul",
        "last_name": "Jha",
        "is_staff": True,
        "is_superuser": True,
        "is_active": True,
        "tenant_id": tenant.id,
    },
)

rahul.is_staff = True
rahul.is_superuser = True
rahul.is_active = True
rahul.tenant_id = tenant.id
rahul.set_password("Admin@123")
rahul.save()

print(f"\n✓ Admin user: {rahul.email}")
print(f"  Password: Admin@123")
print(f"  Tenant: {tenant.name}")
print(f"  Is Staff: {rahul.is_staff}")
print(f"  Is Superuser: {rahul.is_superuser}")

# Create test user
test_user, created = User.objects.get_or_create(
    email="user@clm.local",
    defaults={
        "first_name": "Test",
        "last_name": "User",
        "is_staff": False,
        "is_superuser": False,
        "is_active": True,
        "tenant_id": tenant.id
    }
)

test_user.set_password("User@123")
test_user.save()

print(f"\n✓ Test user: {test_user.email}")
print(f"  Password: User@123")
print(f"  Tenant: {tenant.name}")
