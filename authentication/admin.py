from django.contrib import admin

from clm_backend.admin_site import admin_site
from .models import User

@admin.register(User, site=admin_site)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_active', 'date_joined')