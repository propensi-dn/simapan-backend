from django.contrib import admin

from savings.models import SavingTransaction


@admin.register(SavingTransaction)
class SavingTransactionAdmin(admin.ModelAdmin):
	list_display = ('transaction_id', 'user', 'saving_type', 'amount', 'status', 'submitted_at')
	list_filter = ('saving_type', 'status')
	search_fields = ('transaction_id', 'saving_id', 'user__email')

# Register your models here.
