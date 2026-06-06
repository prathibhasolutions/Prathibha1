from django.conf import settings
from django.db import models


class SolutionBooking(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PROPOSAL_SENT = 'proposal_sent'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROPOSAL_SENT, 'Proposal Sent'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    BUDGET_BASIC = 'basic'
    BUDGET_STANDARD = 'standard'
    BUDGET_PREMIUM = 'premium'
    BUDGET_ENTERPRISE = 'enterprise'
    BUDGET_CHOICES = [
        (BUDGET_BASIC, 'Basic (under 15,000 INR)'),
        (BUDGET_STANDARD, 'Standard (15,000 - 50,000 INR)'),
        (BUDGET_PREMIUM, 'Premium (50,000 - 1,50,000 INR)'),
        (BUDGET_ENTERPRISE, 'Enterprise (above 1,50,000 INR)'),
    ]

    PLATFORM_WEBSITE = 'website'
    PLATFORM_WEB_APP = 'web_app'
    PLATFORM_MOBILE_READY = 'mobile_ready'
    PLATFORM_CHOICES = [
        (PLATFORM_WEBSITE, 'Website'),
        (PLATFORM_WEB_APP, 'Web Application'),
        (PLATFORM_MOBILE_READY, 'Mobile-ready Web App'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solution_bookings')
    service_name = models.CharField(max_length=120)
    customer_name = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=20)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=80)
    pincode = models.CharField(max_length=10)
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    budget_range = models.CharField(max_length=20, choices=BUDGET_CHOICES, default=BUDGET_STANDARD)
    preferred_platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default=PLATFORM_WEBSITE)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.service_name} solution booking for {self.customer_name}"
