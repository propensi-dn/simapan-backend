from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from users.models import User
from .models import Member, BankAccount
from .utils import add_watermark

class MemberRegisterSerializer(serializers.Serializer):
    # Basic Info
    full_name      = serializers.CharField(max_length=255)
    place_of_birth = serializers.CharField(max_length=100)
    date_of_birth  = serializers.DateField()
    gender         = serializers.ChoiceField(choices=[('M','M'),('F','F')])
    occupation     = serializers.CharField(max_length=100)
    # Contact Info
    phone_number   = serializers.CharField(max_length=20)
    home_address   = serializers.CharField()
    city           = serializers.CharField(max_length=100)
    postal_code    = serializers.CharField(max_length=10)
    # Documents
    nik            = serializers.CharField(max_length=16)
    ktp_image      = serializers.ImageField()
    selfie_image = serializers.ImageField()
    # Account Info
    email          = serializers.EmailField()
    password       = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate_nik(self, value):
        if Member.objects.filter(nik=value).exists():
            raise serializers.ValidationError('NIK sudah terdaftar')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email sudah terdaftar')
        return value
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Password tidak cocok'})
        
        if 'ktp_image' in data and data['ktp_image']:
            data['ktp_image'] = add_watermark(
                data['ktp_image'],
                text="SI-MAPAN"
            )

        if 'selfie_image' in data and data['selfie_image']:
            data['selfie_image'] = add_watermark(
                data['selfie_image'],
                text="SI-MAPAN"
            )

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        email    = validated_data.pop('email')
        password = validated_data.pop('password')
        user     = User.objects.create_user(email=email, password=password)
        member   = Member.objects.create(user=user, **validated_data)
        return member

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'bank_name', 'account_number', 'account_holder', 'is_primary']

class MemberProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    bank_accounts = BankAccountSerializer(many=True, read_only=True)
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            'member_id', 'full_name', 'gender', 'place_of_birth', 
            'date_of_birth', 'nik', 'email', 'phone_number', 
            'home_address', 'profile_picture', 'bank_accounts'
        ]
        # Field yang dilarang diubah sesuai kriteria
        read_only_fields = ['member_id', 'nik', 'email']

    def get_profile_picture(self, obj):
        if obj.selfie_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.selfie_image.url)
            return obj.selfie_image.url
        return None