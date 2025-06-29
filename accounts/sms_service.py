# accounts/sms_service.py
import requests
import random
# Global sozlamalar (testda USE_ESKIZ = True deb turing)
USE_ESKIZ = True
USE_PLAYMOBILE = False
USE_INFOBIP = False

def generate_verification_code(length=6):
    return ''.join(random.choices("0123456789", k=length))

# ---- 1. Eskiz.uz ----
def get_eskiz_token():
    login_url = "https://notify.eskiz.uz/api/auth/login"
    login_data = {
        "email": "YOUR_EMAIL",
        "password": "YOUR_PASSWORD"
    }

    response = requests.post(login_url, data=login_data)
    if response.status_code == 200:
        return response.json()["data"]["token"]
    else:
        raise Exception("Eskiz token olishda xatolik")


def send_sms_eskiz(phone, message):
    token = get_eskiz_token()
    url = "https://notify.eskiz.uz/api/message/sms/send"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "mobile_phone": phone,
        "message": message,
        "from": "4546",
        "callback_url": ""
    }

    response = requests.post(url, headers=headers, data=data)
    return response.status_code == 200


# ---- 2. PlayMobile ----
def send_sms_playmobile(phone, message):
    url = "https://cp.playmobile.uz/api/sendSMS"
    payload = {
        "messages": [
            {"recipient": phone, "text": message}
        ],
        "from": "4546",
        "authentication": {
            "username": "YOUR_USERNAME",
            "password": "YOUR_PASSWORD"
        }
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 200


# ---- 3. Infobip ----
def send_sms_infobip(phone, message):
    url = "https://YOUR_BASE_URL.sms.infobip.com/sms/2/text/advanced"
    headers = {
        "Authorization": "App YOUR_API_KEY",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {
                "from": "Info",
                "destinations": [{"to": phone}],
                "text": message
            }
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code == 200


# --- Umumiy foydalanuvchi funksiyasi ---
def send_sms(phone, message):
    if USE_ESKIZ:
        return send_sms_eskiz(phone, message)
    elif USE_PLAYMOBILE:
        return send_sms_playmobile(phone, message)
    elif USE_INFOBIP:
        return send_sms_infobip(phone, message)
    else:
        raise Exception("Hech qanday SMS provayder tanlanmagan!")
    
    # accounts/sms_service.py
 # bu siz tanlagan real provider bo'lishi kerak


def send_verification_sms(phone, code):
    message = f"Sizning tasdiqlash kodingiz: {code}"
    success = send_sms(phone, message)
    if not success:
        raise Exception("SMS yuborishda xatolik yuz berdi")

def send_new_password_sms(phone, password):
    message = f"Yangi parolingiz: {password}"
    success = send_sms(phone, message)
    if not success:
        raise Exception("Parol yuborishda xatolik yuz berdi")