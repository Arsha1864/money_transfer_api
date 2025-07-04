from django.urls import path
from .views import CardCreateView
from .views import resend_card_sms
from .views import CardListView, VerifyCardSmsView, ResendCardSmsView
urlpatterns = [
    path('cards/add/', CardCreateView.as_view(), name='add-card'),
    path('cards/', CardListView.as_view(), name='card-list'),
    path('verify_card_sms/', VerifyCardSmsView.as_view(), name='verify-card-sms'),
    path('resend_card_sms/', ResendCardSmsView.as_view(), name='resend-card-sms'),
]
