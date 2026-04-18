from .models import Notification

# ── Registration ───────────────────────────────────────────────────────────

def notify_registration_pending(member):
    """Dipanggil saat member baru berhasil register."""
    Notification.objects.create(
        recipient=member.user,
        type='REGISTRATION',
        title='Pendaftaran Diterima',
        message=(
            'Pendaftaran keanggotaan Anda telah kami terima dan sedang dalam proses review. '
            'Kami akan mengirim notifikasi apabila verifikasi selesai.'
        ),
        redirect_url='/status',
    )


def notify_registration_verified(member):
    """Dipanggil saat staff verifikasi member → VERIFIED."""
    Notification.objects.create(
        recipient=member.user,
        type='REGISTRATION',
        title='Pendaftaran Disetujui',
        message=(
            'Selamat! Pendaftaran keanggotaan Anda telah disetujui. '
            'Silakan lakukan setoran simpanan pokok untuk mengaktifkan keanggotaan.'
        ),
        redirect_url='/dashboard/member',
    )


def notify_registration_rejected(member, reason=''):
    """Dipanggil saat staff tolak registrasi member."""
    message = 'Pendaftaran keanggotaan Anda ditolak.'
    if reason:
        message += f' Alasan: {reason}'
    Notification.objects.create(
        recipient=member.user,
        type='REGISTRATION',
        title='Pendaftaran Ditolak',
        message=message,
        redirect_url='/status',
    )


# ── Savings ────────────────────────────────────────────────────────────────

def notify_saving_received(saving):
    """Dipanggil saat member submit bukti setoran → status PENDING."""
    Notification.objects.create(
        recipient=saving.member.user,
        type='SAVING',
        title='Setoran Diterima',
        message=(
            f'Setoran {saving.saving_type} ({saving.saving_id}) telah kami terima '
            'dan menunggu verifikasi petugas.'
        ),
        redirect_url='/savings',
    )


def notify_saving_verified(saving):
    """Dipanggil saat staff verifikasi setoran → SUCCESS."""
    Notification.objects.create(
        recipient=saving.member.user,
        type='SAVING',
        title='Setoran Terverifikasi',
        message=(
            f'Setoran Anda ({saving.saving_id}) telah berhasil diverifikasi '
            'dan ditambahkan ke saldo simpanan.'
        ),
        redirect_url='/savings',
    )


def notify_saving_rejected(saving, reason=''):
    """Dipanggil saat staff tolak setoran."""
    message = f'Setoran ({saving.saving_id}) tidak dapat diverifikasi.'
    if reason:
        message += f' Alasan: {reason}'
    message += ' Silakan submit ulang dengan bukti transfer yang valid.'
    Notification.objects.create(
        recipient=saving.member.user,
        type='SAVING',
        title='Setoran Ditolak',
        message=message,
        redirect_url='/savings',
    )


# ── Loans ──────────────────────────────────────────────────────────────────

def notify_loan_submitted(loan):
    """Dipanggil saat member submit pengajuan pinjaman."""
    Notification.objects.create(
        recipient=loan.member.user,
        type='LOAN',
        title='Pengajuan Pinjaman Diterima',
        message=(
            f'Pengajuan pinjaman Anda ({loan.loan_id}) telah dikirim '
            'dan menunggu review manajer.'
        ),
        redirect_url=f'/dashboard/member/loans/{loan.id}',
    )


def notify_loan_approved(loan):
    """Dipanggil saat manager approve pinjaman."""
    Notification.objects.create(
        recipient=loan.member.user,
        type='LOAN',
        title='Pinjaman Disetujui',
        message=(
            f'Pengajuan pinjaman Anda ({loan.loan_id}) telah disetujui. '
            'Dana akan segera dicairkan ke rekening bank Anda.'
        ),
        redirect_url=f'/dashboard/member/loans/{loan.id}',
    )


def notify_loan_rejected(loan, reason=''):
    """Dipanggil saat manager tolak pinjaman."""
    message = f'Pengajuan pinjaman Anda ({loan.loan_id}) ditolak.'
    if reason:
        message += f' Alasan: {reason}'
    Notification.objects.create(
        recipient=loan.member.user,
        type='LOAN',
        title='Pinjaman Ditolak',
        message=message,
        redirect_url=f'/dashboard/member/loans/{loan.id}',
    )


def notify_loan_disbursed(loan):
    """Dipanggil saat staff cairkan pinjaman."""
    Notification.objects.create(
        recipient=loan.member.user,
        type='LOAN',
        title='Dana Pinjaman Dicairkan',
        message=(
            f'Dana pinjaman ({loan.loan_id}) telah dicairkan. '
            'Silakan cek rekening bank Anda.'
        ),
        redirect_url=f'/dashboard/member/loans/{loan.id}',
    )


def notify_installment_submitted(installment):
    """Dipanggil saat member submit pembayaran cicilan (via transfer / simpanan)."""
    loan = installment.loan
    Notification.objects.create(
        recipient=loan.member.user,
        type='LOAN',
        title='Pembayaran Cicilan Dikirim',
        message=(
            f'Laporan pembayaran cicilan ke-{installment.installment_number} '
            f'untuk pinjaman {loan.loan_id} telah dikirim '
            'dan menunggu verifikasi petugas.'
        ),
        redirect_url=f'/dashboard/member/loans/{loan.id}',
    )


def notify_installment_recorded(installment):
    """Dipanggil saat staff verifikasi pembayaran cicilan → PAID."""
    loan = installment.loan
    Notification.objects.create(
        recipient=loan.member.user,
        type='LOAN',
        title='Pembayaran Cicilan Terverifikasi',
        message=(
            f'Pembayaran cicilan ke-{installment.installment_number} '
            f'untuk pinjaman {loan.loan_id} telah berhasil diverifikasi.'
        ),
        redirect_url=f'/dashboard/member/loans/{loan.id}',
    )


def notify_installment_rejected(installment, reason=''):
    """Dipanggil saat staff tolak pembayaran cicilan."""
    loan = installment.loan
    message = (
        f'Pembayaran cicilan ke-{installment.installment_number} '
        f'untuk pinjaman {loan.loan_id} ditolak.'
    )
    if reason:
        message += f' Alasan: {reason}'
    message += ' Silakan submit ulang dengan bukti transfer yang valid.'
    Notification.objects.create(
        recipient=loan.member.user,
        type='LOAN',
        title='Pembayaran Cicilan Ditolak',
        message=message,
        redirect_url=f'/dashboard/member/loans/{loan.id}',
    )


def notify_loan_lunas(loan):
    """Dipanggil saat seluruh cicilan pinjaman telah terbayar → LUNAS."""
    Notification.objects.create(
        recipient=loan.member.user,
        type='LOAN',
        title='Pinjaman Lunas',
        message=(
            f'Selamat! Pinjaman Anda ({loan.loan_id}) telah lunas. '
            'Terima kasih telah memenuhi kewajiban pembayaran tepat waktu.'
        ),
        redirect_url=f'/dashboard/member/loans/{loan.id}',
    )


def notify_loan_overdue(loan):
    """Dipanggil saat pinjaman masuk status OVERDUE."""
    Notification.objects.create(
        recipient=loan.member.user,
        type='LOAN',
        title='Pinjaman Anda Overdue',
        message=(
            f'Pinjaman Anda ({loan.loan_id}) telah melewati tanggal jatuh tempo. '
            'Mohon segera lakukan pembayaran untuk menghindari penalti tambahan.'
        ),
        redirect_url=f'/dashboard/member/loans/{loan.id}',
    )


# ── Withdrawals ────────────────────────────────────────────────────────────

def notify_withdrawal_received(withdrawal):
    """Dipanggil saat member submit penarikan simpanan."""
    Notification.objects.create(
        recipient=withdrawal.member.user,
        type='WITHDRAWAL',
        title='Permintaan Penarikan Diterima',
        message=(
            'Permintaan penarikan simpanan Anda telah diterima '
            'dan sedang diproses oleh petugas.'
        ),
        redirect_url='/dashboard/member/withdrawals',
    )


def notify_withdrawal_processed(withdrawal):
    """Dipanggil saat staff proses penarikan → SUCCESS."""
    Notification.objects.create(
        recipient=withdrawal.member.user,
        type='WITHDRAWAL',
        title='Penarikan Diproses',
        message=(
            'Permintaan penarikan simpanan Anda telah diproses. '
            'Dana akan ditransfer ke rekening bank terdaftar.'
        ),
        redirect_url='/dashboard/member/withdrawals',
    )


# ── Resignation ────────────────────────────────────────────────────────────

def notify_resignation_received(resignation):
    """Dipanggil saat member submit penutupan akun."""
    Notification.objects.create(
        recipient=resignation.member.user,
        type='RESIGNATION',
        title='Permintaan Pengunduran Diri Diterima',
        message=(
            'Permintaan pengunduran diri Anda telah diterima '
            'dan menunggu persetujuan manajer.'
        ),
        redirect_url='/dashboard/member/resignation',
    )


def notify_resignation_approved(resignation):
    """Dipanggil saat manager approve penutupan akun."""
    Notification.objects.create(
        recipient=resignation.member.user,
        type='RESIGNATION',
        title='Pengunduran Diri Disetujui',
        message=(
            'Permintaan pengunduran diri Anda telah disetujui. '
            'Pengembalian simpanan akan segera diproses.'
        ),
        redirect_url='/dashboard/member',
    )