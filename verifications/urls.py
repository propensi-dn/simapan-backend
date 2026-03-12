from django.urls import path
from .views import PendingSavingsListView, SavingVerifyView, MemberSavingsBalanceView

urlpatterns = [
    path('savings/',                          PendingSavingsListView.as_view(), name='verification-savings-list'),
    path('savings/<int:pk>/',                 SavingVerifyView.as_view(),       name='verification-savings-detail'),
    path('savings/balance/<int:member_pk>/',  MemberSavingsBalanceView.as_view(), name='verification-savings-balance'),
]