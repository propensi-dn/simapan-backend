from django.urls import path

from config.views import ActiveCooperativeBankAccountView

urlpatterns = [
    path('bank-account/', ActiveCooperativeBankAccountView.as_view(), name='active-bank-account'),
]
