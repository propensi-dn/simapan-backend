from django.db import models


class MemberStatus(models.TextChoices):
	PENDING = 'PENDING', 'Pending'
	VERIFIED = 'VERIFIED', 'Verified'
	ACTIVE = 'ACTIVE', 'Active'
	REJECTED = 'REJECTED', 'Rejected'


class MemberProfile(models.Model):
	user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='member_profile')
	status = models.CharField(max_length=20, choices=MemberStatus.choices, default=MemberStatus.PENDING)
	has_paid_pokok = models.BooleanField(default=False)
	member_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return f'{self.user.email} - {self.status}'

# Create your models here.
