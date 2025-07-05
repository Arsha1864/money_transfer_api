from django.urls import path
from .views import CardCreateView,CardListView, VerifyCardSmsView, ResendCardSmsView

urlpatterns = [
    path('card/add/', CardCreateView.as_view(), name='add-card'),
    path('card/', CardListView.as_view(), name='card-list'),
    path('verify_card_sms/', VerifyCardSmsView.as_view(), name='verify-card-sms'),
    path('resend_card_sms/', ResendCardSmsView.as_view(), name='resend-card-sms'),
]
