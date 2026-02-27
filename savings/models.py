from django.db import models
from members.models import Member, BankAccount


def generate_saving_id(saving_type):
    prefix_map = {
        'PRINCIPAL': 'SIM-PK',
        'MANDATORY': 'SIM-WB',
        'VOLUNTARY': 'SIM-SK',
    }
    prefix = prefix_map.get(saving_type, 'SIM')
    last = Saving.objects.filter(saving_type=saving_type).count() + 1
    return f"{prefix}-{last:04d}"


def generate_saving_transaction_id():
    last = Saving.objects.count() + 1
    return f"TRX-SV-{last:04d}"


class Saving(models.Model):
    SAVING_TYPE = [
        ('PRINCIPAL', 'Simpanan Pokok'),
        ('MANDATORY', 'Simpanan Wajib'),
        ('VOLUNTARY', 'Simpanan Sukarela'),
    ]
    STATUS = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('REJECTED', 'Rejected'),
    ]

    saving_id        = models.CharField(max_length=30, unique=True, editable=False)
    transaction_id   = models.CharField(max_length=30, unique=True, editable=False)
    member           = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='savings')
    saving_type      = models.CharField(max_length=20, choices=SAVING_TYPE)
    amount           = models.DecimalField(max_digits=15, decimal_places=2)
    status           = models.CharField(max_length=20, choices=STATUS, default='PENDING')
    proof_image      = models.ImageField(upload_to='savings/proofs/')
    bank_account     = models.ForeignKey(
        BankAccount, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    rejection_reason = models.TextField(blank=True)
    verified_by      = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='verified_savings'
    )
    verified_at      = models.DateTimeField(null=True, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-generate ID saat pertama kali dibuat
        if not self.saving_id:
            self.saving_id = generate_saving_id(self.saving_type)
        if not self.transaction_id:
            self.transaction_id = generate_saving_transaction_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.saving_id} - {self.member.full_name} ({self.status})"