from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from apps.users.models import User
from apps.matchmaking.models import Match
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@login_required
def create_match(request, opponent_id):
  next_url = request.GET.get("next", "/")
  opponent = User.objects.get(id=opponent_id)
  
  if opponent is None:
    messages.error(request, _("Opponent not found"))
    return redirect(next_url)
  
  if opponent == request.user:
    messages.error(request, _("You can't play against yourself"))
    return redirect(next_url)
  
  if opponent.status_online == False:
    messages.error(request, _("Opponent is offline"))
    return redirect(next_url)
  
  match = Match(
    user1=request.user,
    user2=opponent,
  )
  match.save()
  
  channel_layer = get_channel_layer()
  async_to_sync(channel_layer.group_send)(
    str(opponent.id),
    {
      "type": "send_toast",
      "message": f"{request.user.username} {_('quer jogar contra você')}",
      "tag": "warning",
      "title": str(_("Convite de partida")),
      "action": "match",
      "extra_data": {
        "accept_url": reverse("match_game", kwargs={"match_id": match.id}),
        "accept_text": str(_("Aceitar")),
        "reject_url": reverse("match_refuse", kwargs={"match_id": match.id}),
        "reject_text": str(_("Rejeitar")),
      }
    },
  )
  
  messages.success(request, _("Match created successfully"))
  return redirect(reverse("match_game", kwargs={"match_id": match.id}))

@require_http_methods(["DELETE"])
@login_required
def match_refuse(request, match_id):
  match = get_object_or_404(Match, id=match_id)
  
  if match.user1 != request.user and match.user2 != request.user:
    messages.error(request, _("You are not part of this match"))
    return redirect("/")
  
  opponent = match.user1 if match.user1 != request.user else match.user2
  
  match.delete()
  
  channel_layer = get_channel_layer()
  async_to_sync(channel_layer.group_send)(
    str(opponent.id),
    {
      "type": "send_toast",
      "message": f"{request.user.username} {_('recusou a partida')}",
      "tag": "danger",
      "title": str(_("Partida recusada")),
      "action": "match_refuse",
    },
  )
  
  return JsonResponse({"status": "success"})

def match_game(request, match_id):
  match = get_object_or_404(Match, id=match_id)

  if match.finished_date_played:
    messages.error(request, _("Match already finished"))
    return redirect("/")

  if match.user1 != request.user and match.user2 != request.user:
    messages.error(request, _("You are not part of this match"))
    return redirect("/")

  return render(request, "matchmaking/pong.html", { "match": match, "is_player1": match.user1 == request.user })
