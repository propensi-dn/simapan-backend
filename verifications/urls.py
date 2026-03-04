from django.urls import path

from verifications.views import (
    DepositConfirmView,
    DepositDetailView,
    DepositQueueView,
    PokokConfirmView,
    PokokDetailView,
    PokokQueueView,
)

urlpatterns = [
    # PBI-9: Simpanan Pokok verification
    path('pokok/', PokokQueueView.as_view(), name='pokok-queue'),
    path('pokok/<int:pk>/', PokokDetailView.as_view(), name='pokok-detail'),
    path('pokok/<int:pk>/confirm/', PokokConfirmView.as_view(), name='pokok-confirm'),

    # PBI-12: Simpanan Wajib/Sukarela verification
    path('deposits/', DepositQueueView.as_view(), name='deposit-queue'),
    path('deposits/<int:pk>/', DepositDetailView.as_view(), name='deposit-detail'),
    path('deposits/<int:pk>/confirm/', DepositConfirmView.as_view(), name='deposit-confirm'),
]