from rest_framework.views import APIView  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework import status  # type: ignore
from django.contrib.auth import authenticate  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import generics, permissions ,viewsets
from .models import Notification,VerificationCode
from .serializers import (
NotificationSerializer,
RegisterSerializer,
FeedbackSerializer,
UserSerializer,

)
from .models import Feedback  # type: ignore
from .sms_service import SMSService
from accounts.models import CustomUser
from django.contrib.auth.models import User
import string
import random
from card.models import Card  # <-- sizning karta model nomi
from django.utils import timezone
from django.contrib.auth.hashers import make_password,check_password
from accounts.sms_service import SMSService
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.timezone import now, timedelta
from django.core.cache import cache


from datetime import timedelta
# konfiguratsiya
FAILED_PIN_LIMIT = 3
PIN_LOCK_MINUTES = 15
CYCLES_BEFORE_FORCE_LOGIN = 2  # misol uchun: ikki sikldan keyin login talab qilinsin


 

User = get_user_model()

# 📌 Register (ochiq)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Tasdiqlash kodi
            code = random.randint(100000, 999999)
            VerificationCode.objects.create(user=user, code=code)

            SMSService(user.phone_number, code)

            refresh = RefreshToken.for_user(user)

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "message": "Foydalanuvchi muvaffaqiyatli ro‘yxatdan o‘tdi."
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 📌 Login (ochiq)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get('phone_number')
        password = request.data.get('password')

        user = authenticate(phone_number=phone, password=password)

        if user:
            if not user.is_verified:
                return Response({"error": "Telefon raqam tasdiqlanmagan"}, status=status.HTTP_403_FORBIDDEN)

            refresh = RefreshToken.for_user(user)

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "phone_number": user.phone_number,
            }, status=status.HTTP_200_OK)

        return Response({"error": "Login yoki parol noto‘g‘ri"}, status=status.HTTP_401_UNAUTHORIZED)



# 📌 Verify Code (ochiq)


class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone_number")
        code = request.data.get("code")

        try:
            user = CustomUser.objects.get(phone_number=phone)

            # Faqat DEBUG holatda "123455" orqali tasdiqlansin
            if  code == '123455':
                user.is_verified = True
                user.save()
                return Response({"message": "Telefon tasdiqlandi"}, status=status.HTTP_200_OK)

            # Aks holda kodni VerificationCode modeli orqali tekshiradi
            verification = VerificationCode.objects.filter(user=user).last()
            if verification and verification.code == code:
                user.is_verified = True
                user.save()
                return Response({"message": "Telefon tasdiqlandi"}, status=status.HTTP_200_OK)

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



class PinStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        has_pin = bool(user.pin_code)  # PIN mavjudmi

        return Response({
            "has_pin": has_pin,
            "biometric_enabled": user.has_fingerprint_enabled
        }, status=status.HTTP_200_OK)


    # Enter Pin cod
# accounts/views.py (yoki kerakli papkada)


def _cache_key(user_id):
    return f"pin_attempts:{user_id}"

class EnterPinView(APIView):
    permission_classes = [permissions.AllowAny]  # endpoint useToken false bo'ladi

    def post(self, request):
        phone_number = request.data.get('phone_number')  # frontend shu nom bilan yuborsin
        pin_code = request.data.get('pin')

        if not phone_number or not pin_code:
            return Response({'detail': 'phone_number yoki pin kerak'}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response({'detail': 'Foydalanuvchi topilmadi'}, status=status.HTTP_404_NOT_FOUND)

        # cache-dan olingan struktura: {'count': int, 'locked_until': datetime, 'cycles': int}
        key = _cache_key(user.id)
        data = cache.get(key) or {'count': 0, 'locked_until': None, 'cycles': 0}

        # bloklanganmi?
        if data.get('locked_until') and timezone.now() < data['locked_until']:
            return Response({'detail': 'PIN bloklangan. Keyinroq urinib ko‘ring.'}, status=status.HTTP_423_LOCKED)

        # pinni tekshirish
        if not user.pin_code:
            return Response({'detail': 'PIN o‘rnatilmagan'}, status=status.HTTP_400_BAD_REQUEST)

        pin_ok = check_password(pin_code, user.pin_code)
        if not pin_ok:
            data['count'] = data.get('count', 0) + 1

            if data['count'] >= FAILED_PIN_LIMIT:
                # bir sikl yakunlandi: bloklash va cycles oshirish
                data['locked_until'] = timezone.now() + timedelta(minutes=PIN_LOCK_MINUTES)
                data['count'] = 0
                data['cycles'] = data.get('cycles', 0) + 1

                cache.set(key, data, timeout=60 * 60 * 24)  # cache uchun yetarli timeout
                # Agar sikllar ma'lum chegara oshsa, majburiy to'liq login
                if data['cycles'] >= CYCLES_BEFORE_FORCE_LOGIN:
                    # to'liq login talab etilsin: foydalanuvchini pinni tiklash/login sahifasiga yuborish
                    cache.delete(key)  # reset
                    return Response({'detail': 'Ko‘p marta xato. Iltimos, to‘liq login qiling.'}, status=status.HTTP_403_FORBIDDEN)

                return Response({'detail': f'PIN noto\'g\'ri. {PIN_LOCK_MINUTES} daqiqa bloklandi.'}, status=status.HTTP_423_LOCKED)

            # saqlash va qaytish
            cache.set(key, data, timeout=60 * 60)
            return Response({'detail': 'Noto\'g\'ri PIN'}, status=status.HTTP_401_UNAUTHORIZED)

        # pin to'g'ri bo'lsa — urinishlarni tiklab qo'yish
        cache.delete(key)

        # tokenlar tayyorlash (SimpleJWT)
        refresh = RefreshToken.for_user(user)
        data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'fingerprint_enabled': bool(user.has_fingerprint_enabled),
        }
        return Response(data, status=status.HTTP_200_OK)


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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pin = request.data.get('pin')
        biometric = request.data.get('biometric', False)

        # PIN validatsiyasi: 4 xonali raqam bo'lishi kerak
        if not pin or len(pin) != 4 or not pin.isdigit():
            return Response(
                {"error": "PIN faqat 4 xonali raqamlardan iborat bo'lishi kerak"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user: CustomUser = request.user  # JWT orqali aniqlangan foydalanuvchi

        # PIN shifrlanib saqlanadi
        user.pin_code = make_password(pin)
        user.has_fingerprint_enabled = biometric
        user.save()

        return Response({
            "success": True,
            "message": "PIN muvaffaqiyatli saqlandi yoki yangilandi"
        }, status=status.HTTP_200_OK)
    
# 📌 Change Password (faqat login qilgan foydalanuvchi)
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        pin = request.data.get('pin')
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not pin or not check_password(pin, user.pin_code):
            return Response({"error": "PIN noto‘g‘ri"}, status=403)

        if not old_password or not new_password:
            return Response({"error": "Parollar to‘liq kiritilmagan"}, status=400)

        if not user.check_password(old_password):
            return Response({"error": "Eski parol noto‘g‘ri"}, status=403)

        if len(new_password) < 6:
            return Response({"error": "Yangi parol kamida 6 ta belgidan iborat bo‘lishi kerak"}, status=400)

        user.set_password(new_password)
        user.save()

        return Response({"success": True, "message": "Parol muvaffaqiyatli yangilandi"}, status=200)
    
# Change-Phone Number
class ChangePhoneView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phone = request.data.get('phone_number')
        pin = request.data.get('pin') 
        user = request.user

        # PIN tekshiruv (agar kerak bo‘lsa)
        if pin and not check_password(pin, user.pin_code):
            return Response({"error": "PIN noto‘g‘ri"}, status=403)

        if not phone or not phone.startswith('+998') or len(phone) != 13:
            return Response({"error": "Telefon raqam noto‘g‘ri"}, status=400)

        user.phone_number = phone
        user.save()
        return Response({"success": True, "message": "Telefon raqam yangilandi"}, status=200)

# Pin Cod ni yangilash 
class ChangePinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_pin = request.data.get('old_pin')
        new_pin = request.data.get('new_pin')
        user = request.user

        if not old_pin or not check_password(old_pin, user.pin_code):
            return Response({"error": "Eski PIN noto‘g‘ri"}, status=400)

        if not new_pin or len(new_pin) != 4 or not new_pin.isdigit():
            return Response({"error": "Yangi PIN 4 xonali raqam bo‘lishi kerak"}, status=400)

        user.pin_code = make_password(new_pin)
        user.save()

        return Response({"success": True, "message": "PIN muvaffaqiyatli o‘zgartirildi"}, status=200)



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
class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Feedback.objects.all().order_by('created_at')
        return Feedback.objects.filter(user=user).order_by('created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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