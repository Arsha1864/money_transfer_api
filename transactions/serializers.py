from rest_framework import serializers
from django.db import transaction
from .models import (
    SubscriptionTransaction,
    TransferTransaction,
    Card,
    Transaction,
    QRToken,
    NFCTransaction,
    ServicePayment,
    MobilePayment,
)


class SubscriptionTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionTransaction
        fields = '__all___'
        read_only_fields = ['user', 'date']
        read_only=True


class ServicePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePayment
        fields = ['id', 'service_name', 'account_number', 'amount', 'date']


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferTransaction
        fields = ['sender', 'receiver', 'amount', 'title']

    def validate(self, data):
        sender = data['sender']
        receiver = data['receiver']
        amount = data['amount']

        if sender == receiver:
            raise serializers.ValidationError("Jo‘natuvchi va qabul qiluvchi kartalar bir xil bo‘lishi mumkin emas.")

        if sender.is_blocked:
            raise serializers.ValidationError("Jo‘natuvchi karta bloklangan.")

        if receiver.is_blocked:
            raise serializers.ValidationError("Qabul qiluvchi karta bloklangan.")

        if sender.balance < amount:
            raise serializers.ValidationError("Jo‘natuvchi kartada yetarli mablag‘ mavjud emas.")

        return data

    def create(self, validated_data):
        sender = validated_data['sender']
        receiver = validated_data['receiver']
        amount = validated_data['amount']

        with transaction.atomic():
            sender.balance -= amount
            receiver.balance += amount
            sender.save()
            receiver.save()

            return TransferTransaction.objects.create(**validated_data)


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = 'all'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = 'all'

    def validate(self, data):
        sender = data['sender_card']
        receiver = data['receiver_card']
        amount = data['amount']
        method = data['method']

        if sender == receiver:
            raise serializers.ValidationError("O‘z-o‘ziga to‘lov qilish mumkin emas.")

        if sender.is_blocked or receiver.is_blocked:
            raise serializers.ValidationError("Bloklangan kartalardan foydalanib bo‘lmaydi.")

        if sender.balance < amount:
            raise serializers.ValidationError("Yetarli balans mavjud emas.")

        if method not in ['QR', 'NFC']:
            raise serializers.ValidationError("Noto‘g‘ri to‘lov usuli.")

        return data

    def create(self, validated_data):
        sender = validated_data['sender_card']
        receiver = validated_data['receiver_card']
        amount = validated_data['amount']

        with transaction.atomic():
            sender.balance -= amount
            receiver.balance += amount
            sender.save()
            receiver.save()

            return Transaction.objects.create(**validated_data)


class QRTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRToken
        fields = 'all'

        # transactions/serializers.py


class NFCTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NFCTransaction
        fields = 'all'
        read_only_fields = ['timestamp', 'status', 'external_ref']


class MobilePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobilePayment
        fields = 'all'