from django.urls import path
from apps.chat.views import index, create_room, enter_room


urlpatterns = [
    path("index", index, name="chat_index"),
    path("<str:room_uuid>/<str:room_name>/", create_room, name="create_room"),
    path("<str:room_uuid>/", enter_room, name="enter_room"),
]
