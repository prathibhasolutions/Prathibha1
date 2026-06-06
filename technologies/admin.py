from django.contrib import admin

try:
    from unfold.admin import ModelAdmin
except Exception:  # pragma: no cover
    ModelAdmin = admin.ModelAdmin

from .models import TechnologyBooking


@admin.register(TechnologyBooking)
class TechnologyBookingAdmin(ModelAdmin):
    list_display = ('service_name', 'customer_name', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method')
    search_fields = ('service_name', 'customer_name', 'phone_number')
