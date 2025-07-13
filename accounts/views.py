from rest_framework.views import APIView  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework import status  # type: ignore
from django.contrib.auth import authenticate  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import generics, permissions
from .serializers import UserSerializer
from .serializers import FeedbackSerializer
from .models import Notification
from .serializers import NotificationSerializer
from .models import Feedback  # type: ignore
from .sms_service import SMSService
from accounts.models import CustomUser
from django.contrib.auth.models import User
import string
import random
from card.models import Card  # <-- sizning karta model nomi
from django.utils import timezone
from django.contrib.auth.hashers import make_password
User = get_user_model()


# 📌 Register (ochiq)
# accounts/views.py
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        phone_number = request.data.get("phone_number")

        if not username or not password or not phone_number:
            return Response({"error": "Barcha maydonlar to‘ldirilishi kerak"}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(phone_number=phone_number).exists():
            return Response({"error": "Telefon raqam ro‘yxatdan o‘tgan"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, password=password,phone_number=phone_number)
         #user.phone_number = phone_number
        code = SMSService()
        user.verification_code = code
        user.is_verified = False
        user.save()

        SMSService(phone_number, code)
        return Response({"message": "Ro‘yxatdan o‘tildi. SMS kod yuborildi."}, status=status.HTTP_201_CREATED,)
        #except Exception as e : 
        #return Response ({'error': f'Ichki xatolik : {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR,)
            
    
        

# 📌 Login (ochiq)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_verified:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({"token": token.key, 'phone_number':user.phone_number}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Telefon raqam tasdiqlanmagan"}, status=status.HTTP_403_FORBIDDEN)
        return Response({"error": "Noto‘g‘ri login yoki parol"}, status=status.HTTP_401_UNAUTHORIZED)



# 📌 Verify Code (ochiq)

class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone_number")
        code = request.data.get("code")

        try:
            user= CustomUser.objects.get(phone_number=phone)
            if user.verification_code == code:
                user.is_verified = True
                user.verification_code = "123456"
                user.save()
                return Response({"message": "Telefon tasdiqlandi"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Kod noto‘g‘ri"}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"error": "Foydalanuvchi topilmadi"}, status=status.HTTP_404_NOT_FOUND)

# views.py
class VerifyCardSmsView(APIView):
    def post(self, request):
        card_number = request.data.get("card_number")
        code = request.data.get("code")

        if not card_number or not code:
            return Response(
                {"error": "Karta raqami va kod talab qilinadi."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            card = Card.objects.get(number=card_number)

            if card.sms_code != code:
                return Response(
                    {"error": "Kod noto‘g‘ri."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            card.is_verified = True
            card.sms_code = "123456"  # Keyinchalik tasodifiy kod generatsiya qiling
            card.verified_at = timezone.now()
            card.save()

            return Response({"message": "Karta tasdiqlandi."}, status=status.HTTP_200_OK)

        except Card.DoesNotExist:
            return Response(
                {"error": "Karta topilmadi."},
                status=status.HTTP_404_NOT_FOUND,
            )


  # <-- o'zingizdagi sms yuboruvchi funksiya

class ResendCardSmsView(APIView):
    def post(self, request):
        card_number = request.data.get("card_number")

        if not card_number:
            return Response(
                {"error": "Karta raqami talab qilinadi."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            card = Card.objects.get(number=card_number)

            new_code = str(random.randint(100000, 999999))
            card.sms_code = new_code
            card.save()

            # SMS yuborish funksiyasi — sozlaganingizga qarab alohida yoziladi
            SMSService(card.owner.phone_number, f"Tasdiqlash kodi: {new_code}")

            return Response({"success": True, "message": "Kod qayta yuborildi."}, status=200)

        except Card.DoesNotExist:
            return Response(
                {"error": "Karta topilmadi."},
                status=status.HTTP_404_NOT_FOUND,
            )

    # Enter Pin cod
class EnterPinView(APIView):
    permission_classes = [IsAuthenticated]  # Token talab qilinadi

    def post(self, request):
        entered_pin = request.data.get('pin_code')

        if not entered_pin:
            return Response({'error': 'PIN kod kiritilmadi'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if user.pin_code == entered_pin:
            return Response({'message': 'PIN kod to‘g‘ri'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Noto‘g‘ri PIN kod'}, status=status.HTTP_401_UNAUTHORIZED)

# 📌 Forgot Password (ochiq)
def generate_random_password(length=8):
          return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone_number")

        try:
            profile = CustomUser.objects.get(phone_number=phone)
            user = profile.user
            new_password = generate_random_password()
            user.set_password(new_password)
            user.save()

            SMSService(phone, new_password)
            return Response({"message": "Yangi parol yuborildi"}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "Telefon raqam topilmadi"}, status=status.HTTP_404_NOT_FOUND)

# 📌 Set PIN (faqat login bo‘lgan foydalanuvchi)
class SetOrUpdatePinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pin = request.data.get('pin')

        if not pin or len(pin) != 4 or not pin.isdigit():
            return Response({"error": "PIN 4 xonali raqam bo'lishi kerak"}, status=400)

        profile = request.user.profile

        # PIN'ni xeshlab saqlaymiz (yangi bo‘lsa ham, eski bo‘lsa ham)
        profile.pin_hash = make_password(pin)
        profile.save()

        return Response({
            "message": "PIN muvaffaqiyatli saqlandi yoki yangilandi"
        }, status=status.HTTP_200_OK)
    
# 📌 Change Password (faqat login qilgan foydalanuvchi)
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response({"detail": "Ikkala parol ham kerak."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return Response({"detail": "Eski parol noto‘g‘ri."}, status=status.HTTP_400_BAD_REQUEST)
        if len(new_password) < 6:
            return Response({"detail": "Yangi parol juda qisqa (kamida 6 belgi)."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Parol muvaffaqiyatli o‘zgartirildi."}, status=status.HTTP_200_OK)

# 📌 Generic User yaratish (ochiq)

@permission_classes([AllowAny])
class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@login_required
def dashboard(request):
    return render(request, 'custom_admin/dashboard.html')

def home_page(request):
    return render(request, 'home.html')

# Fikrlar ro‘yxati – faqat adminlar uchun
class FeedbackCreateView(generics.CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]  # faqat login bo'lganlar

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FeedbackListView(generics.ListAPIView):
    queryset = Feedback.objects.all().order_by('-created_at')
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAdminUser]  # Faqat admin ko‘ra oladi

# 🔔 Foydalanuvchining barcha xabarnomalarini ko‘rsatish
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


# ✅ Bitta xabarnomani "o‘qilgan" deb belgilash
class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({'detail': 'Xabarnoma o‘qilgan deb belgilandi'}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({'error': 'Xabarnoma topilmadi'}, status=status.HTTP_404_NOT_FOUND)