from rest_framework import serializers
from django.contrib.auth import authenticate
from members.models import Member

class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Email atau password salah')
        
        try:
            member = user.member
            if member.status == 'PENDING':
                raise serializers.ValidationError(
                    'Akun kamu belum diverifikasi. Silakan cek status pendaftaran kamu.'
                )
            if member.status == 'REJECTED':
                raise serializers.ValidationError(
                    'Akun kamu ditolak. Silakan hubungi petugas untuk informasi lebih lanjut.'
                )
            if member.status == 'INACTIVE':
                raise serializers.ValidationError(
                    'Akun kamu sudah tidak aktif.'
                )
        except Member.DoesNotExist:
            pass

        data['user'] = user
        return data

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Konfirmasi password tidak cocok.")
        return data
