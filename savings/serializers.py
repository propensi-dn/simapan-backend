from decimal import Decimal

from rest_framework import serializers

from savings.models import SavingTransaction, SavingType


class SavingTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingTransaction
        fields = (
            'id',
            'saving_id',
            'transaction_id',
            'saving_type',
            'amount',
            'status',
            'transfer_proof',
            'member_bank_name',
            'member_account_number',
            'rejection_reason',
            'submitted_at',
        )
        read_only_fields = ('saving_id', 'transaction_id', 'status', 'rejection_reason', 'submitted_at')


class InitialDepositCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingTransaction
        fields = ('transfer_proof', 'member_bank_name', 'member_account_number')

    def create(self, validated_data):
        return SavingTransaction.objects.create(
            user=self.context['request'].user,
            saving_type=SavingType.POKOK,
            amount=Decimal('150000.00'),
            **validated_data,
        )


class DepositCreateSerializer(serializers.ModelSerializer):
    saving_type = serializers.ChoiceField(choices=[SavingType.WAJIB, SavingType.SUKARELA])
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        model = SavingTransaction
        fields = ('saving_type', 'amount', 'transfer_proof', 'member_bank_name', 'member_account_number')

    def validate(self, attrs):
        saving_type = attrs['saving_type']
        amount = attrs['amount']

        if saving_type == SavingType.WAJIB:
            attrs['amount'] = Decimal('100000.00')
        elif amount <= 0:
            raise serializers.ValidationError('Jumlah setoran harus lebih dari 0')

        return attrs

    def create(self, validated_data):
        return SavingTransaction.objects.create(user=self.context['request'].user, **validated_data)
