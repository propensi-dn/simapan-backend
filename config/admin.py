from django.contrib import admin
from .models import CooperativeBank, LandingPageConfig, AboutConfig, FAQ, Service

admin.site.register(CooperativeBank)
admin.site.register(FAQ)
admin.site.register(Service)

@admin.register(LandingPageConfig)
class LandingPageConfigAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False if LandingPageConfig.objects.exists() else True

@admin.register(AboutConfig)
class AboutConfigAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False if AboutConfig.objects.exists() else True