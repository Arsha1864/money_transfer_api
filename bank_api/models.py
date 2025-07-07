from django.db import models

# Create your models here.
# test_bank_api/models.py
from django.db import models
from django.contrib.auth import get_user_model
from card.models import Card

User = get_user_model()

class Transaction(models.Model):
    from_card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, related_name='outgoing')
    to_card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, related_name='incoming')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    title = models.CharField(max_length=255, default='Pul o‘tkazmasi')
    date = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"{self.from_card} -> {self.to_card} ({self.amount})"