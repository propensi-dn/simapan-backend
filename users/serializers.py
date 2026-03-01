from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs['email']
        password = attrs['password']
        user_model = get_user_model()

        try:
            user = user_model.objects.get(email=email)
        except user_model.DoesNotExist as exc:
            raise serializers.ValidationError('Email atau password salah') from exc

        if not user.check_password(password):
            raise serializers.ValidationError('Email atau password salah')

        if not user.is_active:
            raise serializers.ValidationError('Akun tidak aktif')

        refresh = RefreshToken.for_user(user)
        attrs['user'] = user
        attrs['tokens'] = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate_refresh(self, value):
        if not value:
            raise serializers.ValidationError('Refresh token wajib diisi')
        return value
