# game_app/urls.py
from django.urls import path
from .views import home, register, login_view, logout_view, register_view

urlpatterns = [
    path("", home, name="home"),
    path("register/", register, name="register"),  # UserCreationForm version
    path("custom_register/", register_view, name="custom_register"),  # Your custom version
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
]