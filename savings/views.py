from django.db.models import DecimalField, Sum, Value
from django.db.models.functions import Coalesce
from rest_framework import permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from config.models import CooperativeBankAccount
from config.serializers import CooperativeBankAccountSerializer
from members.models import MemberStatus
from savings.models import SavingStatus, SavingTransaction, SavingType
from savings.serializers import (
	DepositCreateSerializer,
	InitialDepositCreateSerializer,
	SavingTransactionSerializer,
)
from users.models import UserRole


class SavingsPagination(PageNumberPagination):
	page_size = 5
	page_size_query_param = 'page_size'
	max_page_size = 50


class BaseMemberSavingsView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get_member_profile(self, user):
		member_profile = getattr(user, 'member_profile', None)
		if not member_profile:
			return None
		return member_profile

	def ensure_member_role(self, user):
		return user.role == UserRole.MEMBER


class InitialDepositCreateView(BaseMemberSavingsView):
	parser_classes = [MultiPartParser, FormParser]

	def post(self, request):
		if not self.ensure_member_role(request.user):
			return Response({'detail': 'Hanya anggota yang dapat melakukan setoran'}, status=status.HTTP_403_FORBIDDEN)

		member_profile = self.get_member_profile(request.user)
		if not member_profile or member_profile.status != MemberStatus.VERIFIED:
			return Response(
				{'detail': 'Hanya anggota berstatus VERIFIED yang bisa upload simpanan pokok'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		if member_profile.has_paid_pokok:
			return Response(
				{'detail': 'Simpanan pokok sudah pernah dibayarkan dan tidak bisa dikirim ulang'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		serializer = InitialDepositCreateSerializer(data=request.data, context={'request': request})
		serializer.is_valid(raise_exception=True)

		saving = SavingTransaction.objects.filter(
			user=request.user,
			saving_type=SavingType.POKOK,
		).order_by('-submitted_at').first()

		if saving and saving.status == SavingStatus.SUCCESS:
			member_profile.has_paid_pokok = True
			member_profile.save(update_fields=['has_paid_pokok'])
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

		member_profile.has_paid_pokok = True
		member_profile.save(update_fields=['has_paid_pokok'])

		return Response(
			{
				'message': 'Bukti simpanan pokok berhasil dikirim',
				'data': SavingTransactionSerializer(saving).data,
			},
			status=status.HTTP_201_CREATED,
		)


class SavingsDepositCreateView(BaseMemberSavingsView):
	parser_classes = [MultiPartParser, FormParser]

	def post(self, request):
		if not self.ensure_member_role(request.user):
			return Response({'detail': 'Hanya anggota yang dapat melakukan setoran'}, status=status.HTTP_403_FORBIDDEN)

		member_profile = self.get_member_profile(request.user)
		if not member_profile or member_profile.status != MemberStatus.ACTIVE:
			return Response(
				{'detail': 'Hanya anggota berstatus ACTIVE yang bisa menambah simpanan'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		serializer = DepositCreateSerializer(data=request.data, context={'request': request})
		serializer.is_valid(raise_exception=True)
		saving = serializer.save()

		return Response(
			{
				'message': 'Setoran berhasil dikirim dan menunggu verifikasi petugas',
				'data': SavingTransactionSerializer(saving).data,
			},
			status=status.HTTP_201_CREATED,
		)


class SavingsOverviewView(BaseMemberSavingsView):
	def get(self, request):
		if not self.ensure_member_role(request.user):
			return Response({'detail': 'Hanya anggota yang dapat mengakses overview'}, status=status.HTTP_403_FORBIDDEN)

		member_profile = self.get_member_profile(request.user)
		if not member_profile:
			return Response({'detail': 'Profil anggota tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)

		bank_account = CooperativeBankAccount.objects.filter(is_active=True).first()
		bank_data = CooperativeBankAccountSerializer(bank_account).data if bank_account else None

		if member_profile.status not in [MemberStatus.VERIFIED, MemberStatus.ACTIVE]:
			return Response(
				{'detail': 'Status anggota tidak dapat mengakses overview simpanan'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		transactions = SavingTransaction.objects.filter(user=request.user)
		status_filter = request.query_params.get('status')
		if status_filter:
			transactions = transactions.filter(status=status_filter.upper())

		totals_query = SavingTransaction.objects.filter(user=request.user, status=SavingStatus.SUCCESS)
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
		serializer = SavingTransactionSerializer(page, many=True)

		paginated = paginator.get_paginated_response(serializer.data).data
		paginated['member_status'] = member_profile.status
		paginated['totals'] = {
			'wajib': f'{total_wajib}',
			'sukarela': f'{total_sukarela}',
		}
		paginated['bank_account'] = bank_data

		return Response(paginated)

# Create your views here.
