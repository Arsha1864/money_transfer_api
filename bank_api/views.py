from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Card, Transaction
from django.contrib.auth import get_user_model

User = get_user_model()

class AddCardView(APIView):
    def post(self, request):
        user = request.user
        number = request.data.get("number")
        pin = request.data.get("pin_code")
        if Card.objects.filter(number=number).exists():
            return Response({"error": "Bu karta allaqachon mavjud"}, status=400)
        card = Card.objects.create(owner=user, number=number, pin_code=pin)
        return Response({"success": "Karta yaratildi", "card_id": card.id})

class TransferView(APIView):
    def post(self, request):
        from_number = request.data.get("from_card")
        to_number = request.data.get("to_card")
        amount = float(request.data.get("amount"))

        try:
            from_card = Card.objects.get(number=from_number)
            to_card = Card.objects.get(number=to_number)
        except Card.DoesNotExist:
            return Response({"error": "Karta topilmadi"}, status=404)

        if from_card.balance < amount:
            return Response({"error": "Balansda yetarli mablag‘ yo‘q"}, status=400)

        from_card.balance -= amount
        to_card.balance += amount
        from_card.save()
        to_card.save()

        Transaction.objects.create(from_card=from_card, to_card=to_card, amount=amount)

        return Response({"success": "O‘tkazma amalga oshirildi"})

class BalanceView(APIView):
    def get(self, request, card_number):
        try:
            card = Card.objects.get(number=card_number)
            return Response({"balance": card.balance})
        except Card.DoesNotExist:
            return Response({"error": "Karta topilmadi"}, status=404)

class TransactionHistoryView(APIView):
    def get(self, request, card_number):
        try:
            card = Card.objects.get(number=card_number)
            transactions = Transaction.objects.filter(from_card=card) | Transaction.objects.filter(to_card=card)
            data = [{
                "from": t.from_card.number if t.from_card else None,
                "to": t.to_card.number if t.to_card else None,
                "amount": t.amount,
                "title": t.title,
                "date": t.date
            } for t in transactions.order_by('-date')]
            return Response(data)
        except Card.DoesNotExist:
            return Response({"error": "Karta topilmadi"}, status=404)

class CheckPinView(APIView):
    def post(self, request, card_number):
        pin = request.data.get("pin_code")
        try:
            card = Card.objects.get(number=card_number)
            if card.pin_code == pin:
                return Response({"valid": True})
            else:
                return Response({"valid": False})
        except Card.DoesNotExist:
            return Response({"error": "Karta topilmadi"}, status=404)

class PayUtilityView(APIView):
    def post(self, request):
        card_number = request.data.get("card_number")
        amount = float(request.data.get("amount"))
        service = request.data.get("service", "Kommunal to‘lov")

        try:
            card = Card.objects.get(number=card_number)
        except Card.DoesNotExist:
            return Response({"error": "Karta topilmadi"}, status=404)

        if card.balance < amount:
            return Response({"error": "Balansda yetarli mablag‘ yo‘q"}, status=400)

        card.balance -= amount
        card.save()
        Transaction.objects.create(from_card=card, to_card=None, amount=amount, title=service)
        return Response({"success": f"{service} uchun to‘lov amalga oshirildi"})