from django.urls import path

from .views import (
    booking_success,
    book_technology,
    cancel_booking,
    my_bookings,
    reschedule_booking,
    retry_online_payment,
    technologies_home,
    verify_online_payment,
)

app_name = 'technologies'

urlpatterns = [
    path('', technologies_home, name='home'),
    path('book/', book_technology, name='book'),
    path('booking-success/', booking_success, name='booking_success'),
    path('verify-payment/', verify_online_payment, name='verify_payment'),
    path('retry-payment/<int:booking_id>/', retry_online_payment, name='retry_payment'),
    path('cancel/<int:booking_id>/', cancel_booking, name='cancel_booking'),
    path('reschedule/<int:booking_id>/', reschedule_booking, name='reschedule_booking'),
    path('my-bookings/', my_bookings, name='my_bookings'),
]
