from rest_framework import serializers
from .models import LandingPageConfig, AboutConfig, FAQ, Service

class LandingPageConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandingPageConfig
        fields = '__all__'

class AboutConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutConfig
        fields = '__all__'

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'