from django.contrib import admin

from savings.models import SavingTransaction, SavingsWithdrawal


@admin.register(SavingTransaction)
class SavingTransactionAdmin(admin.ModelAdmin):
	list_display = ('transaction_id', 'member', 'saving_type', 'amount', 'status', 'submitted_at')
	list_filter = ('saving_type', 'status')
	search_fields = ('transaction_id', 'saving_id', 'member__user__email', 'member__full_name')


@admin.register(SavingsWithdrawal)
class SavingsWithdrawalAdmin(admin.ModelAdmin):
	list_display = ('withdrawal_id', 'member', 'amount', 'bank_name', 'account_number', 'status', 'created_at')
	list_filter = ('status',)
	search_fields = ('withdrawal_id', 'member__user__email', 'member__full_name', 'account_number')
