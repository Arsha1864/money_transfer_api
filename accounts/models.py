from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

from django.contrib.auth import get_user_model

   # Custom user manager
class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number,username, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Foydalanuvchi telefon raqamini kiritishi shart")
        user = self.model(phone_number=phone_number,username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number,username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, username, password, **extra_fields)


   # Custom user modeli


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=13, unique=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_agreed = models.BooleanField(default=True)
    pin_code = models.CharField(max_length=128, blank=True, null=True)  # SHIFRLANGAN pin
    has_fingerprint_enabled =models.BooleanField(default=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number']

    objects = CustomUserManager()

    def __str__(self):
        return self.username or self.phone_number

    # PIN bilan ishlovchi maxsus methodlar:
    def set_pin(self, raw_pin):
        self.pin_code = make_password(raw_pin)

    def check_pin(self, raw_pin):
        return check_password(raw_pin, self.pin_code)

# Feedback model
class Feedback(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_feedbacks')
    message = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='feedback_files/', null=True, blank=True)
    is_from_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def str(self):
        return f"{'User' if self.is_from_user else 'Admin'}: {self.message[:30]}"

# Notification model
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.phone_number}"
    
    # accounts/models.py
class VerificationCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def str(self):
        return f"{self.phone} - {self.code}"

