from django.db import models


class CooperativeBankAccount(models.Model):
	bank_name = models.CharField(max_length=100)
	account_number = models.CharField(max_length=50)
	account_holder = models.CharField(max_length=100)
	qr_code_url = models.URLField(blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-is_active', '-created_at']

	def __str__(self) -> str:
		return f'{self.bank_name} - {self.account_number}'

# Create your models here.
