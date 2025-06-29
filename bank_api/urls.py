from django.urls import path
from .views import AddCardView, TransferView, BalanceView, TransactionHistoryView, CheckPinView, PayUtilityView

urlpatterns = [
    path("cards/add/", AddCardView.as_view()),
    path("cards/transfer/", TransferView.as_view()),
    path("cards/<str:card_number>/balance/", BalanceView.as_view()),
    path("cards/<str:card_number>/history/", TransactionHistoryView.as_view()),
    path("cards/<str:card_number>/validate_pin/", CheckPinView.as_view()),
    path("payment/utilities/", PayUtilityView.as_view()),
]