from rest_framework import generics, permissions

from config.models import CooperativeBankAccount
from config.serializers import CooperativeBankAccountSerializer


class ActiveCooperativeBankAccountView(generics.RetrieveAPIView):
	serializer_class = CooperativeBankAccountSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_object(self):
		account = CooperativeBankAccount.objects.filter(is_active=True).first()
		if account:
			return account

		return CooperativeBankAccount.objects.create(
			bank_name='Bank Central Asia (BCA)',
			account_number='123-456-7890',
			account_holder='SI-MAPAN Credit Union',
			is_active=True,
		)

# Create your views here.
