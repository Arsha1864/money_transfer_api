
from rest_framework import generics, permissions
from .models import Card
from .serializers import CardSerializer
        # cards/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
 # Kartalar modeli
from accounts.models import VerificationCode  # SMS kod modeli (agar mavjud bo‘lsa)
from accounts.sms_service import send_sms_eskiz  # SMS yuborish funksiyasi

class CardCreateView(generics.CreateAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



import random

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_card_sms(request):
    card_number = request.data.get("card_number")

    if not card_number:
        return Response({"error": "Karta raqami yuborilmadi."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        card = Card.objects.get(number=card_number, owner=request.user)
    except Card.DoesNotExist:
        return Response({"error": "Karta topilmadi yoki sizga tegishli emas."}, status=status.HTTP_404_NOT_FOUND)

    # Random 6 xonali kod generatsiyasi
    code = f"{random.randint(100000, 999999)}"

    # Kodni bazaga yozish (VerificationCode modeliga)
    VerificationCode.objects.update_or_create(
        user=request.user,
        purpose="card_verify",
        defaults={"code": code}
    )

    # SMS yuborish (foydalanuvchi telefon raqamiga)
    send_sms_eskiz(phone=card.owner.phone_number, code=code)

    return Response({"message": "Tasdiqlash kodi yuborildi."}, status=status.HTTP_200_OK)