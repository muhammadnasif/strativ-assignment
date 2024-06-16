from django.contrib import admin
from django.urls import path, include
import weather

urlpatterns = [
    path('admin/', admin.site.urls),
    path('weather/', include("weather.urls"))
]
