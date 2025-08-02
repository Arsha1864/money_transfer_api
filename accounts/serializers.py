from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomUser, Feedback, Notification
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.validators import RegexValidator
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']





class FeedbackSerializer(serializers.ModelSerializer):
    from_user = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = ['id', 'message', 'image', 'created_at', 'from_user']

    def get_from_user(self, obj):
        request = self.context.get('request')
        return obj.user == request.user


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    phone = serializers.CharField(
        validators=[RegexValidator(regex=r'^\+998\d{9}$', message="Telefon raqam formati noto‘g‘ri.")]
    )

    class Meta:
        model = User
        fields = ['name', 'phone', 'password', 'confirm_password', 'is_agreed']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Parollar mos emas.")
        if not data.get('is_agreed', False):
            raise serializers.ValidationError("Foydalanuvchi shartlarga rozilik bildirmagan.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user



class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(phone=data['phone'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Telefon raqam yoki parol noto‘g‘ri")


class VerifySmsSerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField()



class SetPinSerializer(serializers.Serializer):
    pin = serializers.CharField(min_length=4, max_length=4)
    biometric = serializers.BooleanField(default=False)

    def validate_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("PIN faqat raqamlardan iborat bo'lishi kerak.")
        return value

    def update_pin(self, user):
        user.pin = self.validated_data['pin']
        user.biometric_enabled = self.validated_data['biometric']
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Yangi parollar mos emas")
        return data
    



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_verified:
            raise serializers.ValidationError("Telefon raqam tasdiqlanmagan.")
        
        data.update({
            "phone_number": self.user.phone_number,
        })
        return data
    


class EnterPinSerializer(serializers.Serializer):
    pin = serializers.CharField(required=False)
    biometric = serializers.BooleanField(required=False)

    def validate(self, attrs):
        request = self.context['request']
        user = request.user if request.user.is_authenticated else None

        pin = attrs.get('pin')
        biometric = attrs.get('biometric')

        if not pin and not biometric:
            raise serializers.ValidationError("PIN yoki biometric kerak")

        # Biometric login
        if biometric:
            if not user or not user.has_fingerprint_enabled:
                raise serializers.ValidationError("Biometric login yoqilmagan.")
            return self._generate_tokens(user)

        # PIN bilan login
        if pin:
            try:
                user = CustomUser.objects.get(pin_code=pin)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("PIN noto‘g‘ri.")
            return self._generate_tokens(user)

        raise serializers.ValidationError("Xatolik yuz berdi.")

    def _generate_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'user': user,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }