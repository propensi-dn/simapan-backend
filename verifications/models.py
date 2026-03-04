from django.db import models


class VerificationAction(models.TextChoices):
    APPROVE = 'APPROVE', 'Approve'
    REJECT = 'REJECT', 'Reject'


class VerificationLog(models.Model):
    """
    Audit trail for all verification actions performed by staff.
    Covers both PBI-9 (simpanan pokok / member activation)
    and PBI-12 (simpanan wajib/sukarela confirmation).
    """
    staff = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='verification_logs',
    )
    saving_transaction = models.ForeignKey(
        'savings.SavingTransaction',
        on_delete=models.CASCADE,
        related_name='verification_logs',
    )
    action = models.CharField(max_length=10, choices=VerificationAction.choices)
    rejection_reason = models.TextField(blank=True)
    reviewed_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Amount after staff review/edit (if different from submitted)',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return (
            f'{self.staff} → {self.action} '
            f'[{self.saving_transaction.transaction_id}] at {self.created_at}'
        )