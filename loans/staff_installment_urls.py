from django.urls import path

from .staff_installment_views import (
    StaffInstallmentStatusUpdateView,
    StaffPendingInstallmentDetailView,
    StaffPendingInstallmentListView,
)

urlpatterns = [
    path('pending/', StaffPendingInstallmentListView.as_view(), name='staff-installment-pending-list'),
    path('pending/<int:pk>/', StaffPendingInstallmentDetailView.as_view(), name='staff-installment-pending-detail'),
    path('<int:pk>/status/', StaffInstallmentStatusUpdateView.as_view(), name='staff-installment-status-update'),
]
