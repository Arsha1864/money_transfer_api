# accounts/urls.py
from django.urls import path
from .views import (
    dashboard,
    UserCreateAPIView,
    RegisterView,
    LoginView,
    VerifyCodeView,
    ForgotPasswordView,
    SetPinView,
    ChangePasswordAPIView,
    FeedbackCreateView,
    FeedbackListView,
    NotificationListView,
    MarkNotificationReadView,
    EnterPinView,
)
urlpatterns = [
    path('', UserCreateAPIView.as_view(), name='user-list'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify/', VerifyCodeView.as_view(), name='verify'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('set-pin/', SetPinView.as_view(), name='set-pin'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path('enter-pin/', EnterPinView.as_view(), name='enter-pin'),
    path('custom-admin/', dashboard, name='custom_dashboard'),
    # Feedback endpoints
    path('feedback/', FeedbackCreateView.as_view(), name='create_feedback'),
    path('feedback/list/', FeedbackListView.as_view(), name='list_feedback'),

    # Notification endpoints
    path('notifications/', NotificationListView.as_view(), name='list_notifications'),
    path('notifications/<int:pk>/mark-read/', MarkNotificationReadView.as_view(), name='mark_notification_read'),
    
]