from abc import ABC, abstractmethod
from django.conf import settings
from payments.crypto_utils import encrypt_payment

class PaymentGateway(ABC):
    @abstractmethod
    def get_payment_params(self, payment, formatted_amount):
        pass

class WebXPayProvider(PaymentGateway):
    def get_payment_params(self, payment, formatted_amount):
        # All WebXPay-specific knowledge is isolated here
        encrypted_payment = encrypt_payment(str(payment.transaction_id), formatted_amount)
        
        return {
            "payment_url": settings.WEBXPAY_URL,
            "params": {
                "first_name": payment.first_name,
                "last_name": payment.last_name,
                "email": payment.email,
                "contact_number": payment.phone,
                "amount": formatted_amount,
                "currency": "LKR",
                "process_currency": "LKR",
                "secret_key": settings.WEBXPAY_SECRET,
                "payment": encrypted_payment,
                "return_url": settings.WEBXPAY_RETURN_URL,
                "callback_id": str(payment.transaction_id),
                "version": "5.2",
                "enc_method": "JCs3J+6oSz4V0LgE0zi/Bg==",
                "cms": "Django"
            }
        }
