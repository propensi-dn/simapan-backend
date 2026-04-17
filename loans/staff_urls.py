from django.urls import path
from .staff_views import StaffApprovedLoansView, StaffDisbursedLoansView, StaffLoanDisbursementView

urlpatterns = [
    path('approved/', StaffApprovedLoansView.as_view(), name='staff-approved-loans'),
    path('disbursed/', StaffDisbursedLoansView.as_view(), name='staff-disbursed-loans'),
    path('<int:pk>/disburse/', StaffLoanDisbursementView.as_view(), name='staff-loan-disburse'),
]
