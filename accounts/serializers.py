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
    user = serializers.StringRelatedField(read_only=True)
    from_user = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = ['id', 'user', 'message', 'created_at', 'from_user']

    def get_from_user(self, obj):
        return obj.user == self.context['request'].user

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


class VerifySmsSerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField()



class SetPinSerializer(serializers.Serializer):
    pin = serializers.CharField(min_length=4, max_length=4)
    

    def validate_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("PIN faqat raqamlardan iborat bo'lishi kerak.")
        return value

    def update_pin(self, user):
        user.pin = self.validated_data['pin']
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

        user = getattr(self, "user", None)
        if not user:
            raise serializers.ValidationError("Login ma'lumotlari noto‘g‘ri")

        if not user.is_verified:
            raise serializers.ValidationError("Telefon raqam tasdiqlanmagan")

        data.update({
            "phone_number": user.phone_number,
            "username": user.username,
        })
        return data
