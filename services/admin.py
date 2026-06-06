from django.contrib import admin

try:
    from unfold.admin import ModelAdmin
except Exception:  # pragma: no cover
    ModelAdmin = admin.ModelAdmin

from .models import ServiceBooking


@admin.register(ServiceBooking)
class ServiceBookingAdmin(ModelAdmin):
    list_display = ('service_name', 'customer_name', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method')
    search_fields = ('service_name', 'customer_name', 'phone_number')
