
from rest_framework import generics, permissions
from .models import Card
from .serializers import CardSerializer
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Card, VerificationCode
  
from accounts.sms_service import send_sms_eskiz  
import random
  # sizning Card model nomingiz
 
class CardCreateView(generics.CreateAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CardListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        cards = Card.objects.filter(user=user)
        serializer = CardSerializer(cards, many=True)
        return Response(serializer.data)



  # Agar SMS yuboruvchi funksiya shu yerda bo‘lsa

class ResendCardSmsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        card_number = request.data.get("card_number")

        if not card_number:
            return Response({"error": "Karta raqami yuborilmadi."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            card = Card.objects.get(card_number=card_number, user=request.user)
        except Card.DoesNotExist:
            return Response({"error": "Karta topilmadi yoki sizga tegishli emas."}, status=status.HTTP_404_NOT_FOUND)

        # 6 xonali random kod
        code = f"{random.randint(100000, 999999)}"

        # VerificationCode modeliga yozish
        VerificationCode.objects.update_or_create(
            user=request.user,
            purpose="card_verify",
            defaults={"code": code}
        )

        # SMS yuborish
        send_sms_eskiz(phone=card.user.phone_number, code=code)

        return Response({"success": True, "message": "Tasdiqlash kodi yuborildi."}, status=status.HTTP_200_OK)
    

class VerifyCardSmsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        card_number = request.data.get("card_number")
        code = request.data.get("code")

        if not card_number or not code:
            return Response(
                {"error": "Karta raqami yoki kod yuborilmadi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            card = Card.objects.get(card_number=card_number, user=request.user)
        except Card.DoesNotExist:
            return Response(
                {"error": "Karta topilmadi yoki sizga tegishli emas."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            verification = VerificationCode.objects.get(user=request.user, purpose="card_verify")
        except VerificationCode.DoesNotExist:
            return Response(
                {"error": "Tasdiqlash kodi topilmadi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if verification.code != code:
            return Response(
                {"error": "Tasdiqlash kodi noto‘g‘ri."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Agar kod to‘g‘ri bo‘lsa, karta faollashtiriladi
        card.is_active = True
        card.save()

        # Kodni o‘chirib tashlash yoki buzib qo‘yish (xavfsizlik uchun)
        verification.code = "000000"
        verification.save()

        return Response({"message": "Karta muvaffaqiyatli tasdiqlandi."}, status=status.HTTP_200_OK)