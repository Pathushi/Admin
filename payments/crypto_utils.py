import os
import base64
import logging
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from django.conf import settings

# Initialize logger to catch errors in gunicorn_error.log
logger = logging.getLogger(__name__)

def encrypt_payment(transaction_id: str, amount: str):
    """
    Encrypts the transaction ID and amount using RSA PKCS#1 v1.5.
    Required for WebXPay secure checkout.
    """
    try:
        # 1. Create the plaintext string
        # WebXPay typically expects the format: transaction_id|amount
        plaintext = f"{transaction_id}|{amount}"

        # 2. Locate the public key file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        key_file = os.path.join(current_dir, "crypto", "public_key.pem")

        if not os.path.exists(key_file):
            logger.error(f"Encryption Error: Public key not found at {key_file}")
            raise FileNotFoundError(f"Public key not found at {key_file}")

        # 3. Import the RSA Key
        with open(key_file, "rb") as f:
            public_key = RSA.import_key(f.read())

        # 4. Perform RSA Encryption
        cipher = PKCS1_v1_5.new(public_key)
        encrypted_bytes = cipher.encrypt(plaintext.encode("utf-8"))
        
        # 5. Convert to Base64 string
        encrypted_b64 = base64.b64encode(encrypted_bytes).decode("ascii")

        # 6. CRITICAL: Return the value to views.py
        return encrypted_b64

    except Exception as e:
        logger.exception("Encryption process failed")
        raise e
