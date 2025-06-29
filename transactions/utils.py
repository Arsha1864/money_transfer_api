from decimal import Decimal
from .models import CommissionSetting

def calculate_fees(amount: Decimal):
    service_fee_percent = Decimal('0.02')   # siz foydalanuvchidan olasiz
    click_fee_percent = Decimal('0.015')    # Click o‘z ulushini oladi

    service_fee = amount * service_fee_percent
    click_fee = amount * click_fee_percent
    your_profit = service_fee - click_fee

    return {
        'service_fee': service_fee,
        'click_fee': click_fee,
        'your_profit': your_profit
    }



def calculate_fees_by_service_type(amount: Decimal, service_type: str):
    setting = CommissionSetting.objects.filter(service_type=service_type).first()

    if not setting:
        # fallback qiymatlar
        if service_type == "mobile":
            service_fee_percent = Decimal('1.50')
            click_fee_percent = Decimal('1.50')
        else:
            service_fee_percent = Decimal('2.00')
            click_fee_percent = Decimal('1.50')
    else:
        service_fee_percent = setting.service_fee_percent
        click_fee_percent = setting.click_fee_percent

    service_fee = amount * service_fee_percent / 100
    click_fee = amount * click_fee_percent / 100
    your_profit = service_fee - click_fee

    return {
        'service_fee': service_fee,
        'click_fee': click_fee,
        'your_profit': your_profit
    }