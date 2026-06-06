from django.urls import path
from . import views

app_name = 'solutions'

urlpatterns = [
    path('', views.solutions_home, name='home'),
    path('service/<slug:slug>/', views.service_detail, name='service_detail'),
    path('book/', views.book_solution, name='book'),
    path('booking-success/', views.booking_success, name='booking_success'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('reschedule/<int:booking_id>/', views.reschedule_booking, name='reschedule_booking'),
]
