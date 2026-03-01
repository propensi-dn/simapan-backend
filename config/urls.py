from django.urls import path
from .views import HeroContentView, AboutContentView, FAQListView, ServiceListView

urlpatterns = [
    path('hero/', HeroContentView.as_view(), name='hero-content'),
    path('services/', ServiceListView.as_view(), name='service-list'),
    path('about/', AboutContentView.as_view(), name='about-content'),
    path('faq/', FAQListView.as_view(), name='faq-list'),
]