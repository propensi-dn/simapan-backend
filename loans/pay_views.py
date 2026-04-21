from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from config.models import CooperativeBank
from members.models import BankAccount
from members.serializers import BankAccountSerializer
from savings.models import SavingsBalance

from .models import Installment, InstallmentStatus, Loan, LoanStatus


class InstallmentPayView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # ── Helpers ──────────────────────────────────────────────────

    def _get_member(self, request):
        try:
            return request.user.member
        except Exception:
            return None

    def _get_installment(self, pk, member):
        """Ambil installment yg dimiliki member (via loan.member)."""
        try:
            return Installment.objects.select_related(
                'loan', 'loan__member'
            ).get(pk=pk, loan__member=member)
        except Installment.DoesNotExist:
            return None

    def _serialize_installment_summary(self, loan, installment):
        return {
            'id': installment.id,
            'loan_id': loan.loan_id,
            'installment_number': installment.installment_number,
            'due_date': installment.due_date,
            'amount': str(installment.amount),
            'status': installment.status,
        }

    # ── GET: data utk halaman Bayar Pinjaman ─────────────────────

    def get(self, request, pk):
        member = self._get_member(request)
        if not member:
            return Response({'error': 'Profil member tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)

        installment = self._get_installment(pk, member)
        if not installment:
            return Response({'error': 'Cicilan tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)

        if installment.status != InstallmentStatus.UNPAID:
            return Response(
                {'error': f'Cicilan ini tidak dapat dibayar. Status saat ini: {installment.status}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        loan = installment.loan
        if loan.status not in [LoanStatus.ACTIVE, LoanStatus.OVERDUE]:
            return Response(
                {'error': f'Pinjaman tidak aktif. Status: {loan.get_status_display()}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Active loans untuk radiobutton table (ACTIVE + OVERDUE)
        active_loans_qs = member.loans.filter(
            status__in=[LoanStatus.ACTIVE, LoanStatus.OVERDUE]
        ).order_by('application_date')

        active_loans = []
        for lo in active_loans_qs:
            next_inst = lo.installments.filter(
                status__in=[InstallmentStatus.UNPAID, InstallmentStatus.PENDING]
            ).order_by('due_date').first()

            active_loans.append({
                'id': lo.id,
                'loan_id': lo.loan_id,
                'category': lo.category,
                'category_display': lo.get_category_display(),
                'amount': str(lo.amount),
                'outstanding_balance': str(lo.outstanding_balance),
                'status': lo.status,
                'status_display': lo.get_status_display(),
                'next_installment_id': next_inst.id if next_inst else None,
                'next_installment_amount': str(next_inst.amount) if next_inst else None,
                'next_due_date': next_inst.due_date if next_inst else None,
            })

        # Payment history (cicilan utk loan yg sama, yg statusnya PAID/PENDING/REJECTED)
        payment_history_qs = Installment.objects.filter(
            loan=loan,
        ).exclude(status=InstallmentStatus.UNPAID).order_by('-submitted_at', '-updated_at')

        payment_history = []
        for inst in payment_history_qs:
            payment_history.append({
                'id': inst.id,
                'loan_id': loan.loan_id,
                'installment_number': inst.installment_number,
                'amount': str(inst.amount),
                'status': inst.status,
                'paid_at': inst.paid_at,
                'submitted_at': inst.submitted_at,
                'transaction_id': inst.transaction_id,
            })

        # Cooperative bank info (tujuan transfer)
        coop_bank = CooperativeBank.objects.filter(is_active=True).first()
        coop_bank_data = None
        if coop_bank:
            coop_bank_data = {
                'bank_name': coop_bank.bank_name,
                'account_number': coop_bank.account_number,
                'account_holder': coop_bank.account_holder,
            }

        # Total simpanan member (khususnya sukarela buat bayar via saldo)
        try:
            balance = member.savings_balance
            savings_data = {
                'total_pokok': str(balance.total_pokok),
                'total_wajib': str(balance.total_wajib),
                'total_sukarela': str(balance.total_sukarela),
                'total_overall': str(balance.total_overall),
            }
        except SavingsBalance.DoesNotExist:
            savings_data = {
                'total_pokok': '0.00',
                'total_wajib': '0.00',
                'total_sukarela': '0.00',
                'total_overall': '0.00',
            }

        # Bank accounts member
        bank_accounts = member.bank_accounts.all()

        return Response({
            'selected_installment': {
                'id': installment.id,
                'loan_id': loan.loan_id,
                'loan_pk': loan.id,
                'installment_number': installment.installment_number,
                'due_date': installment.due_date,
                'amount': str(installment.amount),
                'principal_component': str(installment.principal_component),
                'interest_component': str(installment.interest_component),
                'status': installment.status,
            },
            'active_loans': active_loans,
            'payment_history': payment_history,
            'cooperative_bank': coop_bank_data,
            'savings': savings_data,
            'member_bank_accounts': BankAccountSerializer(bank_accounts, many=True).data,
        })

    # ── POST: submit payment ─────────────────────────────────────

    def post(self, request, pk):
        member = self._get_member(request)
        if not member:
            return Response({'error': 'Profil member tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)

        installment = self._get_installment(pk, member)
        if not installment:
            return Response({'error': 'Cicilan tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)

        # Guard: hanya UNPAID yg bisa dibayar
        if installment.status != InstallmentStatus.UNPAID:
            return Response(
                {'error': f'Cicilan ini sudah tidak bisa dibayar. Status saat ini: {installment.get_status_display()}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        loan = installment.loan
        if loan.status not in [LoanStatus.ACTIVE, LoanStatus.OVERDUE]:
            return Response(
                {'error': f'Pinjaman tidak aktif. Status: {loan.get_status_display()}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment_method = str(request.data.get('payment_method', '')).strip().upper()

        if payment_method not in ['BANK_TRANSFER', 'SAVINGS']:
            return Response(
                {'error': 'Metode pembayaran tidak valid. Gunakan BANK_TRANSFER atau SAVINGS.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── BANK TRANSFER ────────────────────────────────────────
        if payment_method == 'BANK_TRANSFER':
            transfer_proof = request.FILES.get('transfer_proof')
            if not transfer_proof:
                return Response(
                    {'transfer_proof': 'Bukti transfer wajib diunggah.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validasi file size (max 5MB)
            if transfer_proof.size > 5 * 1024 * 1024:
                return Response(
                    {'transfer_proof': 'Ukuran file maksimal 5MB.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validasi content type
            allowed_types = {'image/jpeg', 'image/png', 'image/jpg', 'application/pdf'}
            if hasattr(transfer_proof, 'content_type') and transfer_proof.content_type not in allowed_types:
                return Response(
                    {'transfer_proof': 'Format file harus JPG, PNG, atau PDF.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            bank_account_id = request.data.get('bank_account')
            bank_account = None
            if bank_account_id:
                try:
                    bank_account = BankAccount.objects.get(pk=bank_account_id, member=member)
                except BankAccount.DoesNotExist:
                    return Response(
                        {'bank_account': 'Rekening bank tidak ditemukan atau bukan milik Anda.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            with transaction.atomic():
                installment.status = InstallmentStatus.PENDING
                installment.payment_method = 'BANK_TRANSFER'
                installment.transfer_proof = transfer_proof
                installment.bank_account = bank_account
                installment.submitted_at = timezone.now()

                # Generate transaction ID
                if not installment.transaction_id:
                    seq = Installment.objects.filter(transaction_id__isnull=False).count() + 1
                    installment.transaction_id = f'TRX-INS-{seq:05d}'

                installment.save(update_fields=[
                    'status', 'payment_method', 'transfer_proof',
                    'bank_account', 'submitted_at', 'transaction_id', 'updated_at'
                ])

            # Trigger in-app notif ke member
            try:
                from notifications.service import notify_installment_submitted
                notify_installment_submitted(installment)
            except Exception:
                pass

            return Response({
                'message': 'Laporan pembayaran berhasil dikirim. Menunggu verifikasi petugas.',
                'installment': self._serialize_installment_summary(loan, installment),
                'payment_method': 'BANK_TRANSFER',
            }, status=status.HTTP_200_OK)

        # ── SAVINGS (Sukarela) ───────────────────────────────────
        try:
            balance = SavingsBalance.objects.get(member=member)
        except SavingsBalance.DoesNotExist:
            return Response(
                {'error': 'Anda belum memiliki saldo simpanan.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        installment_amount = Decimal(str(installment.amount))
        current_sukarela = Decimal(str(balance.total_sukarela or 0))

        if current_sukarela < installment_amount:
            return Response(
                {
                    'error': (
                        f'Saldo simpanan sukarela tidak mencukupi. '
                        f'Saldo: Rp {current_sukarela:,.0f}, '
                        f'dibutuhkan: Rp {installment_amount:,.0f}.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # Lock balance row
            balance = SavingsBalance.objects.select_for_update().get(member=member)
            # Re-check after lock
            if Decimal(str(balance.total_sukarela or 0)) < installment_amount:
                return Response(
                    {'error': 'Saldo simpanan sukarela tidak mencukupi.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            balance.total_sukarela = Decimal(str(balance.total_sukarela or 0)) - installment_amount
            balance.save(update_fields=['total_sukarela', 'last_updated'])

            installment.status = InstallmentStatus.PENDING
            installment.payment_method = 'SAVINGS'
            installment.submitted_at = timezone.now()

            if not installment.transaction_id:
                seq = Installment.objects.filter(transaction_id__isnull=False).count() + 1
                installment.transaction_id = f'TRX-INS-{seq:05d}'

            installment.save(update_fields=[
                'status', 'payment_method', 'submitted_at',
                'transaction_id', 'updated_at'
            ])

        # Trigger in-app notif ke member
        try:
            from notifications.service import notify_installment_submitted
            notify_installment_submitted(installment)
        except Exception:
            pass

        return Response({
            'message': 'Pembayaran dari simpanan sukarela berhasil dikirim. Menunggu verifikasi petugas.',
            'installment': self._serialize_installment_summary(loan, installment),
            'payment_method': 'SAVINGS',
            'remaining_sukarela': str(balance.total_sukarela),
        }, status=status.HTTP_200_OK)