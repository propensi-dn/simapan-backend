from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import LandingPageConfig, AboutConfig, FAQ, Service
from .serializers import LandingPageConfigSerializer, AboutConfigSerializer, FAQSerializer, ServiceSerializer

class HeroContentView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        config, _ = LandingPageConfig.objects.get_or_create(id=1)
        return Response(LandingPageConfigSerializer(config).data)

class AboutContentView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        config, _ = AboutConfig.objects.get_or_create(id=1)
        return Response(AboutConfigSerializer(config).data)

class FAQListView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        faqs = FAQ.objects.filter(is_active=True)
        return Response(FAQSerializer(faqs, many=True).data)

class ServiceListView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        services = Service.objects.filter(is_active=True)
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)