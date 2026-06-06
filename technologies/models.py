from django.conf import settings
from django.db import models


class TechnologyBooking(models.Model):
    PAYMENT_COD = 'cod'
    PAYMENT_ONLINE = 'online'
    PAYMENT_CHOICES = [
        (PAYMENT_COD, 'Cash on Delivery'),
        (PAYMENT_ONLINE, 'Online Payment'),
    ]

    PAYMENT_STATUS_UNPAID = 'unpaid'
    PAYMENT_STATUS_PAID = 'paid'
    PAYMENT_STATUS_FAILED = 'failed'
    PAYMENT_STATUS_REFUNDED = 'refunded'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_UNPAID, 'Unpaid'),
        (PAYMENT_STATUS_PAID, 'Paid'),
        (PAYMENT_STATUS_FAILED, 'Failed'),
        (PAYMENT_STATUS_REFUNDED, 'Refunded'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='technology_bookings')
    service_name = models.CharField(max_length=120)
    customer_name = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=20)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=80)
    pincode = models.CharField(max_length=10)
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    amount_inr = models.DecimalField(max_digits=8, decimal_places=2, default=499.00)
    notes = models.TextField(blank=True)
    payment_reference = models.CharField(max_length=120, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_UNPAID)
    razorpay_order_id = models.CharField(max_length=120, blank=True)
    razorpay_payment_id = models.CharField(max_length=120, blank=True)
    razorpay_signature = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.service_name} technology booking for {self.customer_name}"
