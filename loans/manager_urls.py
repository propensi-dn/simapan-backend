from django.urls import path

from .manager_views import ManagerPendingLoansView, ManagerLoanDetailView, ManagerLoanStatusUpdateView

urlpatterns = [
    path('pending/', ManagerPendingLoansView.as_view(), name='manager-pending-loans'),
    path('<int:pk>/status/', ManagerLoanStatusUpdateView.as_view(), name='manager-loan-status-update'),
    path('<int:pk>/', ManagerLoanDetailView.as_view(), name='manager-loan-detail'),
]
