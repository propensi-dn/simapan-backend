from django.urls import path

from .password_reset_views import ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path('forgot/', ForgotPasswordView.as_view(), name='password-forgot'),
    path('reset/', ResetPasswordView.as_view(), name='password-reset'),
]