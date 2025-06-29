from django.db import models

# Create your models here.
# test_bank_api/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Card(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.CharField(max_length=16, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    pin_code = models.CharField(max_length=6, default='123456')
    is_blocked = models.BooleanField(default=False)

    def str(self):
        return f"{self.number} ({self.owner})"


class Transaction(models.Model):
    from_card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, related_name='outgoing')
    to_card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, related_name='incoming')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    title = models.CharField(max_length=255, default='Pul o‘tkazmasi')
    date = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"{self.from_card} -> {self.to_card} ({self.amount})"