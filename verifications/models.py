from decimal import Decimal
from django.db import models


class SavingType(models.TextChoices):
    POKOK    = 'POKOK',    'Simpanan Pokok'
    WAJIB    = 'WAJIB',    'Simpanan Wajib'
    SUKARELA = 'SUKARELA', 'Simpanan Sukarela'


class SavingStatus(models.TextChoices):
    PENDING  = 'PENDING',  'Pending'
    SUCCESS  = 'SUCCESS',  'Success'
    REJECTED = 'REJECTED', 'Rejected'


class SavingTransaction(models.Model):
    member                = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='saving_transactions')
    saving_type           = models.CharField(max_length=20, choices=SavingType.choices)
    saving_id             = models.CharField(max_length=50, unique=True)
    transaction_id        = models.CharField(max_length=50, unique=True)
    amount                = models.DecimalField(max_digits=14, decimal_places=2)
    status                = models.CharField(max_length=20, choices=SavingStatus.choices, default=SavingStatus.PENDING)
    transfer_proof        = models.FileField(upload_to='transfer_proofs/')
    member_bank_name      = models.CharField(max_length=100)
    member_account_number = models.CharField(max_length=50)
    rejection_reason      = models.TextField(blank=True)
    verified_by           = models.ForeignKey(
        'users.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='verified_savings'
    )
    submitted_at          = models.DateTimeField(auto_now_add=True)
    updated_at            = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self) -> str:
        return f'{self.transaction_id} - {self.member.user.email}'

    def _next_sequence(self) -> int:
        return SavingTransaction.objects.count() + 1

    def save(self, *args, **kwargs):
        if not self.saving_id:
            seq = self._next_sequence()
            prefix_map = {
                SavingType.POKOK:    'SIM-PK',
                SavingType.WAJIB:    'SIM-WB',
                SavingType.SUKARELA: 'SIM-SK',
            }
            self.saving_id = f"{prefix_map[self.saving_type]}-{seq:05d}"

        if not self.transaction_id:
            seq = self._next_sequence()
            self.transaction_id = f'TRX-SV-{seq:05d}'

        super().save(*args, **kwargs)


class SavingsBalance(models.Model):
    member         = models.OneToOneField('members.Member', on_delete=models.CASCADE, related_name='savings_balance')
    total_pokok    = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total_wajib    = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total_sukarela = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    last_updated   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Savings Balance'
        verbose_name_plural = 'Savings Balances'

    def __str__(self):
        return f'Balance — {self.member.full_name}'

    @property
    def total(self) -> Decimal:
        return self.total_pokok + self.total_wajib + self.total_sukarela