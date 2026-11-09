from django.urls import path
from .views import about_me_view

urlpatterns = [
    path('', about_me_view, name="about_me")
]
