from django.db import models


class CooperativeBank(models.Model):
    bank_name      = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_holder = models.CharField(max_length=150)
    is_active      = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Cooperative Bank Account'

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"