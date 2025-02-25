from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from apps.users.models import User
from apps.matchmaking.models import Match

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
  
  messages.success(request, _("Match created successfully"))
  return redirect(reverse("match_game", kwargs={"match_id": match.id}))

def match_game(request, match_id):
  match = get_object_or_404(Match, id=match_id)

  if match.finished_date_played:
    messages.error(request, _("Match already finished"))
    return redirect("/")

  if match.user1 != request.user and match.user2 != request.user:
    messages.error(request, _("You are not part of this match"))
    return redirect("/")

  return render(request, "matchmaking/pong.html", { "match": match, "is_player1": match.user1 == request.user })
