from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Message, Chat, ChatParticipants
from apps.users.models import User
from django.utils import timezone

@login_required
def index(request):
    return render(request, "chat/index.html")

@login_required
def create_room(request, room_uuid, room_name):
    chat = Chat.objects.create(id=room_uuid, name=room_name, is_group_chat=True)
    ChatParticipants.objects.create(chat=chat, user=request.user, joined_at=timezone.now())

    return redirect("enter_room", room_uuid=room_uuid)

@login_required
def enter_room(request, room_uuid):
    chat = get_object_or_404(Chat, id=room_uuid)
    messages = Message.objects.filter(chat=chat).order_by("sent_at")
    messages_list = list(messages.values("sender", "content", "sent_at"))
    sender = list(messages.values("sender"))
    
    for i in range(len(sender)):
        sender[i] = User.objects.get(id=sender[i]["sender"]).username

    for i in range(len(messages_list)):
        messages_list[i]["sender"] = sender[i]

    context = {
        "chat": chat,
        "messages": messages_list,
    }

    return render(request, "chat/room.html", context)
