from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()

# Token valid selama 1 jam (3600 detik)
RESET_TOKEN_MAX_AGE = 60 * 60
SIGNER_SALT = 'simapan-password-reset'


def _get_signer():
    return TimestampSigner(salt=SIGNER_SALT)


def _build_reset_url(token):
    """Generate full URL ke halaman reset password di frontend."""
    frontend_base = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')
    return f'{frontend_base.rstrip("/")}/reset-password?token={token}'


class ForgotPasswordView(APIView):
    """
    POST /api/auth/password/forgot/
    Body: { "email": "user@example.com" }

    Security note: Response selalu success walaupun email tidak ada,
    supaya tidak bisa dipakai untuk email enumeration.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = str(request.data.get('email', '')).strip().lower()

        if not email:
            return Response(
                {'error': 'Email wajib diisi.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Cari user — case insensitive
        try:
            user = User.objects.get(email__iexact=email, is_active=True)
        except User.DoesNotExist:
            user = None

        # Kalau user ada, generate token + kirim email
        if user is not None:
            signer = _get_signer()
            token = signer.sign(str(user.pk))
            reset_url = _build_reset_url(token)

            self._send_reset_email(user, reset_url)

        # Selalu return success message (anti enumeration)
        return Response(
            {
                'message': (
                    'Apabila email Anda terdaftar, link reset password '
                    'telah dikirim ke inbox Anda. Silakan cek email.'
                )
            },
            status=status.HTTP_200_OK,
        )

    def _send_reset_email(self, user, reset_url):
        """Kirim email berisi link reset password."""
        display_name = ''
        try:
            display_name = user.member.full_name
        except Exception:
            display_name = user.email

        subject = '[SI-MAPAN] Reset Password Akun Anda'
        body = (
            f'Yth. {display_name},\n\n'
            'Kami menerima permintaan reset password untuk akun Anda di SI-MAPAN.\n\n'
            'Silakan klik link berikut untuk mengatur password baru:\n\n'
            f'{reset_url}\n\n'
            'Link ini hanya berlaku selama 1 jam. Apabila Anda tidak meminta '
            'reset password, abaikan email ini dan password Anda akan tetap aman.\n\n'
            'Salam,\nTim SI-MAPAN'
        )

        try:
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except Exception:
            pass


class ResetPasswordView(APIView):
    """
    POST /api/auth/password/reset/
    Body: {
        "token": "...",
        "new_password": "...",
        "confirm_password": "..."
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = str(request.data.get('token', '')).strip()
        new_password = request.data.get('new_password', '')
        confirm_password = request.data.get('confirm_password', '')

        # Basic validation
        if not token:
            return Response(
                {'error': 'Token tidak valid.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not new_password or not confirm_password:
            return Response(
                {'error': 'Password baru dan konfirmasi wajib diisi.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_password:
            return Response(
                {'error': 'Password dan konfirmasi password tidak cocok.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verifikasi token
        signer = _get_signer()
        try:
            user_pk = signer.unsign(token, max_age=RESET_TOKEN_MAX_AGE)
        except SignatureExpired:
            return Response(
                {'error': 'Link reset password sudah expired. Silakan request ulang.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except BadSignature:
            return Response(
                {'error': 'Token tidak valid atau sudah digunakan.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ambil user
        try:
            user = User.objects.get(pk=user_pk, is_active=True)
        except User.DoesNotExist:
            return Response(
                {'error': 'User tidak ditemukan.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validasi kekuatan password pakai Django validators
        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            return Response(
                {'error': list(e.messages)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set password baru
        user.set_password(new_password)
        user.save(update_fields=['password'])

        # Kirim email konfirmasi password berhasil diubah
        self._send_confirmation_email(user)

        return Response(
            {
                'message': (
                    'Password berhasil diubah. '
                    'Silakan login dengan password baru Anda.'
                )
            },
            status=status.HTTP_200_OK,
        )

    def _send_confirmation_email(self, user):
        display_name = ''
        try:
            display_name = user.member.full_name
        except Exception:
            display_name = user.email

        subject = '[SI-MAPAN] Password Anda Telah Diubah'
        body = (
            f'Yth. {display_name},\n\n'
            'Password akun SI-MAPAN Anda telah berhasil diubah.\n\n'
            'Apabila Anda merasa tidak melakukan perubahan ini, '
            'segera hubungi petugas kami untuk mengamankan akun Anda.\n\n'
            'Salam,\nTim SI-MAPAN'
        )

        try:
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except Exception:
            pass