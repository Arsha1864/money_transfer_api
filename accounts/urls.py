# accounts/urls.py
from django.urls import path
from .views import (
    dashboard,
    UserCreateAPIView,
    RegisterView,
    LoginView,
    VerifyCodeView,
    ForgotPasswordView,
    SetOrUpdatePinView,
    ChangePasswordView,
    FeedbackCreateView,
    FeedbackListView,
    NotificationListView,
    MarkNotificationReadView,
    EnterPinView,
    VerifyCardSmsView, 
    ResendCardSmsView,
    PinStatusView,
    ChangePhoneView,
    ChangePinView,
)
urlpatterns = [
    path('', UserCreateAPIView.as_view(), name='user-list'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify/', VerifyCodeView.as_view(), name='verify'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('change-phone/', ChangePhoneView.as_view(), name='change-phone'),
    path('change-pin/', ChangePinView.as_view(),name='change-pin'),

    path('set-pin/', SetOrUpdatePinView.as_view()),
    path('enter-pin/', EnterPinView.as_view(), name='enter-pin'),
    path('pin-status/', PinStatusView.as_view(), name='pin-status'),
    path('custom-admin/', dashboard, name='custom_dashboard'),
    # Feedback endpoints
    path('feedback/', FeedbackCreateView.as_view(), name='create_feedback'),
    path('feedback/list/', FeedbackListView.as_view(), name='list_feedback'),

    # Notification endpoints
    path('notifications/', NotificationListView.as_view(), name='list_notifications'),
    path('notifications/<int:pk>/mark-read/', MarkNotificationReadView.as_view(), name='mark_notification_read'),
    
    path('verify_card_sms/', VerifyCardSmsView.as_view()),
    path('resend_card_sms/', ResendCardSmsView.as_view()),
    
]
