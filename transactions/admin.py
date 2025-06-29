from django.contrib import admin
from .models import (
    Card,
    QRToken,
    Transaction,
    TransferTransaction,
    TransferPage,
    SubscriptionTransaction,
    NFCTransaction,CommissionSetting,
    ServicePayment,TransferProfitLog
)

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'owner', 'balance', 'card_type', 'is_blocked')
    search_fields = ('card_number', 'owner__phone_number')
    list_filter = ('is_blocked', 'card_type')


@admin.register(QRToken)
class QRTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'card', 'created_at')
    search_fields = ('token',)

   # NFCTransaction modelini import qilish

@admin.register(NFCTransaction)
class NFCTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'amount', 'timestamp', 'status')
    list_filter = ('status', 'timestamp')
    search_fields = ('sendercard_number', 'receivercard_number')
    ordering = ('-timestamp',)




@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('sender_card', 'receiver_card', 'amount', 'method', 'timestamp')
    list_filter = ('method', 'timestamp')
    search_fields = ('sender_cardcard_number', 'receiver_cardcard_number')


@admin.register(TransferTransaction)
class TransferTransactionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'amount', 'date')
    search_fields = ('sendercard_number', 'receivercard_number')


@admin.register(TransferPage)
class TransferPageAdmin(admin.ModelAdmin):
    list_display = ('id', 'commission_percent',)
    fields = ('commission',)

    def commission_percent(self, obj):
        return f"{obj.commission}%"
    commission_percent.short_description = "Komissiya foizda"


@admin.register(SubscriptionTransaction)
class SubscriptionTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'amount', 'date')
    search_fields = ('user__phone_number', 'title')



@admin.register(ServicePayment)
class ServicePaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'service_type', 'amount', 'date')
    list_filter = ('service_type', 'date')
    search_fields = ('user__username', 'service_type')

@admin.register(TransferProfitLog)
class ProfitLogAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'your_profit', 'click_fee', 'service_fee', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('transaction__id',)


@admin.register(CommissionSetting)
class CommissionSettingAdmin(admin.ModelAdmin):
    list_display = ('service_type', 'service_fee_percent', 'click_fee_percent', 'updated_at')