from django.contrib import admin

try:
    from unfold.admin import ModelAdmin
except Exception:  # pragma: no cover
    ModelAdmin = admin.ModelAdmin

from .models import SolutionBooking


@admin.register(SolutionBooking)
class SolutionBookingAdmin(ModelAdmin):
    list_display = ('service_name', 'customer_name', 'status', 'budget_range', 'created_at')
    list_filter = ('status', 'budget_range', 'preferred_platform')
    search_fields = ('service_name', 'customer_name', 'phone_number')
