from rest_framework import serializers
from .models import Card

class CardVerifySerializer(serializers.Serializer):
    card_number = serializers.CharField()
    expiry_date = serializers.CharField()
    pin = serializers.CharField()

    def validate(self, attrs):
        # Simulyatsiya qilingan verify logikasi
        from services_api.bank_api import get_card_balance
        balance = get_card_balance(attrs['card_number'], attrs['expiry_date'], attrs['pin'])

        if balance is None:
            raise serializers.ValidationError("Karta ma'lumotlari noto‘g‘ri yoki bank bilan bog‘lanib bo‘lmadi.")

        return {
            "card_number": attrs['card_number'],
            "verified": True,
            "balance": balance
        }