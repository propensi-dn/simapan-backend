from django.urls import path
from .pay_views import InstallmentPayView

urlpatterns = [
    path('<int:pk>/pay/', InstallmentPayView.as_view(), name='installment-pay'),
]