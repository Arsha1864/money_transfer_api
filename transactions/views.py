from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, permissions
from django.db import transaction
import requests

from services_api.bank_api import transfer_between_cards  # Soxta API funktsiyasi
from decimal import Decimal
from .utils import calculate_fees
from django.db.models import Sum


from services_api.bank_api import pay_with_qr  # Soxta API funksiyasi
from services_api.bank_api import transfer_funds  # Shu yerga import

from card.models import Card
from .models import (
    TransferTransaction, SubscriptionTransaction,MobilePayment,TransferProfitLog,
     QRToken, Transaction,NFCTransaction, ServicePayment
)
from .serializers import (
    TransferSerializer, SubscriptionTransactionSerializer,NFCTransactionSerializer, ServicePaymentSerializer,
    TransactionSerializer,MobilePaymentSerializer,QRTokenSerializer
)


class TransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        card = request.GET.get('card')
        date = request.GET.get('date')

        transactions = TransferTransaction.objects.filter(sender__user=user)

        if card:
            transactions = transactions.filter(sender__number=card)

        if date:
            transactions = transactions.filter(date__date=date)

        serializer = TransferSerializer(transactions.order_by('-date'), many=True)
        return Response(serializer.data)

    # Django DRF view'da:
def get_queryset(self):
    queryset = super().get_queryset()
    tx_type = self.request.query_params.get('type')
    if tx_type == 'income':
        queryset = queryset.filter(is_incoming=True)
    elif tx_type == 'expense':
        queryset = queryset.filter(is_incoming=False)
    return queryset


class TransferAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            sender_card = serializer.validated_data['sender']
            receiver_card = serializer.validated_data['receiver']
            amount = serializer.validated_data['amount']

            if sender_card.user != request.user:
                return Response({"error": "Faqat o‘z kartalaringizdan pul o‘tkaza olasiz."},
                                status=status.HTTP_403_FORBIDDEN)

            # SOXTA API chaqiruvi
            result = transfer_funds(sender_card.card_number, receiver_card.card_number, amount)

            if result["success"]:
                # Ixtiyoriy: tarixga yozib qo‘yish uchun bazaga saqlash
                serializer.save()
                return Response({"success": result["message"]}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": result["message"]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubscriptionTransactionListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        transactions = SubscriptionTransaction.objects.filter(user=user).order_by('-date')
        serializer = SubscriptionTransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SubscriptionTransactionSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['user'] != request.user:
                return Response({"error": "Faqat o‘z obunangizga to‘lov kiritishingiz mumkin."},
                                status=status.HTTP_403_FORBIDDEN)
            serializer.save()
            return Response({"success": "Obuna to‘lovi yaratildi."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
class ServicePaymentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = ServicePayment.objects.filter(user=request.user).order_by('-date')
        serializer = ServicePaymentSerializer(payments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ServicePaymentSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['user'] != request.user:
                return Response({"error": "Faqat o‘z hisobingizdan to‘lov qiling."},
                                status=status.HTTP_403_FORBIDDEN)

            # Soxta bank API funksiyasi chaqiramiz
            from services_api.bank_api import pay_utility_service

            success, msg = pay_utility_service(
                card=request.user.cards.filter(is_primary=True).first(),
                amount=serializer.validated_data['amount']
            )

            if not success:
                return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({"success": "To‘lov bajarildi"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class QRPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QRTokenSerializer(data=request.data)
        if serializer.is_valid():
            sender_card = serializer.validated_data['sender_card']
            qr_token = serializer.validated_data['qr_token']
            amount = serializer.validated_data['amount']

            if sender_card.user != request.user:
                return Response({"error": "Faqat o‘z kartalaringizdan to‘lov qilishingiz mumkin."},
                                status=status.HTTP_403_FORBIDDEN)

            result = pay_with_qr(sender_card.card_number, qr_token, amount)

            if result["success"]:
                serializer.save()  # Transaction history uchun
                return Response({"success": result["message"]}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": result["message"]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class NFCPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            sender_card = serializer.validated_data['sender_card']
            receiver_card = serializer.validated_data['receiver_card']
            amount = serializer.validated_data['amount']

            # Foydalanuvchi faqat o'z kartasidan to'lov qilishi mumkin
            if sender_card.user != request.user:
                return Response(
                    {"error": "Faqat o‘z kartalaringizdan foydalanishingiz mumkin."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Soxta API orqali o'tkazma
            success, message = transfer_between_cards(
                sender_card.card_number,
                receiver_card.card_number,
                amount
            )

            if success:
                serializer.save(method="NFC")  # 'QR' yoki 'NFC' method deb saqlaymiz
                return Response({"success": "NFC orqali to‘lov bajarildi."}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # transactions/views.py


class NFCTransferView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        sender_card_id = request.data.get('sender_card_id')
        nfc_token = request.data.get('nfc_token')
        amount = request.data.get('amount')

        try:
            sender = Card.objects.get(id=sender_card_id, owner=request.user, is_blocked=False)
        except Card.DoesNotExist:
            return Response({"error": "Sender card topilmadi yoki bloklangan."}, status=400)

        try:
            token_obj = QRToken.objects.get(token=nfc_token)  # NFC token QRTokenda saqlanmoqda
            receiver = token_obj.card
        except QRToken.DoesNotExist:
            return Response({"error": "NFC token noto‘g‘ri yoki muddati tugagan."}, status=400)

        if sender.balance < float(amount):
            return Response({"error": "Yetarli mablag‘ mavjud emas."}, status=400)

        # Simulyatsiya qilingan bank API chaqiruv
        bank_response = self.call_bank_api(sender.card_number, receiver.card_number, amount)
        
        transaction = NFCTransaction.objects.create(
            sender=sender,
            receiver=receiver,
            amount=amount,
            status='success' if bank_response["success"] else 'failed',
            external_ref=bank_response.get("reference", "")
        )

        if bank_response["success"]:
            sender.balance -= float(amount)
            receiver.balance += float(amount)
            sender.save()
            receiver.save()
            return Response(NFCTransactionSerializer(transaction).data, status=200)
        else:
            return Response({"error": "Bank API orqali to‘lov amalga oshmadi."}, status=502)

    def call_bank_api(self, sender_card_number, receiver_card_number, amount):
        """
        Bu joyda siz real bank API'ga HTTP so‘rov yuborasiz.
        Misol uchun, bu joyni UzCard yoki Humo API'ga moslashtirasiz.
        """
        try:
            response = requests.post("https://api.realbank.uz/transfer", json={
                "from_card": sender_card_number,
                "to_card": receiver_card_number,
                "amount": amount,
                "secret_key": "YOUR_BANK_SECRET"  # real autentifikatsiya
            }, timeout=5)

            if response.status_code == 200:
                return {"success": True, "reference": response.json().get("transaction_id")}
            else:
                return {"success": False}

        except requests.exceptions.RequestException:
            return {"success": False}
        


class MobilePaymentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = MobilePayment.objects.filter(user=request.user).order_by('-date')
        serializer = MobilePaymentSerializer(payments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MobilePaymentSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['user'] != request.user:
                return Response({"error": "Faqat o‘z hisobingizdan to‘lov qiling."},
                                status=status.HTTP_403_FORBIDDEN)

            # Soxta bank API dan foydalanamiz
            from services_api.bank_api import pay_mobile_service

            primary_card = request.user.cards.filter(is_primary=True).first()

            success, msg = pay_mobile_service(
                card=primary_card,
                amount=serializer.validated_data['amount']
            )

            if not success:
                return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({"success": "Mobil to‘lov bajarildi"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class CreateTransferTransactionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        sender_card_id = request.data.get('sender_card_id')
        receiver_card_id = request.data.get('receiver_card_id')
        amount = Decimal(request.data.get('amount'))
        title = request.data.get('title', "Pul o‘tkazmasi")

        try:
            sender = Card.objects.get(id=sender_card_id, owner=request.user)
            receiver = Card.objects.get(id=receiver_card_id)
        except Card.DoesNotExist:
            return Response({'error': 'Karta topilmadi'}, status=404)

        if sender.balance < amount:
            return Response({'error': 'Hisobda mablag‘ yetarli emas'}, status=400)

        # Pul yechish va qo‘shish
        sender.balance -= amount
        receiver.balance += amount
        sender.save()
        receiver.save()

        # Tranzaksiyani yaratish
        transaction = TransferTransaction.objects.create(
            sender=sender,
            receiver=receiver,
            amount=amount,
            title=title
        )

        # Foyda logini hisoblash va yozish
        fees = calculate_fees(amount)
        TransferProfitLog.objects.create(
            transaction=transaction,
            click_fee=fees['click_fee'],
            service_fee=fees['service_fee'],
            your_profit=fees['your_profit']
        )

        return Response({
            'message': 'Tranzaksiya muvaffaqiyatli bajarildi',
            'amount': str(amount),
            'your_profit': str(fees['your_profit']),
        }, status=status.HTTP_201_CREATED)
    


class ProfitStatisticsView(APIView):
    permission_classes = [permissions.IsAdminUser]  # faqat adminlar ko‘ra oladi

    def get(self, request):
        total_profit = TransferProfitLog.objects.aggregate(Sum('your_profit'))['your_profit__sum'] or 0
        total_click_fee = TransferProfitLog.objects.aggregate(Sum('click_fee'))['click_fee__sum'] or 0
        total_service_fee = TransferProfitLog.objects.aggregate(Sum('service_fee'))['service_fee__sum'] or 0

        return Response({
            "total_profit": str(total_profit),
            "total_click_fee": str(total_click_fee),
            "total_service_fee_collected": str(total_service_fee),
        })
    
class MobilePaymentView(APIView):
       permission_classes = [permissions.IsAuthenticated]

       def post(self, request):
        from decimal import Decimal
        from .utils import calculate_fees_by_service_type
        from .models import MobilePayment, ServiceProfitLog

        operator = request.data.get('operator')
        phone = request.data.get('phone_number')
        amount = Decimal(request.data.get('amount'))

        mp = MobilePayment.objects.create(
            user=request.user,
            operator=operator,
            phone_number=phone,
            amount=amount
        )

        fees = calculate_fees_by_service_type(amount, 'mobile')

        ServiceProfitLog.objects.create(
            user=request.user,
            payment_type='mobile',
            related_id=mp.id,
            amount=amount,
            service_fee=fees['service_fee'],
            click_fee=fees['click_fee'],
            your_profit=fees['your_profit']
        )

        return Response({"message": "Mobil to‘lov bajarildi", "your_profit": str(fees['your_profit'])})
    

class ServicePaymentView(APIView):
      permission_classes = [permissions.IsAuthenticated]

      def post(self, request):
        from decimal import Decimal
        from .utils import calculate_fees_by_service_type
        from .models import ServicePayment, ServiceProfitLog

        service_type = request.data.get('service_type')  # electricity, gas, water, internet
        service_name = request.data.get('service_name')
        account_number = request.data.get('account_number')
        amount = Decimal(request.data.get('amount'))

        sp = ServicePayment.objects.create(
            user=request.user,
            service_type=service_type,
            service_name=service_name,
            account_number=account_number,
            amount=amount
        )

        fees = calculate_fees_by_service_type(amount, 'service')

        ServiceProfitLog.objects.create(
            user=request.user,
            payment_type='service',
            related_id=sp.id,
            amount=amount,
            service_fee=fees['service_fee'],
            click_fee=fees['click_fee'],
            your_profit=fees['your_profit']
        )

        return Response({"message": "Kommunal to‘lov bajarildi", "your_profit": str(fees['your_profit'])})