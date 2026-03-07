from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from .models import Member
from .permissions import IsStaffOrAbove
from .staff_serializers import (
    PendingMemberListSerializer,
    MemberDetailSerializer,
    MemberVerifySerializer,
)


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })


class PendingMembersListView(APIView):
    permission_classes = [IsStaffOrAbove]

    def get(self, request):
        queryset = (
            Member.objects
            .filter(status='PENDING')
            .select_related('user')
            .order_by('-registration_date')
        )

        search = request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search)
                | Q(user__email__icontains=search)
                | Q(nik__icontains=search)
            )

        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = PendingMemberListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class MemberVerifyView(APIView):
    permission_classes = [IsStaffOrAbove]

    def _get_member(self, pk):
        try:
            return Member.objects.select_related('user', 'verified_by').get(pk=pk)
        except Member.DoesNotExist:
            return None

    def get(self, request, pk):
        member = self._get_member(pk)
        if not member:
            return Response(
                {'error': 'Anggota tidak ditemukan.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = MemberDetailSerializer(member, context={'request': request})
        return Response(serializer.data)

    def post(self, request, pk):
        member = self._get_member(pk)
        if not member:
            return Response(
                {'error': 'Anggota tidak ditemukan.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if member.status != 'PENDING':
            return Response(
                {
                    'error': (
                        f'Hanya anggota dengan status PENDING yang dapat diverifikasi. '
                        f'Status saat ini: {member.status}.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = MemberVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        action = serializer.validated_data['action']
        rejection_reason = serializer.validated_data.get('rejection_reason', '')

        if action == 'approve':
            member.status = 'VERIFIED'
            member.rejection_reason = None
        else:
            member.status = 'REJECTED'
            member.rejection_reason = rejection_reason

        member.verified_by = request.user
        member.verified_at = timezone.now()
        member.save(update_fields=['status', 'rejection_reason', 'verified_by', 'verified_at'])

        self._send_status_email(member, action)

        updated_serializer = MemberDetailSerializer(member, context={'request': request})
        return Response(
            {
                'message': (
                    'Anggota berhasil diverifikasi.'
                    if action == 'approve'
                    else 'Anggota berhasil ditolak.'
                ),
                'member': updated_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def _send_status_email(self, member, action):
        """Kirim email notifikasi perubahan status ke calon anggota."""
        email = member.user.email

        if action == 'approve':
            subject = 'Status Keanggotaan Anda Telah Diverifikasi – SI-MAPAN'
            body = (
                f'Yth. {member.full_name},\n\n'
                'Selamat! Pendaftaran keanggotaan Anda di SI-MAPAN telah diverifikasi.\n'
                'Status keanggotaan Anda sekarang adalah VERIFIED.\n\n'
                'Silakan login ke aplikasi SI-MAPAN untuk melanjutkan proses keanggotaan Anda.\n\n'
                'Terima kasih telah mendaftar.\n\n'
                'Salam,\n'
                'Tim SI-MAPAN'
            )
        else:
            subject = 'Status Keanggotaan Anda Ditolak – SI-MAPAN'
            body = (
                f'Yth. {member.full_name},\n\n'
                'Mohon maaf, pendaftaran keanggotaan Anda di SI-MAPAN tidak dapat disetujui.\n'
                f'Alasan penolakan: {member.rejection_reason}\n\n'
                'Apabila ada pertanyaan lebih lanjut, silakan hubungi petugas kami.\n\n'
                'Salam,\n'
                'Tim SI-MAPAN'
            )

        try:
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True,
            )
        except Exception:
            # Kegagalan pengiriman email tidak boleh mengganggu proses verifikasi
            pass
