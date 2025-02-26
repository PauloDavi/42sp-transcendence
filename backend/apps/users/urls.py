from django.urls import path
from apps.users.views import (
    home,
    login,
    logout,
    register,
    update_user,
    search_user,
    profile,
    add_friend,
    remove_friend,
    accept_friend,
    reject_friend,
    friend_profile,
)

urlpatterns = [
    path("", home, name="home"),
    path("login", login, name="login"),
    path("logout", logout, name="logout"),
    path("register", register, name="register"),
    path("user", profile, name="profile"),
    path("user/<uuid:friend_id>", friend_profile, name="friend_profile"),
    path("user/edit", update_user, name="update_user"),
    path("user/add_friend", add_friend, name="add_friend"),
    path("user/remove_friend/<uuid:friend_id>", remove_friend, name="remove_friend"),
    path("user/accept_friend/<uuid:friend_id>", accept_friend, name="accept_friend"),
    path("user/reject_friend/<uuid:friend_id>", reject_friend, name="reject_friend"),
    path("user/search", search_user, name="search_user"),
]
