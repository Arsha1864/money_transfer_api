from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Feedback, Notification
from django.contrib.auth import authenticate

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
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'message', 'created_at']
        read_only_fields = ['user', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(
            phone=validated_data['phone'],
            password=validated_data['password']
        )


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
    pin_code = serializers.CharField(max_length=6)
    confirm_pin = serializers.CharField(max_length=6)

    def validate(self, data):
        if data['pin_code'] != data['confirm_pin']:
            raise serializers.ValidationError("PIN kodlar mos emas")
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Yangi parollar mos emas")
        return data
