from decimal import Decimal

from rest_framework import serializers

from savings.models import SavingTransaction, SavingType
from savings.serializers import SavingTransactionSerializer


# ---------------------------------------------------------------------------
# PBI-9  – Deposit Pokok detail + confirmation
# PBI-12 – Deposit Wajib/Sukarela detail + confirmation
# ---------------------------------------------------------------------------

class TransactionDetailSerializer(serializers.ModelSerializer):
    """
    Full detail view of a SavingTransaction as seen by staff.
    Used by both PBI-9 and PBI-12 detail endpoints.
    """
    member_name = serializers.SerializerMethodField()
    member_id = serializers.SerializerMethodField()
    member_status = serializers.SerializerMethodField()

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
            'updated_at',
            # enriched
            'member_name',
            'member_id',
            'member_status',
        )

    def get_member_name(self, obj: SavingTransaction) -> str:
        return obj.user.get_full_name() or obj.user.username

    def get_member_id(self, obj: SavingTransaction) -> str | None:
        profile = getattr(obj.user, 'member_profile', None)
        return profile.member_id if profile else None

    def get_member_status(self, obj: SavingTransaction) -> str | None:
        profile = getattr(obj.user, 'member_profile', None)
        return profile.status if profile else None


# ---------------------------------------------------------------------------
# PBI-9 – Confirm / Reject simpanan POKOK  →  activates member
# ---------------------------------------------------------------------------

class PokokConfirmSerializer(serializers.Serializer):
    """
    Staff approves OR rejects the initial simpanan pokok payment.
    - approve  → member status VERIFIED → ACTIVE, generate member_id
    - reject   → saving status → REJECTED, member.has_paid_pokok reset
    """
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, attrs):
        if attrs['action'] == 'reject' and not attrs.get('rejection_reason', '').strip():
            raise serializers.ValidationError(
                {'rejection_reason': 'Rejection reason wajib diisi saat menolak'}
            )
        return attrs


# ---------------------------------------------------------------------------
# PBI-12 – Confirm / Reject simpanan WAJIB / SUKARELA
# ---------------------------------------------------------------------------

class DepositConfirmSerializer(serializers.Serializer):
    """
    Staff approves OR rejects a wajib/sukarela deposit.
    Optionally allows editing the amount (Review Setoran feature).
    - approve  → saving status → SUCCESS, member balance updated
    - reject   → saving status → REJECTED
    """
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True, default='')
    reviewed_amount = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):
        if attrs['action'] == 'reject' and not attrs.get('rejection_reason', '').strip():
            raise serializers.ValidationError(
                {'rejection_reason': 'Rejection reason wajib diisi saat menolak'}
            )

        reviewed = attrs.get('reviewed_amount')
        if reviewed is not None and reviewed <= Decimal('0'):
            raise serializers.ValidationError(
                {'reviewed_amount': 'Amount harus lebih dari 0'}
            )
        return attrs


# ---------------------------------------------------------------------------
# Staff queue list serializers
# ---------------------------------------------------------------------------

class PokokQueueSerializer(serializers.ModelSerializer):
    """Lightweight row for the POKOK verification queue (PBI-9 list)."""
    member_name = serializers.SerializerMethodField()
    member_email = serializers.SerializerMethodField()

    class Meta:
        model = SavingTransaction
        fields = (
            'id',
            'saving_id',
            'transaction_id',
            'amount',
            'status',
            'submitted_at',
            'member_name',
            'member_email',
        )

    def get_member_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_member_email(self, obj):
        return obj.user.email


class DepositQueueSerializer(serializers.ModelSerializer):
    """Lightweight row for the WAJIB/SUKARELA verification queue (PBI-12 list)."""
    member_name = serializers.SerializerMethodField()
    member_id = serializers.SerializerMethodField()

    class Meta:
        model = SavingTransaction
        fields = (
            'id',
            'saving_id',
            'transaction_id',
            'saving_type',
            'amount',
            'status',
            'submitted_at',
            'member_name',
            'member_id',
        )

    def get_member_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_member_id(self, obj):
        profile = getattr(obj.user, 'member_profile', None)
        return profile.member_id if profile else None