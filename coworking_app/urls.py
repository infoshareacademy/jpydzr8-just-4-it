from django.urls import path
from . import views

urlpatterns = [
    path('coworking/', views.coworking_view, name='coworking'),
]
