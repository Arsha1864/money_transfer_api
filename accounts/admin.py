from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.timezone import now
from django.utils.html import format_html
from .models import Feedback, Notification
from accounts.models import CustomUser
from .utils import send_push_notification
User = get_user_model()


  


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser

    list_display = ('username', 'phone_number', 'is_verified', 'verification_code', 'is_staff')
    search_fields = ('username', 'phone_number', 'verification_code')
    list_filter = ('is_verified', 'is_staff', 'is_superuser')
    ordering = ('id',)

    readonly_fields= ('last_login', 'date_joined')

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



@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message_short', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def message_short(self, obj):
        return (obj.message[:50] + '...') if obj.message and len(obj.message) > 50 else obj.message
    message_short.short_description = 'Message'



@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "created_at")
    actions = ["send_to_user"]

    def send_to_user(self, request, queryset):
        for notif in queryset:
            username = notif.user
            if not username.fcm_token:
                self.message_user(request, f"❌ {username.username} uchun FCM token topilmadi")
                continue

            success = send_push_notification(
                username.fcm_token, notif.title, notif.body, notif.image
            )

            if success:
                self.message_user(request, f"✅ {username.username} ga yuborildi")
            else:
                self.message_user(request, f"⚠️ {username.username} ga yuborishda xatolik")

    send_to_user.short_description = "Tanlangan xabarlarni Firebase orqali yuborish"


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'comment', 'image_tag')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:50px;"/>', obj.image.url)
        return "-"
    image_tag.short_description = 'Image'
