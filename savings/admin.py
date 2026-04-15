from django.contrib import admin

from savings.models import SavingTransaction


@admin.register(SavingTransaction)
class SavingTransactionAdmin(admin.ModelAdmin):
	list_display = ('transaction_id', 'member', 'saving_type', 'amount', 'status', 'submitted_at')
	list_filter = ('saving_type', 'status')
	search_fields = ('transaction_id', 'saving_id', 'member__user__email', 'member__full_name')

# Register your models here.
