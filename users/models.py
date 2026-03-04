from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
	MEMBER = 'MEMBER', 'Member'
	STAFF = 'STAFF', 'Staff'
	MANAGER = 'MANAGER', 'Manager'
	CHAIRMAN = 'CHAIRMAN', 'Chairman'


class User(AbstractUser):
	email = models.EmailField(unique=True)
	role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.MEMBER)

	def __str__(self) -> str:
		return self.email

# Create your models here.
