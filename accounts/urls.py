from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,     # token yangilash
    TokenVerifyView       # tokenni tekshirish
)


from accounts.token import CustomTokenObtainPairView
from .views import (
    dashboard,
    UserCreateAPIView,
    RegisterView,
    LoginView,  # bu kerak bo‘lsa, boshqa yo‘l nomi bilan
    VerifyCodeView,
    ForgotPasswordView,
    SetOrUpdatePinView,
    ChangePasswordView,
    NotificationListView,
    MarkNotificationReadView,
    EnterPinView,
    VerifyCardSmsView, 
    ResendCardSmsView,
    PinStatusView,
    ChangePhoneView,
    ChangePinView,
   FeedbackListCreateView
)




urlpatterns = [
    path('', UserCreateAPIView.as_view(), name='user-list'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login-old/', LoginView.as_view(), name='login-old'),  # Agar eski login kerak bo‘lsa

    path('verify/', VerifyCodeView.as_view(), name='verify'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('change-phone/', ChangePhoneView.as_view(), name='change-phone'),
    path('change-pin/', ChangePinView.as_view(), name='change-pin'),

    path('set-pin/', SetOrUpdatePinView.as_view()),
   
    path('pin-status/', PinStatusView.as_view(), name='pin-status'),
    path('custom-admin/', dashboard, name='custom_dashboard'),

    # Feedback

    path('feedback/', FeedbackListCreateView.as_view(), name='feedback'),

    # Notification
    path('notifications/', NotificationListView.as_view(), name='list_notifications'),
    path('notifications/<int:pk>/mark-read/', MarkNotificationReadView.as_view(), name='mark_notification_read'),

    path('verify_card_sms/', VerifyCardSmsView.as_view()),
    path('resend_card_sms/', ResendCardSmsView.as_view()),

    # ✅ JWT Token endpoints (custom login)
    path('login/', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('enter-pin/', EnterPinView.as_view(), name='enter-pin'),
]




   
