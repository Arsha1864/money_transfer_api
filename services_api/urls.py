from django.urls import path
from .views import VerifyCardAPIView

urlpatterns = [
    path('verify-card/', VerifyCardAPIView.as_view()),
]