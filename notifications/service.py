"""
notifications/service.py

Helper functions untuk membuat notifikasi dari views lain.
Import dan panggil fungsi ini setiap kali ada event yang perlu dinotifikasi.

Contoh penggunaan:
    from notifications.service import notify_member_verified
    notify_member_verified(member)
"""

from .models import Notification


# ── Registration ───────────────────────────────────────────────────────────

def notify_registration_pending(member):
    """Dipanggil saat member baru berhasil register."""
    Notification.objects.create(
        recipient=member.user,
        type='REGISTRATION',
        title='Registration Received',
        message=(
            'Your membership registration has been received and is currently under review. '
            'We will notify you once the verification is complete.'
        ),
        redirect_url='/dashboard/member',
    )


def notify_registration_verified(member):
    """Dipanggil saat staff verifikasi member → VERIFIED."""
    Notification.objects.create(
        recipient=member.user,
        type='REGISTRATION',
        title='Registration Approved',
        message=(
            'Congratulations! Your membership registration has been approved. '
            'You can now access all member features.'
        ),
        redirect_url='/dashboard/member',
    )


def notify_registration_rejected(member, reason=''):
    """Dipanggil saat staff tolak registrasi member."""
    message = 'Your membership registration has been rejected.'
    if reason:
        message += f' Reason: {reason}'
    Notification.objects.create(
        recipient=member.user,
        type='REGISTRATION',
        title='Registration Rejected',
        message=message,
        redirect_url='/status',
    )


# ── Savings ────────────────────────────────────────────────────────────────

def notify_saving_received(saving):
    """Dipanggil saat member submit bukti setoran → status PENDING."""
    Notification.objects.create(
        recipient=saving.member.user,
        type='SAVING',
        title='Deposit Received',
        message=(
            f'Your deposit of {saving.saving_type} ({saving.saving_id}) has been received '
            'and is awaiting verification by our staff.'
        ),
        redirect_url=f'/dashboard/member/savings',
    )


def notify_saving_verified(saving):
    """Dipanggil saat staff verifikasi setoran → SUCCESS."""
    Notification.objects.create(
        recipient=saving.member.user,
        type='SAVING',
        title='Deposit Verified',
        message=(
            f'Your deposit ({saving.saving_id}) has been successfully verified '
            f'and added to your savings balance.'
        ),
        redirect_url='/dashboard/member/savings',
    )


def notify_saving_rejected(saving, reason=''):
    """Dipanggil saat staff tolak setoran."""
    message = f'Your deposit ({saving.saving_id}) could not be verified.'
    if reason:
        message += f' Reason: {reason}'
    message += ' Please resubmit with a valid proof of transfer.'
    Notification.objects.create(
        recipient=saving.member.user,
        type='SAVING',
        title='Deposit Rejected',
        message=message,
        redirect_url='/dashboard/member/savings',
    )


# ── Loans ──────────────────────────────────────────────────────────────────

def notify_loan_submitted(loan):
    """Dipanggil saat member submit pengajuan pinjaman."""
    Notification.objects.create(
        recipient=loan.member.user,
        type='LOAN',
        title='Loan Application Submitted',
        message=(
            f'Your loan application ({loan.loan_id}) has been submitted '
            'and is awaiting manager review.'
        ),
        redirect_url=f'/dashboard/member/loans/{loan.id}',
    )


def notify_loan_approved(loan):
    """Dipanggil saat manager approve pinjaman."""
    Notification.objects.create(
        recipient=loan.member.user,
        type='LOAN',
        title='Loan Approved',
        message=(
            f'Your loan application ({loan.loan_id}) has been approved. '
            'The funds will be disbursed to your registered bank account shortly.'
        ),
        redirect_url=f'/dashboard/member/loans/{loan.id}',
    )


def notify_loan_rejected(loan, reason=''):
    """Dipanggil saat manager tolak pinjaman."""
    message = f'Your loan application ({loan.loan_id}) has been rejected.'
    if reason:
        message += f' Reason: {reason}'
    Notification.objects.create(
        recipient=loan.member.user,
        type='LOAN',
        title='Loan Rejected',
        message=message,
        redirect_url=f'/dashboard/member/loans/{loan.id}',
    )


def notify_loan_disbursed(loan):
    """Dipanggil saat staff cairkan pinjaman."""
    Notification.objects.create(
        recipient=loan.member.user,
        type='LOAN',
        title='Loan Disbursed',
        message=(
            f'Your loan ({loan.loan_id}) has been disbursed. '
            'Please check your bank account.'
        ),
        redirect_url=f'/dashboard/member/loans/{loan.id}',
    )


def notify_installment_recorded(installment):
    """Dipanggil saat staff record pembayaran angsuran."""
    Notification.objects.create(
        recipient=installment.loan.member.user,
        type='LOAN',
        title='Installment Payment Recorded',
        message=(
            f'Your installment payment for loan {installment.loan.loan_id} '
            f'has been successfully recorded.'
        ),
        redirect_url=f'/dashboard/member/loans/{installment.loan.id}',
    )


# ── Withdrawals ────────────────────────────────────────────────────────────

def notify_withdrawal_received(withdrawal):
    """Dipanggil saat member submit penarikan simpanan."""
    Notification.objects.create(
        recipient=withdrawal.member.user,
        type='WITHDRAWAL',
        title='Withdrawal Request Received',
        message=(
            f'Your savings withdrawal request has been received '
            'and is being processed by our staff.'
        ),
        redirect_url='/dashboard/member/withdrawals',
    )


def notify_withdrawal_processed(withdrawal):
    """Dipanggil saat staff proses penarikan → SUCCESS."""
    Notification.objects.create(
        recipient=withdrawal.member.user,
        type='WITHDRAWAL',
        title='Withdrawal Processed',
        message=(
            'Your savings withdrawal has been processed. '
            'The funds will be transferred to your registered bank account.'
        ),
        redirect_url='/dashboard/member/withdrawals',
    )


# ── Resignation ────────────────────────────────────────────────────────────

def notify_resignation_received(resignation):
    """Dipanggil saat member submit penutupan akun."""
    Notification.objects.create(
        recipient=resignation.member.user,
        type='RESIGNATION',
        title='Resignation Request Received',
        message=(
            'Your membership resignation request has been received '
            'and is awaiting manager approval.'
        ),
        redirect_url='/dashboard/member/resignation',
    )


def notify_resignation_approved(resignation):
    """Dipanggil saat manager approve penutupan akun."""
    Notification.objects.create(
        recipient=resignation.member.user,
        type='RESIGNATION',
        title='Resignation Approved',
        message=(
            'Your membership resignation has been approved. '
            'Your savings refund will be processed shortly.'
        ),
        redirect_url='/dashboard/member',
    )