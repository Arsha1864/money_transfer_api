from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.utils import timezone


   # Custom user manager
class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Foydalanuvchi telefon raqamini kiritishi shart")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)


   # Custom user modeli
class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)  # Qo‘shildi
    phone_number = models.CharField(max_length=13, unique=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    pin_code = models.CharField(max_length=6, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number']  # Superuser yaratishda talab qilinadi

    objects = CustomUserManager()

    def __str__(self):
        return self.username or self.phone_number


# Feedback model
class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fikr #{self.id} - {self.user.phone_number if self.user else 'Anonim'}"


# Javob model
class FeedbackReply(models.Model):
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='replies')
    reply_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Javob: {self.reply_text[:30]}"


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
    
    # models.py
class Card(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    number = models.CharField(max_length=16, unique=True)
    sms_code = models.CharField(max_length=6, default='123456')
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    related_name='account_cards'

    def str(self):
        return f"{self.number} - {self.owner}"