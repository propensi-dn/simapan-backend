from rest_framework import serializers
from .models import Member


class PendingMemberListSerializer(serializers.ModelSerializer):
    """Serializer ringkas untuk daftar calon anggota PENDING."""
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Member
        fields = ['id', 'full_name', 'registration_date', 'nik', 'status', 'email']


class MemberDetailSerializer(serializers.ModelSerializer):
    """Serializer lengkap untuk halaman verifikasi petugas."""
    email = serializers.EmailField(source='user.email', read_only=True)
    ktp_image = serializers.SerializerMethodField()
    selfie_image = serializers.SerializerMethodField()
    verified_by_email = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            'id',
            'full_name',
            'place_of_birth',
            'date_of_birth',
            'gender',
            'occupation',
            'phone_number',
            'home_address',
            'city',
            'postal_code',
            'nik',
            'ktp_image',
            'selfie_image',
            'email',
            'status',
            'rejection_reason',
            'registration_date',
            'verified_by_email',
            'verified_at',
        ]

    def get_ktp_image(self, obj):
        request = self.context.get('request')
        if obj.ktp_image:
            return request.build_absolute_uri(obj.ktp_image.url) if request else obj.ktp_image.url
        return None

    def get_selfie_image(self, obj):
        request = self.context.get('request')
        if obj.selfie_image:
            return request.build_absolute_uri(obj.selfie_image.url) if request else obj.selfie_image.url
        return None

    def get_verified_by_email(self, obj):
        if obj.verified_by:
            return obj.verified_by.email
        return None


class MemberVerifySerializer(serializers.Serializer):
    """Payload untuk approve / reject calon anggota."""
    ACTION_CHOICES = [('approve', 'Approve'), ('reject', 'Reject')]

    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    rejection_reason = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, data):
        if data['action'] == 'reject' and not data.get('rejection_reason', '').strip():
            raise serializers.ValidationError(
                {'rejection_reason': 'Alasan penolakan wajib diisi ketika menolak anggota.'}
            )
        return data
