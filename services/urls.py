from django.urls import path

from .views import (
    booking_tracking_data,
    booking_success,
    book_service,
    cancel_booking,
    my_bookings,
    reschedule_booking,
    retry_online_payment,
    services_home,
    technician_accept_booking,
    technician_dashboard,
    technician_update_location,
    track_booking,
    verify_online_payment,
)

app_name = 'services'

urlpatterns = [
    path('', services_home, name='home'),
    path('book/', book_service, name='book'),
    path('booking-success/', booking_success, name='booking_success'),
    path('verify-payment/', verify_online_payment, name='verify_payment'),
    path('retry-payment/<int:booking_id>/', retry_online_payment, name='retry_payment'),
    path('cancel/<int:booking_id>/', cancel_booking, name='cancel_booking'),
    path('reschedule/<int:booking_id>/', reschedule_booking, name='reschedule_booking'),
    path('my-bookings/', my_bookings, name='my_bookings'),
    path('track/<int:booking_id>/', track_booking, name='track_booking'),
    path('track-data/<int:booking_id>/', booking_tracking_data, name='booking_tracking_data'),
    path('technician/dashboard/', technician_dashboard, name='technician_dashboard'),
    path('technician/accept/<int:booking_id>/', technician_accept_booking, name='technician_accept_booking'),
    path('technician/update-location/<int:booking_id>/', technician_update_location, name='technician_update_location'),
]
