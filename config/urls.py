from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('home.urls')),
    path('services/', include('services.urls')),
    path('technologies/', include('technologies.urls')),
    path('institute/', include('institute.urls')),
    path('solutions/', include('solutions.urls')),
]
