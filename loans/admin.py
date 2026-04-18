from django.contrib import admin
from .models import Loan, Installment, BadDebt


class InstallmentInline(admin.TabularInline):
    model = Installment
    extra = 0
    readonly_fields = ['transaction_id', 'paid_at', 'updated_at']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['loan_id', 'member', 'category', 'amount', 'tenor', 'status', 'application_date']
    list_filter = ['status', 'category']
    search_fields = ['loan_id', 'member__full_name', 'member__user__email']
    readonly_fields = ['loan_id', 'application_date', 'updated_at']
    inlines = [InstallmentInline]


@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'loan', 'installment_number', 'due_date', 'amount', 'status']
    list_filter = ['status']
    search_fields = ['transaction_id', 'loan__loan_id', 'loan__member__full_name']
    readonly_fields = ['transaction_id', 'updated_at']


@admin.register(BadDebt)
class BadDebtAdmin(admin.ModelAdmin):
    list_display = ['loan', 'status', 'created_at']
    list_filter = ['status']