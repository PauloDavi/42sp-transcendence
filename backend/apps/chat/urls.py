from django.urls import path

from apps.chat.views import block_friend, create_room, enter_room, friend_chat, index, unblock_friend

urlpatterns = [
    path("index", index, name="chat_index"),
    path("friend/<uuid:friend_id>/", friend_chat, name="friend_chat"),
    path("<uuid:room_uuid>/<str:room_name>/", create_room, name="create_room"),
    path("<uuid:room_uuid>/", enter_room, name="enter_room"),
    path("block-friend/<uuid:friend_id>/", block_friend, name="block_friend"),
    path("unblock-friend/<uuid:friend_id>/", unblock_friend, name="unblock_friend"),
]
