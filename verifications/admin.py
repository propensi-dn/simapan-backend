from django.contrib import admin

from verifications.models import VerificationLog


@admin.register(VerificationLog)
class VerificationLogAdmin(admin.ModelAdmin):
    list_display = ('saving_transaction', 'staff', 'action', 'reviewed_amount', 'created_at')
    list_filter = ('action',)
    search_fields = ('saving_transaction__transaction_id', 'staff__email')
    readonly_fields = ('created_at',)