"""
Views for PBI-9 and PBI-12 — staff verification endpoints.

URL layout (set in verifications/urls.py):
  GET  /api/verifications/pokok/              → list PENDING pokok transactions       (PBI-9)
  GET  /api/verifications/pokok/<id>/         → detail of one pokok transaction       (PBI-9)
  POST /api/verifications/pokok/<id>/confirm/ → approve or reject pokok              (PBI-9)

  GET  /api/verifications/deposits/              → list PENDING wajib/sukarela        (PBI-12)
  GET  /api/verifications/deposits/<id>/         → detail of one deposit              (PBI-12)
  POST /api/verifications/deposits/<id>/confirm/ → approve or reject deposit          (PBI-12)
"""
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from savings.models import SavingStatus, SavingTransaction, SavingType
from verifications.permissions import IsStaffOrAbove
from verifications.serializers import (
    DepositConfirmSerializer,
    DepositQueueSerializer,
    PokokConfirmSerializer,
    PokokQueueSerializer,
    TransactionDetailSerializer,
)
from verifications.services import process_deposit_verification, process_pokok_verification


class VerificationPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50


# ============================================================
# PBI-9  – Simpanan Pokok Verification
# ============================================================

class PokokQueueView(APIView):
    """
    GET /api/verifications/pokok/
    Returns paginated list of PENDING simpanan pokok transactions.
    Supports ?search=<name|email|transaction_id>
    """
    permission_classes = [IsStaffOrAbove]

    def get(self, request):
        qs = (
            SavingTransaction.objects
            .select_related('user', 'user__member_profile')
            .filter(saving_type=SavingType.POKOK, status=SavingStatus.PENDING)
        )

        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(user__email__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(transaction_id__icontains=search)
            )

        paginator = VerificationPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = PokokQueueSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class PokokDetailView(APIView):
    """
    GET /api/verifications/pokok/<id>/
    Full detail of a simpanan pokok transaction for staff review.
    """
    permission_classes = [IsStaffOrAbove]

    def get(self, request, pk: int):
        saving = get_object_or_404(
            SavingTransaction.objects.select_related('user', 'user__member_profile'),
            pk=pk,
            saving_type=SavingType.POKOK,
        )
        serializer = TransactionDetailSerializer(saving, context={'request': request})
        return Response(serializer.data)


class PokokConfirmView(APIView):
    """
    POST /api/verifications/pokok/<id>/confirm/
    Body: { "action": "approve" | "reject", "rejection_reason": "..." }

    PBI-9 core action:
    - approve → member VERIFIED → ACTIVE, member_id generated
    - reject  → saving REJECTED, member can re-upload
    """
    permission_classes = [IsStaffOrAbove]

    def post(self, request, pk: int):
        saving = get_object_or_404(
            SavingTransaction.objects.select_related('user', 'user__member_profile'),
            pk=pk,
            saving_type=SavingType.POKOK,
        )

        serializer = PokokConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = process_pokok_verification(
                saving=saving,
                staff=request.user,
                action=serializer.validated_data['action'],
                rejection_reason=serializer.validated_data.get('rejection_reason', ''),
            )
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        # Return updated saving detail alongside the result
        saving.refresh_from_db()
        detail = TransactionDetailSerializer(saving, context={'request': request}).data

        return Response(
            {
                **result,
                'transaction': detail,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# PBI-12 – Simpanan Wajib / Sukarela Verification
# ============================================================

class DepositQueueView(APIView):
    """
    GET /api/verifications/deposits/
    Returns paginated list of PENDING wajib/sukarela transactions.
    Supports ?search=<name|member_id|transaction_id>&saving_type=WAJIB|SUKARELA
    """
    permission_classes = [IsStaffOrAbove]

    def get(self, request):
        qs = (
            SavingTransaction.objects
            .select_related('user', 'user__member_profile')
            .filter(
                saving_type__in=[SavingType.WAJIB, SavingType.SUKARELA],
                status=SavingStatus.PENDING,
            )
        )

        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(user__email__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__member_profile__member_id__icontains=search)
                | Q(transaction_id__icontains=search)
            )

        saving_type = request.query_params.get('saving_type', '').upper()
        if saving_type in {SavingType.WAJIB, SavingType.SUKARELA}:
            qs = qs.filter(saving_type=saving_type)

        paginator = VerificationPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = DepositQueueSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class DepositDetailView(APIView):
    """
    GET /api/verifications/deposits/<id>/
    Full detail of a wajib/sukarela deposit for staff review.
    """
    permission_classes = [IsStaffOrAbove]

    def get(self, request, pk: int):
        saving = get_object_or_404(
            SavingTransaction.objects.select_related('user', 'user__member_profile'),
            pk=pk,
            saving_type__in=[SavingType.WAJIB, SavingType.SUKARELA],
        )
        serializer = TransactionDetailSerializer(saving, context={'request': request})
        return Response(serializer.data)


class DepositConfirmView(APIView):
    """
    POST /api/verifications/deposits/<id>/confirm/
    Body: {
      "action": "approve" | "reject",
      "rejection_reason": "...",         # required on reject
      "reviewed_amount": 125000          # optional, only on approve (Review Setoran feature)
    }

    PBI-12 core action:
    - approve → saving SUCCESS, member balance updated (tracked by SavingTransaction status)
    - reject  → saving REJECTED, reason stored
    """
    permission_classes = [IsStaffOrAbove]

    def post(self, request, pk: int):
        saving = get_object_or_404(
            SavingTransaction.objects.select_related('user', 'user__member_profile'),
            pk=pk,
            saving_type__in=[SavingType.WAJIB, SavingType.SUKARELA],
        )

        serializer = DepositConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = process_deposit_verification(
                saving=saving,
                staff=request.user,
                action=serializer.validated_data['action'],
                rejection_reason=serializer.validated_data.get('rejection_reason', ''),
                reviewed_amount=serializer.validated_data.get('reviewed_amount'),
            )
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        saving.refresh_from_db()
        detail = TransactionDetailSerializer(saving, context={'request': request}).data

        return Response(
            {
                **result,
                'transaction': detail,
            },
            status=status.HTTP_200_OK,
        )