from django.urls import path
from .views import home_view, about_me_view, experience_view, contact_view

urlpatterns = [
    path('', home_view, name="home"),
    path('about/', about_me_view, name="about_me"),
    path('experience/', experience_view, name="experience"),
    path('contact/', contact_view, name="contact"),
]