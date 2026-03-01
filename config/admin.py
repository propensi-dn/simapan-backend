from django.contrib import admin

from config.models import CooperativeBankAccount


@admin.register(CooperativeBankAccount)
class CooperativeBankAccountAdmin(admin.ModelAdmin):
	list_display = ('bank_name', 'account_number', 'account_holder', 'is_active')
	list_filter = ('is_active',)

# Register your models here.
