from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from savings.models import SavingTransaction, SavingsBalance, SavingType, SavingStatus
from notifications.service import notify_saving_verified, notify_saving_rejected


@transaction.atomic
def approve_saving_transaction(saving: SavingTransaction, staff_user) -> dict:
    if saving.status == SavingStatus.SUCCESS:
        raise ValueError('Transaksi ini sudah diverifikasi sebelumnya.')

    saving.status           = SavingStatus.SUCCESS
    saving.verified_by      = staff_user
    saving.rejection_reason = ''
    saving.save(update_fields=['status', 'verified_by', 'rejection_reason'])

    balance, _ = SavingsBalance.objects.select_for_update().get_or_create(
        member=saving.member
    )

    member_activated = False

    if saving.saving_type == SavingType.POKOK:
        balance.total_pokok = (balance.total_pokok or Decimal('0')) + saving.amount
        balance.save(update_fields=['total_pokok', 'last_updated'])

        member = saving.member
        if member.status == 'VERIFIED':
            member.status = 'ACTIVE'
            member.save(update_fields=['status'])
            member_activated = True

            if not member.member_id:
                active_count = type(member).objects.filter(
                    status='ACTIVE', member_id__isnull=False
                ).count()
                member.member_id = f'MBR-{active_count:04d}'
                member.save(update_fields=['member_id'])

    elif saving.saving_type == SavingType.WAJIB:
        balance.total_wajib = (balance.total_wajib or Decimal('0')) + saving.amount
        balance.save(update_fields=['total_wajib', 'last_updated'])

    elif saving.saving_type == SavingType.SUKARELA:
        balance.total_sukarela = (balance.total_sukarela or Decimal('0')) + saving.amount
        balance.save(update_fields=['total_sukarela', 'last_updated'])

    notify_saving_verified(saving)

    return {'member_activated': member_activated, 'balance': balance}


@transaction.atomic
def reject_saving_transaction(saving: SavingTransaction, staff_user, reason: str) -> None:
    if saving.status == SavingStatus.SUCCESS:
        raise ValueError('Transaksi yang sudah SUCCESS tidak bisa ditolak.')

    saving.status           = SavingStatus.REJECTED
    saving.verified_by      = staff_user
    saving.rejection_reason = reason
    saving.save(update_fields=['status', 'verified_by', 'rejection_reason'])

    notify_saving_rejected(saving, reason)