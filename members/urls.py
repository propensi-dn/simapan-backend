from django.urls import path
from .views import MemberRegisterView, MemberStatusView

urlpatterns = [
    path('register/', MemberRegisterView.as_view(), name='register'),
    path('status/', MemberStatusView.as_view(), name='member-status'),
]