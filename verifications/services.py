"""
Business logic layer for verification workflows.

Separating this from views keeps the code testable and avoids fat views.
"""
import logging
from decimal import Decimal

from django.db import transaction

from members.models import MemberProfile, MemberStatus
from savings.models import SavingStatus, SavingTransaction, SavingType
from verifications.models import VerificationLog

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper: generate member ID
# ---------------------------------------------------------------------------

def _generate_member_id() -> str:
    """
    Generates next member ID in format #MBR-{urutan-member} (zero-padded 5 digits).
    Uses SELECT FOR UPDATE inside a transaction to prevent race conditions.
    """
    last = (
        MemberProfile.objects.select_for_update()
        .exclude(member_id__isnull=True)
        .exclude(member_id__exact='')
        .order_by('-member_id')
        .first()
    )
    if last and last.member_id:
        try:
            # Extract numeric part: #MBR-00001 → 1
            seq = int(last.member_id.replace('#MBR-', ''))
        except ValueError:
            seq = 0
    else:
        seq = 0
    return f'#MBR-{seq + 1:05d}'


# ---------------------------------------------------------------------------
# PBI-9: Approve/Reject simpanan POKOK  →  activates member
# ---------------------------------------------------------------------------

@transaction.atomic
def process_pokok_verification(
    *,
    saving: SavingTransaction,
    staff,
    action: str,
    rejection_reason: str = '',
) -> dict:
    """
    Confirms or rejects a POKOK saving transaction.

    On APPROVE:
      - saving.status → SUCCESS
      - member.status VERIFIED → ACTIVE
      - member.member_id generated (format: #MBR-{n})
      - VerificationLog created

    On REJECT:
      - saving.status → REJECTED
      - saving.rejection_reason stored
      - member.has_paid_pokok reset to False so member can re-upload
      - VerificationLog created

    Returns a dict with 'action', 'member_id' (if approved), 'message'.
    """
    if saving.saving_type != SavingType.POKOK:
        raise ValueError('Transaksi bukan simpanan pokok')

    if saving.status != SavingStatus.PENDING:
        raise ValueError(
            f'Transaksi sudah berstatus {saving.status} dan tidak bisa diubah lagi'
        )

    member_profile: MemberProfile = getattr(saving.user, 'member_profile', None)
    if not member_profile:
        raise ValueError('Profil anggota tidak ditemukan')

    if member_profile.status != MemberStatus.VERIFIED:
        raise ValueError(
            f'Status anggota harus VERIFIED, saat ini: {member_profile.status}'
        )

    log_kwargs = dict(
        staff=staff,
        saving_transaction=saving,
        action=action.upper(),
        rejection_reason=rejection_reason,
    )

    if action == 'approve':
        # 1. Generate member ID
        new_member_id = _generate_member_id()

        # 2. Update saving
        saving.status = SavingStatus.SUCCESS
        saving.rejection_reason = ''
        saving.save(update_fields=['status', 'rejection_reason', 'updated_at'])

        # 3. Activate member
        member_profile.status = MemberStatus.ACTIVE
        member_profile.member_id = new_member_id
        member_profile.has_paid_pokok = True
        member_profile.save(update_fields=['status', 'member_id', 'has_paid_pokok', 'updated_at'])

        # 4. Audit log
        VerificationLog.objects.create(**log_kwargs)

        logger.info(
            'PBI-9 APPROVE: staff=%s saving=%s member=%s new_id=%s',
            staff.email, saving.transaction_id, saving.user.email, new_member_id,
        )

        return {
            'action': 'approved',
            'member_id': new_member_id,
            'message': f'Anggota berhasil diaktifkan. Member ID: {new_member_id}',
        }

    else:  # reject
        # 1. Update saving
        saving.status = SavingStatus.REJECTED
        saving.rejection_reason = rejection_reason
        saving.save(update_fields=['status', 'rejection_reason', 'updated_at'])

        # 2. Reset so member can re-upload
        member_profile.has_paid_pokok = False
        member_profile.save(update_fields=['has_paid_pokok', 'updated_at'])

        # 3. Audit log
        VerificationLog.objects.create(**log_kwargs)

        logger.info(
            'PBI-9 REJECT: staff=%s saving=%s reason=%s',
            staff.email, saving.transaction_id, rejection_reason,
        )

        return {
            'action': 'rejected',
            'member_id': None,
            'message': 'Simpanan pokok ditolak. Anggota dapat mengupload ulang bukti transfer.',
        }


# ---------------------------------------------------------------------------
# PBI-12: Approve/Reject simpanan WAJIB / SUKARELA
# ---------------------------------------------------------------------------

@transaction.atomic
def process_deposit_verification(
    *,
    saving: SavingTransaction,
    staff,
    action: str,
    rejection_reason: str = '',
    reviewed_amount: Decimal | None = None,
) -> dict:
    """
    Confirms or rejects a WAJIB/SUKARELA saving transaction.

    On APPROVE:
      - If reviewed_amount is given, saving.amount is updated first (Review Setoran)
      - saving.status → SUCCESS
      - VerificationLog created (with reviewed_amount if changed)

    On REJECT:
      - saving.status → REJECTED
      - saving.rejection_reason stored
      - VerificationLog created

    Returns a dict with 'action', 'message', 'final_amount'.
    """
    if saving.saving_type not in {SavingType.WAJIB, SavingType.SUKARELA}:
        raise ValueError('Transaksi bukan simpanan wajib/sukarela')

    if saving.status != SavingStatus.PENDING:
        raise ValueError(
            f'Transaksi sudah berstatus {saving.status} dan tidak bisa diubah lagi'
        )

    log_kwargs = dict(
        staff=staff,
        saving_transaction=saving,
        action=action.upper(),
        rejection_reason=rejection_reason,
        reviewed_amount=reviewed_amount,
    )

    if action == 'approve':
        final_amount = saving.amount

        # Review Setoran: staff overrides the amount
        if reviewed_amount is not None and reviewed_amount != saving.amount:
            saving.amount = reviewed_amount
            final_amount = reviewed_amount

        saving.status = SavingStatus.SUCCESS
        saving.rejection_reason = ''
        saving.save(update_fields=['amount', 'status', 'rejection_reason', 'updated_at'])

        VerificationLog.objects.create(**log_kwargs)

        logger.info(
            'PBI-12 APPROVE: staff=%s saving=%s type=%s amount=%s',
            staff.email, saving.transaction_id, saving.saving_type, final_amount,
        )

        return {
            'action': 'approved',
            'final_amount': str(final_amount),
            'message': 'Setoran berhasil dikonfirmasi dan saldo anggota telah diperbarui.',
        }

    else:  # reject
        saving.status = SavingStatus.REJECTED
        saving.rejection_reason = rejection_reason
        saving.save(update_fields=['status', 'rejection_reason', 'updated_at'])

        VerificationLog.objects.create(**log_kwargs)

        logger.info(
            'PBI-12 REJECT: staff=%s saving=%s reason=%s',
            staff.email, saving.transaction_id, rejection_reason,
        )

        return {
            'action': 'rejected',
            'final_amount': None,
            'message': 'Setoran ditolak.',
        }