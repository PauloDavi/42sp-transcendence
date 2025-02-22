from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Message, Chat, ChatParticipants
from django.utils import timezone

@login_required
def index(request):
    return render(request, "chat/index.html")

@login_required
def create_room(request, room_uuid, room_name):
    if Chat.objects.filter(name=room_name).exists():
        return render(request, "chat/room_already_exists.html", {"room_name": room_name})

    chat = Chat.objects.create(id=room_uuid, name=room_name, is_group_chat=True)
    ChatParticipants.objects.create(chat=chat, user=request.user, joined_at=timezone.now())

    print(f"CREATED ROOM: room_name: {room_name} room_uuid: {room_uuid}")

    return render(request, "chat/room.html", {"room_uuid": room_uuid})

@login_required
def enter_room(request, room_uuid):
    if not Chat.objects.filter(id=room_uuid).exists():
        return render(request, "chat/room_not_found.html", {"room_uuid": room_uuid})

    print(f"FOUND ROOM: room_uuid: {room_uuid}")
    return render(request, "chat/room.html", {"room_uuid": room_uuid})
