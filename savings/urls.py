from django.urls import path

from savings.views import InitialDepositCreateView, SavingsDepositCreateView, SavingsOverviewView

urlpatterns = [
    path('overview/', SavingsOverviewView.as_view(), name='savings-overview'),
    path('deposits/pokok/', InitialDepositCreateView.as_view(), name='savings-deposit-pokok'),
    path('deposits/', SavingsDepositCreateView.as_view(), name='savings-deposit'),
]
