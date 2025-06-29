import requests

def get_card_balance(card_number, expiry_date, pin_code):
    try:
        response = requests.post('https://testbank.uz/api/get-balance/', json={
            "card_number": card_number,
            "expiry_date": expiry_date,
            "pin": pin_code
        })
        response.raise_for_status()
        return response.json().get("balance")
    except requests.RequestException:
        return None
    # services_api/bank_api.py

# Soxta test kartalar bazasi
test_cards = {
    "8600123456789012": {
        "balance": 150000.00,
        "is_blocked": False,
        "holder_name": "Ali Karimov",
        "expiry": "12/26",
    },
    "9860123456789012": {
        "balance": 85000.00,
        "is_blocked": False,
        "holder_name": "Dilnoza Azizova",
        "expiry": "11/25",
    },
    "8600999988887777": {
        "balance": 5000.00,
        "is_blocked": True,
        "holder_name": "Blocked User",
        "expiry": "01/24",
    },
}

def transfer_between_cards(sender_card, receiver_card_number, amount):
    # Soxta logika: faqat balans yetarliligini tekshiradi
    if sender_card.balance < amount:
        return {'success': False, 'message': 'Balans yetarli emas.'}
    
    # Aks holda muvaffaqiyatli o‘tkazma
    return {'success': True, 'message': 'Pul muvaffaqiyatli o‘tkazildi.'}


def is_card_valid(card_number):
    """Karta mavjudmi"""
    return card_number in test_cards


def is_card_blocked(card_number):
    """Karta bloklanganmi"""
    return test_cards.get(card_number, {}).get("is_blocked", True)


def get_card_balance(card_number):
    """Karta balansi"""
    return test_cards.get(card_number, {}).get("balance", 0.0)


def get_holder_name(card_number):
    """Karta egasi"""
    return test_cards.get(card_number, {}).get("holder_name", "Noma'lum")


def transfer_funds(sender_card, receiver_card, amount):
    """Soxta o‘tkazma funksiyasi"""
    if not is_card_valid(sender_card):
        return {"success": False, "message": "Jo‘natuvchi karta topilmadi."}

    if not is_card_valid(receiver_card):
        return {"success": False, "message": "Qabul qiluvchi karta topilmadi."}

    if is_card_blocked(sender_card):
        return {"success": False, "message": "Jo‘natuvchi karta bloklangan."}

    sender_balance = test_cards[sender_card]["balance"]

    if sender_balance < amount:
        return {"success": False, "message": "Balansda mablag‘ yetarli emas."}

    # Mablag‘ o‘tkazamiz
    test_cards[sender_card]["balance"] -= amount
    test_cards[receiver_card]["balance"] += amount

    return {"success": True, "message": f"{amount} so‘m o‘tkazildi."}


def pay_service(card_number, amount):
    """Kommunal yoki xizmat to‘lovi uchun"""
    if not is_card_valid(card_number):
        return {"success": False, "message": "Karta topilmadi."}

    if is_card_blocked(card_number):
        return {"success": False, "message": "Karta bloklangan."}

    if get_card_balance(card_number) < amount:
        return {"success": False, "message": "Balansda mablag‘ yetarli emas."}

    # Balansdan yechamiz
    test_cards[card_number]["balance"] -= amount

    return {"success": True, "message": f"{amount} so‘m xizmat uchun to‘landi."}


   # Soxta 
def pay_with_qr(sender_card_number, qr_token, amount):
    # Bu joyda token asosida qaysi karta qabul qiluvchiligini aniqlaymiz (mock)
    receiver_card_number = "8600123412341234"  # Test karta raqami

    if sender_card_number == receiver_card_number:
        return {"success": False, "message": "O‘zingizga to‘lov qilolmaysiz."}

    # Mablag' yetarli bo‘lishi va boshqa testlar
    if amount > 1000000:  # Test uchun cheklov
        return {"success": False, "message": "Mablag‘ yetarli emas."}

    return {"success": True, "message": "QR to‘lov muvaffaqiyatli amalga oshirildi."}


def pay_utility_service(card, amount):
    """
    Soxta bank API: Kommunal xizmat to‘lovi uchun balansdan pul yechish.
    """
    if not card:
        return False, "Asosiy karta topilmadi."

    if card.balance < amount:
        return False, "Karta balansida yetarli mablag‘ yo‘q."

    card.balance -= amount
    card.save()
    return True, "To‘lov muvaffaqiyatli amalga oshirildi."


def pay_mobile_service(card, amount):
    if not card:
        return False, "Asosiy karta topilmadi."

    if not card.is_active:
        return False, "Karta bloklangan."

    if card.balance < amount:
        return False, "Yetarli balans mavjud emas."

    card.balance -= amount
    card.save()
    return True, "Mobil to‘lov amalga oshirildi."