from rest_framework import serializers
from .models import Card

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = [
            'id', 'user', 'card_number', 'holder_name', 'expiry_date',
            'balance', 'is_active', 'is_primary', 'created_at'
        ]
        read_only_fields = ['id', 'balance', 'created_at']