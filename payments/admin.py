from django.contrib import admin
from .models import Payment, FailedPayment, ContactMessage

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # Fields to show in the list
    list_display = ('transaction_id', 'first_name', 'amount', 'donate_to', 'status', 'created_at')
    
    # Filters on the right sidebar
    list_filter = ('status', 'donate_to', 'country', 'created_at')
    
    # Search box functionality
    search_fields = ('transaction_id', 'first_name', 'last_name', 'email')
    
    # Make the list ordered by newest first
    ordering = ('-created_at',)

@admin.register(FailedPayment)
class FailedPaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'first_name', 'email', 'amount', 'created_at')
    search_fields = ('transaction_id', 'email')
    readonly_fields = ('created_at',)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email')
    readonly_fields = ('created_at',)