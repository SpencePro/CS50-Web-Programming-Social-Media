
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.new_view, name="new"),
    path("profile/<int:id>", views.profile_view, name="profile"),
    path("following", views.following_view, name="following"),
    path("edit/<int:id>", views.edit_view, name="edit"),
    path("like/<int:id>", views.like_view, name="like"),
    path("follow/<int:id>", views.follow_view, name="follow"),
]
