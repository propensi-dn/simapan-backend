from rest_framework import serializers

from config.models import CooperativeBankAccount


class CooperativeBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CooperativeBankAccount
        fields = ('bank_name', 'account_number', 'account_holder', 'qr_code_url')
