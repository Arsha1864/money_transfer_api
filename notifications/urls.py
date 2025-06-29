# 3. urls.py
from django.urls import path
from .views import NotificationListView, MarkAsReadView, DeleteNotificationView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/read/', MarkAsReadView.as_view(), name='notification-mark-read'),
    path('<int:pk>/delete/', DeleteNotificationView.as_view(), name='notification-delete'),
]