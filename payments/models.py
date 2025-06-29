from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Subscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_payment = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.phone} - {self.last_payment}"