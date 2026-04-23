from django.urls import path
from .staff_views import (
    StaffApprovedLoansView, 
    StaffDisbursedLoansView, 
    StaffLoanDisbursementView,
    StaffLoanDetailView,
    StaffLoanDashboardView,
)
from .staff_monitoring_views import (
    StaffLoanMonitoringDetailView,
    StaffLoanInstallmentExportCsvView,
)

urlpatterns = [
    path('dashboard/', StaffLoanDashboardView.as_view(), name='staff-loan-dashboard'),
    path('approved/', StaffApprovedLoansView.as_view(), name='staff-approved-loans'),
    path('disbursed/', StaffDisbursedLoansView.as_view(), name='staff-disbursed-loans'),
    path('<int:pk>/', StaffLoanMonitoringDetailView.as_view(), name='staff-loan-monitoring-detail'),
    path('<int:pk>/export-csv/', StaffLoanInstallmentExportCsvView.as_view(), name='staff-loan-monitoring-export-csv'),
    path('<int:pk>/detail/', StaffLoanDetailView.as_view(), name='staff-loan-detail'),
    path('<int:pk>/disburse/', StaffLoanDisbursementView.as_view(), name='staff-loan-disburse'),
]
