from django.urls import path
from .views import continue_with_google, register

app_name = 'accounts'

urlpatterns = [
    path('register/', register, name='register'),
    path('google/login/', continue_with_google, name='google_login'),
]
