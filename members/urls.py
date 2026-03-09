from django.urls import path
from .views import MemberRegisterView, MemberStatusView, MemberProfileView, MemberBankAccountView, MemberBankAccountDetailView

urlpatterns = [
    path('register/', MemberRegisterView.as_view(), name='register'),
    path('status/', MemberStatusView.as_view(), name='member-status'),
    path('profile/', MemberProfileView.as_view(), name='member-profile'),
    path('bank-accounts/', MemberBankAccountView.as_view(), name='member-bank-accounts'),
    path('bank-accounts/<int:pk>/', MemberBankAccountDetailView.as_view(), name='member-bank-account-detail'),
]