from uuid import UUID

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.chat.models import Chat, ChatParticipants
from apps.users.models import User


@login_required
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "chat/index.html")


@login_required
def create_room(request: HttpRequest, room_uuid: UUID, room_name: str) -> HttpResponse:
    chat = Chat.objects.create(id=room_uuid, name=room_name, is_group_chat=True)
    ChatParticipants.objects.create(chat=chat, user=request.user, joined_at=timezone.now())

    return redirect("enter_room", room_uuid=room_uuid)


@login_required
def friend_chat(request: HttpRequest, friend_id: int) -> HttpResponse:
    friend = get_object_or_404(User, id=friend_id)
    chat = Chat.objects.filter(is_group_chat=False, participants=request.user).filter(participants=friend).first()

    if not chat:
        chat = Chat.objects.create(
            is_group_chat=False,
            name=f"{request.user.username} - {friend.username}",
        )
        chat.participants.add(request.user, friend)

    return redirect("enter_room", room_uuid=chat.id)


@login_required
def enter_room(request: HttpRequest, room_uuid: UUID) -> HttpResponse:
    chat = get_object_or_404(Chat, id=room_uuid)
    ChatParticipants.objects.filter(chat=chat, user=request.user).update(messages_not_read=0)
    return render(request, "chat/room.html", {"chat": chat})
