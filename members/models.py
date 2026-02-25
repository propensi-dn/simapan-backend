from django.db import models
from users.models import User

class Member(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('VERIFIED', 'Verified'),
        ('ACTIVE', 'Active'),
        ('REJECTED', 'Rejected'),
        ('INACTIVE', 'Inactive'),
    ]
    GENDER_CHOICES = [('M', 'Laki-laki'), ('F', 'Perempuan')]

    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member')
    member_id       = models.CharField(max_length=20, unique=True, null=True, blank=True)  # #MBR-xxx
    full_name       = models.CharField(max_length=255)
    place_of_birth  = models.CharField(max_length=100)
    date_of_birth   = models.DateField()
    gender          = models.CharField(max_length=1, choices=GENDER_CHOICES)
    occupation      = models.CharField(max_length=100)
    phone_number    = models.CharField(max_length=20)
    home_address    = models.TextField()
    city            = models.CharField(max_length=100)
    postal_code     = models.CharField(max_length=10)
    nik             = models.CharField(max_length=16, unique=True)
    ktp_image       = models.ImageField(upload_to='ktp/')
    selfie_image    = models.ImageField(upload_to='selfie/', null=True, blank=True)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    rejection_reason= models.TextField(null=True, blank=True)
    verified_by     = models.ForeignKey(User, null=True, blank=True,
                        on_delete=models.SET_NULL, related_name='verified_members')
    verified_at     = models.DateTimeField(null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.full_name} ({self.status})'

class BankAccount(models.Model):
    member         = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='bank_accounts')
    bank_name      = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_holder = models.CharField(max_length=150)
    is_primary     = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bank_name} - {self.account_number} ({self.member.full_name})"