
from django.db import models
from django.conf import settings

class Card(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cards'
    )
    card_number = models.CharField(max_length=16, unique=True)
    holder_name = models.CharField(max_length=100)
    expiry_date = models.CharField(max_length=5)  # Format: MM/YY
    pin_code = models.CharField(max_length=6, default='123456')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def str(self):
        return f"{self.card_number} ({self.user.username})"

    # --- 🔐 PIN tekshirish ---
    def check_pin(self, input_pin):
        return self.pin_code == input_pin  # Ishonchli tizimda bu hash bilan solishtiriladi

    # --- 🔒 Kartani bloklash ---
    def block(self):
        self.is_active = False
        self.save()

    # --- 🔓 Kartani blokdan chiqarish ---
    def unblock(self):
        self.is_active = True
        self.save()

    # --- 🌟 Kartani asosiy qilish ---
    def set_as_primary(self):
        # Avval boshqa kartalarni asosiydan chiqaramiz
        self.user.cards.update(is_primary=False)
        self.is_primary = True
        self.save()