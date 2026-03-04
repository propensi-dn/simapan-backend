from django.contrib import admin

from members.models import MemberProfile


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'status', 'member_id', 'created_at')
	list_filter = ('status',)
	search_fields = ('user__email', 'member_id')

# Register your models here.
