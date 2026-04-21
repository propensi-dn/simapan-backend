from django.db.models import DecimalField, Sum, Value
from django.db.models.functions import Coalesce
from rest_framework import permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from config.models import CooperativeBank
from savings.models import SavingStatus, SavingTransaction, SavingType
from savings.serializers import (
	DepositCreateSerializer,
	InitialDepositCreateSerializer,
	SavingTransactionSerializer,
)


class SavingsPagination(PageNumberPagination):
	page_size = 5
	page_size_query_param = 'page_size'
	max_page_size = 50


class BaseMemberSavingsView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get_member(self, user):
		return getattr(user, 'member', None)

	def ensure_member_role(self, user):
		return user.role == 'MEMBER'


class InitialDepositCreateView(BaseMemberSavingsView):
	parser_classes = [MultiPartParser, FormParser]

	def post(self, request):
		if not self.ensure_member_role(request.user):
			return Response({'detail': 'Hanya anggota yang dapat melakukan setoran'}, status=status.HTTP_403_FORBIDDEN)

		member = self.get_member(request.user)
		if not member or member.status != 'VERIFIED':
			return Response(
				{'detail': 'Hanya anggota berstatus VERIFIED yang bisa upload simpanan pokok'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		serializer = InitialDepositCreateSerializer(data=request.data, context={'request': request})
		serializer.is_valid(raise_exception=True)

		saving = SavingTransaction.objects.filter(
			member=member,
			saving_type=SavingType.POKOK,
		).order_by('-submitted_at').first()

		if saving and saving.status == SavingStatus.SUCCESS:
			return Response(
				{'detail': 'Simpanan pokok sudah terkonfirmasi sebelumnya'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		validated_data = serializer.validated_data
		if saving:
			saving.transfer_proof = validated_data['transfer_proof']
			saving.member_bank_name = validated_data['member_bank_name']
			saving.member_account_number = validated_data['member_account_number']
			saving.amount = 150000
			saving.status = SavingStatus.PENDING
			saving.rejection_reason = ''
			saving.save()
		else:
			saving = serializer.save()

		# Trigger notifikasi setoran diterima
		try:
			from notifications.service import notify_saving_received
			notify_saving_received(saving)
		except Exception:
			pass

		return Response(
			{
				'message': 'Bukti simpanan pokok berhasil dikirim',
				'data': SavingTransactionSerializer(saving, context={'request': request}).data,
			},
			status=status.HTTP_201_CREATED,
		)


class SavingsDepositCreateView(BaseMemberSavingsView):
	parser_classes = [MultiPartParser, FormParser]

	def post(self, request):
		if not self.ensure_member_role(request.user):
			return Response({'detail': 'Hanya anggota yang dapat melakukan setoran'}, status=status.HTTP_403_FORBIDDEN)

		member = self.get_member(request.user)
		if not member or member.status != 'ACTIVE':
			return Response(
				{'detail': 'Hanya anggota berstatus ACTIVE yang bisa menambah simpanan'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		serializer = DepositCreateSerializer(data=request.data, context={'request': request})
		serializer.is_valid(raise_exception=True)
		saving = serializer.save()

		# Trigger notifikasi setoran diterima
		try:
			from notifications.service import notify_saving_received
			notify_saving_received(saving)
		except Exception:
			pass

		return Response(
			{
				'message': 'Setoran berhasil dikirim dan menunggu verifikasi petugas',
				'data': SavingTransactionSerializer(saving, context={'request': request}).data,
			},
			status=status.HTTP_201_CREATED,
		)


class SavingsOverviewView(BaseMemberSavingsView):
	def get(self, request):
		if not self.ensure_member_role(request.user):
			return Response({'detail': 'Hanya anggota yang dapat mengakses overview'}, status=status.HTTP_403_FORBIDDEN)

		member = self.get_member(request.user)
		if not member:
			return Response({'detail': 'Profil anggota tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)

		bank_account = CooperativeBank.objects.filter(is_active=True).first()
		bank_data = None
		if bank_account:
			bank_data = {
				'bank_name': bank_account.bank_name,
				'account_number': bank_account.account_number,
				'account_holder': bank_account.account_holder,
				'qr_code_url': None,
			}

		if member.status not in ['VERIFIED', 'ACTIVE']:
			return Response(
				{'detail': 'Status anggota tidak dapat mengakses overview simpanan'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		transactions = SavingTransaction.objects.filter(member=member)
		if member.status == 'VERIFIED':
			transactions = transactions.filter(saving_type=SavingType.POKOK)

		status_filter = request.query_params.get('status')
		if status_filter:
			transactions = transactions.filter(status=status_filter.upper())

		totals_query = SavingTransaction.objects.filter(member=member, status=SavingStatus.SUCCESS)
		totals = totals_query.values('saving_type').annotate(
			total=Coalesce(
				Sum('amount'),
				Value(0, output_field=DecimalField(max_digits=14, decimal_places=2)),
			)
		)

		total_wajib = next((item['total'] for item in totals if item['saving_type'] == SavingType.WAJIB), 0)
		total_sukarela = next((item['total'] for item in totals if item['saving_type'] == SavingType.SUKARELA), 0)

		paginator = SavingsPagination()
		page = paginator.paginate_queryset(transactions, request)
		serializer = SavingTransactionSerializer(page, many=True, context={'request': request})

		paginated = paginator.get_paginated_response(serializer.data).data
		paginated['member_status'] = member.status
		paginated['totals'] = {
			'wajib': f'{total_wajib}',
			'sukarela': f'{total_sukarela}',
		}
		paginated['bank_account'] = bank_data

		return Response(paginated)