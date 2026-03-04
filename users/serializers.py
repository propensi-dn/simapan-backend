from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers

from members.models import MemberProfile, MemberStatus


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs['email'].strip()
        password = attrs['password']
        user_model = get_user_model()

        try:
            user = user_model.objects.get(
                Q(email__iexact=identifier) | Q(username__iexact=identifier)
            )
        except user_model.DoesNotExist as exc:
            raise serializers.ValidationError('Email atau password salah') from exc

        if not user.check_password(password):
            raise serializers.ValidationError('Email atau password salah')

        if not user.is_active:
            raise serializers.ValidationError('Akun tidak aktif')

        if user.role == 'MEMBER':
            profile = MemberProfile.objects.filter(user=user).first()
            if profile and profile.status == MemberStatus.PENDING:
                raise serializers.ValidationError('Akun belum diverifikasi')
            if profile and profile.status == MemberStatus.REJECTED:
                raise serializers.ValidationError('Akun ditolak')

        attrs['user'] = user
        return attrs
