from django.urls import path
from .views import (
    TransactionListView,
    TransferAPIView,
    SubscriptionTransactionListCreateAPIView,
    QRPaymentView, NFCPaymentView, ServicePaymentListCreateAPIView,MobilePaymentListCreateAPIView,
    CreateTransferTransactionView, ProfitStatisticsView, MobilePaymentView, ServicePaymentView
)

urlpatterns = [
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('transfer/', TransferAPIView.as_view(), name='transfer'),
    path('subscriptions/', SubscriptionTransactionListCreateAPIView.as_view(), name='subscription-transactions'),
    path('pay/qr/', QRPaymentView.as_view(), name='qr-pay'),
    path('pay/nfc/', NFCPaymentView.as_view(), name='nfc-pay'),
    path('service-payments/', ServicePaymentListCreateAPIView.as_view(), name='service-payments'),
    path('mobile-payments/', MobilePaymentListCreateAPIView.as_view(), name='mobile-payments'),
    path('api/transfer/', CreateTransferTransactionView.as_view(), name='transfer'),
    path('api/profit/statistics/', ProfitStatisticsView.as_view(), name='profit-statistics'),
    path('api/payment/mobile/', MobilePaymentView.as_view(), name='mobile-payment'),
    path('api/payment/service/', ServicePaymentView.as_view(), name='service-payment'),
]