from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.timezone import now
from datetime import timedelta
from .models import Feedback, FeedbackReply, Notification
from accounts.models import CustomUser
User = get_user_model()

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser

    list_display = ('username', 'phone_number', 'is_verified', 'verification_code', 'is_staff')
    search_fields = ('username', 'phone_number', 'verification_code')
    list_filter = ('is_verified', 'is_staff', 'is_superuser')
    ordering = ('id',)

    readonly_fields= ('last_lodin', 'date_joined')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Shaxsiy maʼlumotlar', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Ruxsatlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Muhim sanalar', {'fields': ('last_login', 'date_joined')}),
        ('SMS KOD', {'fields': ('verification_code','is_verified')}),
    )

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if request.user.is_superuser:
            readonly_fields.append('verification_code')
        return readonly_fields



class FeedbackReplyInline(admin.TabularInline):
    model = FeedbackReply
    extra = 1
    readonly_fields = ['created_at']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'short_message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('message', 'user__username')
    ordering = ('-created_at',)
    inlines = [FeedbackReplyInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        seven_days_ago = now() - timedelta(days=7)
        return qs.filter(created_at__gte=seven_days_ago)

    def short_message(self, obj):
        return obj.message[:50] + ('...' if len(obj.message) > 50 else '')
    short_message.short_description = 'Fikr matni'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    list_filter = ('created_at',)

