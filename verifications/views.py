from django.db.models import Q
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from members.models import Member
from members.permissions import IsStaffOrAbove
from savings.models import SavingTransaction, SavingsBalance, SavingStatus, SavingType
from .services import approve_saving_transaction, reject_saving_transaction

from .serializers import (
    SavingTransactionListSerializer,
    SavingTransactionDetailSerializer,
    SavingVerifySerializer,
    SavingsBalanceSerializer,
)


class StandardPagination(PageNumberPagination):
    page_size             = 10
    page_size_query_param = 'page_size'
    max_page_size         = 100

    def get_paginated_response(self, data):
        return Response({
            'count':        self.page.paginator.count,
            'total_pages':  self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size':    self.get_page_size(self.request),
            'next':         self.get_next_link(),
            'previous':     self.get_previous_link(),
            'results':      data,
        })


class PendingSavingsListView(APIView):
    permission_classes = [IsStaffOrAbove]

    def get(self, request):
        qs = (
            SavingTransaction.objects
            .select_related('member__user', 'verified_by')
            .order_by('-submitted_at')
        )

        status_param = request.query_params.get('status', 'PENDING').upper()
        if status_param != 'ALL':
            qs = qs.filter(status=status_param)

        saving_type = request.query_params.get('saving_type', '').upper()
        if saving_type in [SavingType.POKOK, SavingType.WAJIB, SavingType.SUKARELA]:
            qs = qs.filter(saving_type=saving_type)

        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(member__full_name__icontains=search)
                | Q(member__user__email__icontains=search)
                | Q(transaction_id__icontains=search)
                | Q(saving_id__icontains=search)
            )

        paginator = StandardPagination()
        page      = paginator.paginate_queryset(qs, request)
        serializer = SavingTransactionListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class SavingVerifyView(APIView):
    permission_classes = [IsStaffOrAbove]

    def _get_saving(self, pk):
        try:
            return SavingTransaction.objects.select_related(
                'member__user', 'verified_by'
            ).get(pk=pk)
        except SavingTransaction.DoesNotExist:
            return None

    def get(self, request, pk):
        saving = self._get_saving(pk)
        if not saving:
            return Response({'error': 'Transaksi tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(SavingTransactionDetailSerializer(saving, context={'request': request}).data)

    def post(self, request, pk):
        saving = self._get_saving(pk)
        if not saving:
            return Response({'error': 'Transaksi tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)

        if saving.status != SavingStatus.PENDING:
            return Response(
                {'error': f'Hanya transaksi PENDING yang dapat diverifikasi. Status saat ini: {saving.status}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SavingVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        action           = serializer.validated_data['action']
        rejection_reason = serializer.validated_data.get('rejection_reason', '')

        try:
            if action == 'approve':
                result = approve_saving_transaction(saving, request.user)
                saving.refresh_from_db()

                type_label = dict(SavingType.choices).get(saving.saving_type, saving.saving_type)
                msg = f'{type_label} berhasil diverifikasi.'
                if result['member_activated']:
                    msg += f' Status anggota diperbarui menjadi ACTIVE. Member ID: {saving.member.member_id}.'

                return Response({
                    'message':          msg,
                    'member_activated': result['member_activated'],
                    'member_id':        saving.member.member_id,
                    'transaction':      SavingTransactionDetailSerializer(saving, context={'request': request}).data,
                    'balance':          SavingsBalanceSerializer(result['balance']).data,
                }, status=status.HTTP_200_OK)

            else:
                reject_saving_transaction(saving, request.user, rejection_reason)
                saving.refresh_from_db()
                return Response({
                    'message':     'Transaksi berhasil ditolak.',
                    'transaction': SavingTransactionDetailSerializer(saving, context={'request': request}).data,
                }, status=status.HTTP_200_OK)

        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class MemberSavingsBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, member_pk):
        user     = request.user
        is_staff = user.role in ['STAFF', 'MANAGER', 'CHAIRMAN']

        if not is_staff:
            try:
                member = user.member
            except Exception:
                return Response({'error': 'Profil tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)
            if member.pk != member_pk:
                return Response({'error': 'Akses ditolak.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            balance = SavingsBalance.objects.select_related('member__user').get(member_id=member_pk)
            return Response(SavingsBalanceSerializer(balance).data)
        except SavingsBalance.DoesNotExist:
            try:
                member_obj = Member.objects.get(pk=member_pk)
            except Member.DoesNotExist:
                return Response({'error': 'Anggota tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)
            return Response({
                'member_name': member_obj.full_name,
                'member_id':   member_obj.member_id,
                'total_pokok': '0.00', 'total_wajib': '0.00',
                'total_sukarela': '0.00', 'total': '0.00', 'last_updated': None,
            })