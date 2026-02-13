from django.db import models
import uuid

class Payment(models.Model):
    transaction_id = models.CharField(max_length=100, default=uuid.uuid4, unique=True, editable=False)

    # Standard Plaintext Fields - No more encryption overhead or signature errors
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=255)
    address_line_one = models.CharField(max_length=500)
    address_line_two = models.CharField(max_length=500, blank=True)
    city = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)

    # Tracking and Filtering Fields
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=50, blank=True)
    donation_option = models.CharField(max_length=100, blank=True)
    donate_to = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"


class FailedPayment(models.Model):
    transaction_id = models.CharField(max_length=100)

    # Standard Plaintext Fields
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=255)
    address_line_one = models.CharField(max_length=500, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Additional Data
    address_line_two = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=50, blank=True)
    donation_option = models.CharField(max_length=100, blank=True)
    donate_to = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Failed: {self.transaction_id}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"
