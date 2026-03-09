from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('email', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter   = ('role', 'is_active', 'is_staff')
    search_fields = ('email',)
    ordering      = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Role & Status', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_active', 'is_staff'),
        }),
    )
