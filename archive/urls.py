from django.urls import path
from .views import console_coworking_app

urlpatterns = [
    path('', console_coworking_app.index, name='home'),
]