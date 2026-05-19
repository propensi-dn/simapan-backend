from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q, Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from members.permissions import IsStaffOrAbove
from .models import Loan, LoanStatus, Installment, InstallmentStatus
from .serializers import (
    StaffApprovedLoanSerializer, 
    StaffDisbursedLoanSerializer,
    InstallmentSerializer,
    BankAccountSerializer,
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


class StaffApprovedLoansView(APIView):
    """
    GET /api/staff/loans/approved/

    Return list of loans dengan status APPROVED yang siap dicairkan.
    
    Query Parameters:
    - search: search berdasarkan loan_id atau nama member
    - start_date: filter berdasarkan tanggal approval (format: YYYY-MM-DD)
    - end_date: filter berdasarkan tanggal approval (format: YYYY-MM-DD)
    - page: nomor halaman (default: 1)
    - page_size: jumlah item per halaman (default: 10, max: 100)

    Response:
    {
        "count": 5,
        "total_pages": 1,
        "current_page": 1,
        "page_size": 10,
        "results": [
            {
                "id": 1,
                "loan_id": "LN-2026-001",
                "member_name": "John Doe",
                "category": "MODAL_USAHA",
                "category_display": "Modal Usaha",
                "amount": "5000000.00",
                "tenor": 12,
                "status": "APPROVED",
                "status_display": "Approved",
                "reviewed_at": "2026-04-10T14:30:00Z",
                "application_date": "2026-04-05T10:00:00Z"
            }
        ]
    }
    """
    permission_classes = [IsStaffOrAbove]

    def get(self, request):
        # Base queryset: hanya pinjaman status APPROVED
        queryset = (
            Loan.objects
            .filter(status=LoanStatus.APPROVED)
            .select_related('member')
            .order_by('-reviewed_at', '-application_date')
        )

        # Search berdasarkan loan_id atau nama member
        search = request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(loan_id__icontains=search) |
                Q(member__full_name__icontains=search)
            )

        # Filter berdasarkan range tanggal approval (reviewed_at)
        start_date = request.query_params.get('start_date', '').strip()
        end_date = request.query_params.get('end_date', '').strip()

        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(reviewed_at__date__gte=start_datetime.date())
            except ValueError:
                return Response(
                    {'error': 'Format start_date tidak valid. Gunakan format YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if end_date:
            try:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                # Include end_date hingga akhir hari (23:59:59)
                queryset = queryset.filter(reviewed_at__date__lte=end_datetime.date())
            except ValueError:
                return Response(
                    {'error': 'Format end_date tidak valid. Gunakan format YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Pagination
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = StaffApprovedLoanSerializer(page, many=True)

        # Add summary statistics
        summary_stats = {
            'total_approved_loans': Loan.objects.filter(status=LoanStatus.APPROVED).count(),
            'total_approved_amount': Loan.objects.filter(status=LoanStatus.APPROVED).aggregate(
                total=Sum('amount')
            )['total'] or 0,
        }

        response_data = paginator.get_paginated_response(serializer.data)
        response_data.data['summary'] = summary_stats
        return response_data


class StaffDisbursedLoansView(APIView):
    """
    GET /api/staff/loans/disbursed/

    Return history of loans yang sudah dicairkan (disbursed).
    
    Query Parameters:
    - search: search berdasarkan loan_id atau nama member
    - start_date: filter berdasarkan tanggal pencairan (format: YYYY-MM-DD)
    - end_date: filter berdasarkan tanggal pencairan (format: YYYY-MM-DD)
    - status: filter berdasarkan status (ACTIVE, LUNAS, LUNAS_AFTER_OVERDUE)
    - page: nomor halaman (default: 1)
    - page_size: jumlah item per halaman (default: 10, max: 100)

    Response:
    {
        "count": 3,
        "total_pages": 1,
        "current_page": 1,
        "page_size": 10,
        "results": [
            {
                "id": 1,
                "loan_id": "LN-2026-001",
                "member_name": "John Doe",
                "category": "MODAL_USAHA",
                "category_display": "Modal Usaha",
                "amount": "5000000.00",
                "tenor": 12,
                "status": "ACTIVE",
                "status_display": "Active",
                "approved_at": "2026-04-10T14:30:00Z",
                "disbursed_at": "2026-04-15T10:00:00Z",
                "disbursed_by": "Admin Staff"
            }
        ]
    }
    """
    permission_classes = [IsStaffOrAbove]

    def get(self, request):
        # Base queryset: pinjaman yang sudah dicairkan (disbursed_at tidak null)
        # Termasuk status: ACTIVE, LUNAS, LUNAS_AFTER_OVERDUE, OVERDUE
        queryset = (
            Loan.objects
            .filter(
                status__in=[
                    LoanStatus.ACTIVE,
                    LoanStatus.LUNAS,
                    LoanStatus.LUNAS_AFTER_OVERDUE,
                    LoanStatus.OVERDUE,
                ],
                disbursed_at__isnull=False
            )
            .select_related('member', 'disbursed_by')
            .order_by('-disbursed_at', '-application_date')
        )

        # Search berdasarkan loan_id atau nama member
        search = request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(loan_id__icontains=search) |
                Q(member__full_name__icontains=search)
            )

        # Filter berdasarkan range tanggal pencairan (disbursed_at)
        start_date = request.query_params.get('start_date', '').strip()
        end_date = request.query_params.get('end_date', '').strip()

        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(disbursed_at__date__gte=start_datetime.date())
            except ValueError:
                return Response(
                    {'error': 'Format start_date tidak valid. Gunakan format YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if end_date:
            try:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                queryset = queryset.filter(disbursed_at__date__lte=end_datetime.date())
            except ValueError:
                return Response(
                    {'error': 'Format end_date tidak valid. Gunakan format YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Filter berdasarkan status
        loan_status = request.query_params.get('status', '').strip().upper()
        if loan_status:
            valid_statuses = {
                LoanStatus.ACTIVE,
                LoanStatus.LUNAS,
                LoanStatus.LUNAS_AFTER_OVERDUE,
                LoanStatus.OVERDUE,
            }
            if loan_status not in valid_statuses:
                return Response(
                    {'error': f'Status tidak valid. Gunakan salah satu dari: {", ".join(valid_statuses)}'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            queryset = queryset.filter(status=loan_status)

        # Pagination
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = StaffDisbursedLoanSerializer(page, many=True)

        # Add summary statistics
        disbursed_loans = Loan.objects.filter(
            status__in=[
                LoanStatus.ACTIVE,
                LoanStatus.LUNAS,
                LoanStatus.LUNAS_AFTER_OVERDUE,
                LoanStatus.OVERDUE,
            ],
            disbursed_at__isnull=False
        )
        summary_stats = {
            'total_disbursed_loans': disbursed_loans.count(),
            'total_disbursed_amount': disbursed_loans.aggregate(
                total=Sum('amount')
            )['total'] or 0,
        }

        response_data = paginator.get_paginated_response(serializer.data)
        response_data.data['summary'] = summary_stats
        return response_data


class StaffLoanDisbursementView(APIView):
    """
    POST /api/staff/loans/<id>/disburse/

    Endpoint untuk melakukan pencairan dana (disbursement) untuk pinjaman yang berstatus APPROVED.
    
    Request Body:
    {
        "disbursement_proof": <file> (optional - bukti pencairan)
    }
    
    Response:
    {
        "message": "Pinjaman berhasil dicairkan",
        "loan_id": "LN-2026-001",
        "status": "ACTIVE",
        "member_name": "John Doe",
        "amount": "5000000.00",
        "disbursed_at": "2026-04-15T10:30:45Z"
    }
    """
    permission_classes = [IsStaffOrAbove]

    def post(self, request, pk):
        try:
            loan = Loan.objects.select_related('member', 'member__user').get(pk=pk)
        except Loan.DoesNotExist:
            return Response(
                {'error': 'Pinjaman tidak ditemukan'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Hanya pinjaman status APPROVED yang bisa dicairkan
        if loan.status != LoanStatus.APPROVED:
            return Response(
                {
                    'error': (
                        f'Hanya pinjaman status APPROVED yang dapat dicairkan. '
                        f'Status saat ini: {loan.get_status_display()}.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update loan status
        loan.status = LoanStatus.ACTIVE
        loan.disbursed_by = request.user
        loan.disbursed_at = timezone.now()

        # Handle disbursement proof jika ada
        if 'disbursement_proof' in request.FILES:
            loan.disbursement_proof = request.FILES['disbursement_proof']

        loan.save(update_fields=['status', 'disbursed_by', 'disbursed_at', 'disbursement_proof', 'updated_at'])

        # Create installments for the loan if not already created
        from .services import create_installments
        create_installments(loan)

        # Send notification
        try:
            from notifications.service import notify_loan_disbursed
            notify_loan_disbursed(loan)
        except Exception:
            pass

        return Response({
            'message': 'Pinjaman berhasil dicairkan',
            'loan_id': loan.loan_id,
            'status': loan.status,
            'member_name': loan.member.full_name,
            'amount': str(loan.amount),
            'disbursed_at': loan.disbursed_at,
        }, status=status.HTTP_200_OK)


class StaffLoanDetailView(APIView):
    """
    GET /api/staff/loans/<id>/detail/

    Endpoint untuk mendapatkan detail pinjaman lengkap untuk proses pencairan.
    Mengembalikan:
    - Loan info
    - Installment schedule (preview)
    - Monthly installment amount
    - Member bank account

    Response:
    {
        "id": 1,
        "loan_id": "LN-2026-001",
        "member_name": "John Doe",
        "amount": "5000000.00",
        "tenor": 12,
        "status": "APPROVED",
        "category_display": "Modal Usaha",
        "monthly_installment": "450000.00",
        "total_repayment": "5400000.00",
        "member_bank_account": {
            "id": 1,
            "bank_name": "BCA",
            "account_number": "123456789",
            "account_holder": "John Doe"
        },
        "installment_schedule": [
            {
                "installment_number": 1,
                "due_date": "2026-05-15",
                "amount": "450000.00",
                "principal_component": "416666.67",
                "interest_component": "33333.33"
            },
            ...
        ]
    }
    """
    permission_classes = [IsStaffOrAbove]

    def get(self, request, pk):
        try:
            loan = Loan.objects.select_related('member', 'bank_account').get(pk=pk)
        except Loan.DoesNotExist:
            return Response(
                {'error': 'Pinjaman tidak ditemukan'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Generate preview installment schedule
        from .services import generate_installment_schedule
        schedule = generate_installment_schedule(loan)

        # Get member's primary or first bank account
        member_bank_account = loan.member.bank_accounts.filter(is_primary=True).first()
        if not member_bank_account:
            member_bank_account = loan.member.bank_accounts.first()

        return Response({
            'id': loan.id,
            'loan_id': loan.loan_id,
            'member_name': loan.member.full_name,
            'amount': str(loan.amount),
            'tenor': loan.tenor,
            'status': loan.status,
            'status_display': loan.get_status_display(),
            'category_display': loan.get_category_display(),
            'monthly_installment': str(loan.monthly_installment),
            'total_repayment': str(loan.total_repayment),
            'member_bank_account': BankAccountSerializer(member_bank_account).data if member_bank_account else None,
            'installment_schedule': schedule,
        }, status=status.HTTP_200_OK)


class StaffLoanDashboardView(APIView):
    """
    GET /api/staff/loans/dashboard/

    Endpoint untuk dashboard aktivitas pinjaman staff. Mengembalikan:
    1. Total pinjaman berstatus APPROVED
    2. Aktivitas loan dalam bentuk chart data (6 bulan terakhir)
    3. Total pembayaran angsuran yang belum terverifikasi
    4. Total pinjaman overdue
    5. Daftar pinjaman mendekati due date (2 minggu ke depan)

    Query Parameters:
    - page: nomor halaman untuk upcoming due loans (default: 1)
    - page_size: jumlah item per halaman (default: 10, max: 100)

    Response:
    {
        "summary": {
            "total_approved_loans": 5,
            "total_approved_amount": "25000000.00",
            "total_unverified_installments": 12,
            "total_unverified_amount": "5400000.00",
            "total_overdue_loans": 2,
            "total_overdue_amount": "3200000.00"
        },
        "loan_activities": [
            {"month": "2025-11", "count": 5, "amount": "25000000.00"},
            {"month": "2025-12", "count": 3, "amount": "18000000.00"},
            ...
        ],
        "upcoming_due_loans": {
            "count": 8,
            "total_pages": 1,
            "current_page": 1,
            "page_size": 10,
            "results": [
                {
                    "id": 1,
                    "loan_id": "LN-2026-001",
                    "member_name": "John Doe",
                    "amount": "5000000.00",
                    "remaining_balance": "4200000.00",
                    "next_due_date": "2026-05-15",
                    "status": "ACTIVE",
                    "days_until_due": 7
                },
                ...
            ]
        }
    }
    """
    permission_classes = [IsStaffOrAbove]

    def get(self, request):
        # 1. Total APPROVED loans
        approved_loans = Loan.objects.filter(status=LoanStatus.APPROVED)
        total_approved_loans = approved_loans.count()
        total_approved_amount = approved_loans.aggregate(total=Sum('amount'))['total'] or 0

        # 2. Loan activities - last 6 months
        loan_activities = self._get_loan_activities()

        # 3. Unverified installment payments
        unverified_installments = Installment.objects.filter(
            status=InstallmentStatus.PENDING,
            submitted_at__isnull=False,
            verified_by__isnull=True
        )
        total_unverified_installments = unverified_installments.count()
        total_unverified_amount = unverified_installments.aggregate(total=Sum('amount'))['total'] or 0

        # 4. Overdue loans
        today = timezone.now().date()
        overdue_loans = Loan.objects.filter(
            status=LoanStatus.OVERDUE
        )
        total_overdue_loans = overdue_loans.count()
        total_overdue_amount = overdue_loans.aggregate(total=Sum('amount'))['total'] or 0

        # 5. Upcoming due loans (2 minggu ke depan)
        upcoming_due_loans = self._get_upcoming_due_loans(request)

        return Response({
            'summary': {
                'total_approved_loans': total_approved_loans,
                'total_approved_amount': str(total_approved_amount),
                'total_unverified_installments': total_unverified_installments,
                'total_unverified_amount': str(total_unverified_amount),
                'total_overdue_loans': total_overdue_loans,
                'total_overdue_amount': str(total_overdue_amount),
            },
            'loan_activities': loan_activities,
            'upcoming_due_loans': upcoming_due_loans.data,
        }, status=status.HTTP_200_OK)

    def _get_loan_activities(self):
        """
        Get loan disbursement activities for the last 6 months grouped by month.
        Returns data for bar chart.
        """
        today = timezone.now().date()
        six_months_ago = today - relativedelta(months=6)

        # Get all disbursed loans in the last 6 months
        disbursed_loans = Loan.objects.filter(
            disbursed_at__date__gte=six_months_ago,
            disbursed_at__isnull=False
        ).values(
            'disbursed_at__year',
            'disbursed_at__month'
        ).annotate(
            count=Count('id'),
            amount=Sum('amount')
        ).order_by('disbursed_at__year', 'disbursed_at__month')

        # Create month range for the last 6 months
        activities = []
        for i in range(6):
            month_date = today - relativedelta(months=5-i)
            year = month_date.year
            month = month_date.month
            month_str = month_date.strftime('%Y-%m')

            # Find data for this month
            month_data = next(
                (d for d in disbursed_loans 
                 if d['disbursed_at__year'] == year and d['disbursed_at__month'] == month),
                None
            )

            activities.append({
                'month': month_str,
                'count': month_data['count'] if month_data else 0,
                'amount': str(month_data['amount']) if month_data else '0.00',
            })

        return activities

    def _get_upcoming_due_loans(self, request):
        """
        Get loans approaching due date (within 2 weeks).
        """
        today = timezone.now().date()
        two_weeks_later = today + timedelta(days=14)

        # Get all active/overdue loans with upcoming installments
        loans_with_upcoming = Loan.objects.filter(
            status__in=[LoanStatus.ACTIVE, LoanStatus.OVERDUE],
            disbursed_at__isnull=False
        ).select_related('member').prefetch_related('installments')

        upcoming_loans = []
        for loan in loans_with_upcoming:
            # Get next unpaid installment
            next_installment = loan.installments.filter(
                status__in=[InstallmentStatus.UNPAID, InstallmentStatus.PENDING]
            ).order_by('due_date').first()

            if next_installment and next_installment.due_date <= two_weeks_later:
                days_until_due = (next_installment.due_date - today).days
                upcoming_loans.append({
                    'id': loan.id,
                    'loan_id': loan.loan_id,
                    'member_name': loan.member.full_name,
                    'amount': str(loan.amount),
                    'remaining_balance': str(loan.outstanding_balance),
                    'next_due_date': str(next_installment.due_date),
                    'status': loan.status,
                    'days_until_due': days_until_due,
                })

        # Sort by due date
        upcoming_loans.sort(key=lambda x: x['next_due_date'])

        # Paginate
        paginator = StandardPagination()
        page = paginator.paginate_queryset(upcoming_loans, request)

        return paginator.get_paginated_response(page)
