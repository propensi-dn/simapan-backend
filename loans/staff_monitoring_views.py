import csv
from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from members.permissions import IsStaffOrAbove

from .models import Installment, InstallmentStatus, Loan


class InstallmentPagination(PageNumberPagination):
    page_size = 8
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


class StaffLoanMonitoringDetailView(APIView):
    permission_classes = [IsStaffOrAbove]

    def get(self, request, pk):
        try:
            loan = Loan.objects.select_related('member').get(pk=pk)
        except Loan.DoesNotExist:
            return Response({'error': 'Pinjaman tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)

        installments_qs = loan.installments.all().order_by('installment_number')

        total_installments = installments_qs.count()
        paid_installments = installments_qs.filter(status=InstallmentStatus.PAID).count()
        progress_percent = round((paid_installments / total_installments) * 100, 2) if total_installments > 0 else 0

        next_due = installments_qs.filter(
            status__in=[InstallmentStatus.UNPAID, InstallmentStatus.PENDING]
        ).order_by('due_date').first()

        paginator = InstallmentPagination()
        page = paginator.paginate_queryset(installments_qs, request)

        installment_rows = []
        for installment in page:
            installment_rows.append({
                'id': installment.id,
                'installment_number': installment.installment_number,
                'due_date': installment.due_date,
                'amount': str(installment.amount),
                'status': installment.status,
                'status_display': installment.get_status_display(),
                'payment_method': installment.payment_method,
                'submitted_at': installment.submitted_at,
                'paid_at': installment.paid_at,
                'transaction_id': installment.transaction_id,
                'transfer_proof_url': (
                    request.build_absolute_uri(installment.transfer_proof.url)
                    if installment.transfer_proof else None
                ),
            })

        paginated_installments = paginator.get_paginated_response(installment_rows).data

        return Response({
            'loan': {
                'id': loan.id,
                'loan_id': loan.loan_id,
                'member_name': loan.member.full_name,
                'tenor': loan.tenor,
                'status': loan.status,
                'status_display': loan.get_status_display(),
                'amount': str(loan.amount),
                'outstanding_balance': str(loan.outstanding_balance),
                'payment_progress_percent': progress_percent,
                'paid_installments': paid_installments,
                'total_installments': total_installments,
                'next_due_date': next_due.due_date if next_due else None,
            },
            'installments': paginated_installments,
        }, status=status.HTTP_200_OK)


class StaffLoanInstallmentExportCsvView(APIView):
    permission_classes = [IsStaffOrAbove]

    def get(self, request, pk):
        try:
            loan = Loan.objects.select_related('member').get(pk=pk)
        except Loan.DoesNotExist:
            return Response({'error': 'Pinjaman tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)

        installments_qs = loan.installments.all().order_by('installment_number')

        response = HttpResponse(content_type='text/csv')
        filename = f'loan_installments_{loan.loan_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow([
            'Loan ID',
            'Member Name',
            'Installment Number',
            'Due Date',
            'Amount',
            'Status',
            'Payment Method',
            'Submitted At',
            'Paid At',
            'Transaction ID',
            'Transfer Proof URL',
        ])

        for installment in installments_qs:
            writer.writerow([
                loan.loan_id,
                loan.member.full_name,
                installment.installment_number,
                installment.due_date,
                str(installment.amount),
                installment.status,
                installment.payment_method or '',
                installment.submitted_at.isoformat() if installment.submitted_at else '',
                installment.paid_at.isoformat() if installment.paid_at else '',
                installment.transaction_id or '',
                request.build_absolute_uri(installment.transfer_proof.url) if installment.transfer_proof else '',
            ])

        return response
