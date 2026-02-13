from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Display the new fields in the admin list view
    list_display = ('username', 'email', 'role', 'status', 'is_staff')
    
    # Add filters for easier management
    list_filter = ('role', 'status', 'is_staff', 'is_superuser')
    
    # Fieldsets for the edit page
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('role', 'status')}),
    )
    
    # Fieldsets for the 'add user' page
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Extra Info', {'fields': ('role', 'status')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)