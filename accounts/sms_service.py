import requests
import random


class SMSService:
    USE_ESKIZ = True
    USE_PLAYMOBILE = False
    USE_INFOBIP = False

    @staticmethod
    def generate_verification_code(length=6):
        return ''.join(random.choices("0123456789", k=length))

    # ---- 1. Eskiz.uz ----
    @staticmethod
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

    @classmethod
    def send_sms_eskiz(cls, phone, message):
        token = cls.get_eskiz_token()
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
    @staticmethod
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
    @staticmethod
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
    @classmethod
    def send_sms(cls, phone, message):
        if cls.USE_ESKIZ:
            return cls.send_sms_eskiz(phone, message)
        elif cls.USE_PLAYMOBILE:
            return cls.send_sms_playmobile(phone, message)
        elif cls.USE_INFOBIP:
            return cls.send_sms_infobip(phone, message)
        else:
            raise Exception("Hech qanday SMS provayder tanlanmagan!")

    @classmethod
    def send_verification_sms(cls, phone, code):
        message = f"Sizning tasdiqlash kodingiz: {code}"
        success = cls.send_sms(phone, message)
        if not success:
            raise Exception("SMS yuborishda xatolik yuz berdi")

    @classmethod
    def send_new_password_sms(cls, phone, password):
        message = f"Yangi parolingiz: {password}"
        success = cls.send_sms(phone, message)
        if not success:
            raise Exception("Parol yuborishda xatolik yuz berdi")