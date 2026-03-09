from django.urls import path
from .staff_views import PendingMembersListView, MemberVerifyView

urlpatterns = [
    path('pending/', PendingMembersListView.as_view(), name='staff-pending-members'),
    path('<int:pk>/verify/', MemberVerifyView.as_view(), name='staff-verify-member'),
]
