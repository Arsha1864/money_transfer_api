from django.db import models
from django.conf import settings


User = settings.AUTH_USER_MODEL

class Card(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    card_type = models.CharField(max_length=10, choices=[("UzCard", "UzCard"), ("Humo", "Humo")])
    is_blocked = models.BooleanField(default=False)
    pin_code = models.CharField(max_length=6, default='12345')
    related_name='transaction_cards'

    def __str__(self):
        return f"{self.card_number} - {self.owner.phone_number}"


class TransferTransaction(models.Model):
    sender = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='sent_transfers')
    receiver = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='received_transfers')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, default="Pul o‘tkazmasi")

    def __str__(self):
        return f"{self.sender.card_number} ➝ {self.receiver.card_number} ({self.amount})"


class TransferPage(models.Model):
    commission = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        help_text="O'tkazma komissiyasi foizda"
    )

    def __str__(self):
        return f"TransferPage (Komissiya: {self.commission}%)"


class SubscriptionTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.amount} so'm"
    
 # class ServicePayment(models.Model):
     # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
     # service_name = models.CharField(max_length=100)  # Elektr, Suv, Internet
    #  account_number = models.CharField(max_length=50)  # hisob raqami yoki abonent ID
    #  amount = models.DecimalField(max_digits=12, decimal_places=2)
    #  date = models.DateTimeField(auto_now_add=True)

    #  def str(self):
        #  return f"{self.service_name} - {self.account_number} - {self.amount}"

class ServicePayment(models.Model):
    SERVICE_CHOICES = [
        ("electricity", "Elektr"),
        ("water", "Suv"),
        ("gas", "Gaz"),
        ("internet", "Internet"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    service_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"{self.user.username} - {self.service_type} - {self.amount}"

class QRToken(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"QR: {self.card.card_number}"

 # transactions/models.py


class NFCTransaction(models.Model):
    sender = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='nfc_sent')
    receiver = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='nfc_received')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="pending")  # pending, success, failed
    external_ref = models.CharField(max_length=100, blank=True, null=True)

    def str(self):
        return f"NFC: {self.sender.card_number} ➝ {self.receiver.card_number} ({self.amount})"
    



class Transaction(models.Model):
    sender_card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='sent_transactions')
    receiver_card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=10, choices=[("QR", "QR"), ("NFC", "NFC")])

    def __str__(self):
        return f"{self.sender_card.card_number} -> {self.receiver_card.card_number} : {self.amount}"
    

class MobilePayment(models.Model):
    OPERATOR_CHOICES = [
        ("Ucell", "Ucell"),
        ("Beeline", "Beeline"),
        ("Mobiuz", "Mobiuz"),
        ("Humans", "Humans"),
        ("Uzmobile", "Uzmobile"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES)
    phone_number = models.CharField(max_length=13)  # +998901234567
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"{self.operator} - {self.phone_number} - {self.amount}"

class TransferProfitLog(models.Model):
    transaction = models.OneToOneField(TransferTransaction, on_delete=models.CASCADE, related_name='profit_log')
    click_fee = models.DecimalField(max_digits=12, decimal_places=2)
    service_fee = models.DecimalField(max_digits=12, decimal_places=2)
    your_profit = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Profit from Tx {self.transaction.id} — {self.your_profit} so'm"
    

class CommissionSetting(models.Model):
    SERVICE_TYPE_CHOICES = [
        ("mobile", "Mobil to‘lov"),
        ("service", "Kommunal xizmat"),
    ]

    service_type = models.CharField(max_length=10, choices=SERVICE_TYPE_CHOICES, unique=True)
    service_fee_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Foydalanuvchidan olinadigan komissiya (%)"
    )
    click_fee_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Click yoki provayder ulushi (%)"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def str(self):
        return f"{self.get_service_type_display()} - {self.service_fee_percent}%"