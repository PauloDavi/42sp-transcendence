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
from django.views.decorators.http import require_http_methods, require_POST
from apps.matchmaking.models import Tournament, TournamentPlayer
from apps.matchmaking.forms import CreateTournament, JoinTournament
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


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

    if not opponent.status_online:
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
            },
        },
    )

    messages.success(request, _("Match created successfully"))
    return redirect(reverse("match_game", kwargs={"match_id": match.id}))


@login_required
@require_http_methods(["DELETE"])
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

    return render(
        request,
        "matchmaking/pong.html",
        {"match": match, "is_player1": match.user1 == request.user},
    )


@login_required
@require_POST
def create_tournament(request):
    tournament = Tournament(
        name=request.POST["name"],
        created_by=request.user,
    )
    tournament.save()

    messages.success(request, _("Tournament created successfully"))
    return redirect(
        reverse("tournament_detail", kwargs={"tournament_id": tournament.id})
    )


@login_required
def tournaments(request):
    join_form = JoinTournament()
    form = CreateTournament()
    if request.method == "POST":
        form = CreateTournament(request.POST)
        if form.is_valid():
            tournament = form.save(commit=False)
            tournament.created_by = request.user
            tournament.save()

            player = TournamentPlayer.objects.create(
                player=request.user,
                display_name=form.cleaned_data["display_name"],
            )

            tournament.players.add(player)

    page = request.GET.get("page", 1)
    paginator = Paginator(Tournament.objects.all().order_by("-created_at"), 5)
    try:
        tournaments = paginator.page(page)
    except PageNotAnInteger:
        tournaments = paginator.page(1)
    except EmptyPage:
        tournaments = paginator.page(paginator.num_pages)

    return render(
        request,
        "matchmaking/tournaments.html",
        {"tournaments": tournaments, "form": form, "join_form": join_form},
    )


@login_required
def delete_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    if tournament.created_by != request.user:
        messages.error(request, _("You are not the creator of this tournament"))
        return redirect(reverse("tournaments"))

    if tournament.started_at:
        messages.error(request, _("Tournament already started"))
        return redirect(reverse("tournaments"))

    tournament.delete()
    messages.success(request, _("Tournament deleted successfully"))
    return redirect(reverse("tournaments"))


@login_required
def join_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    if tournament.players.filter(player=request.user).exists():
        messages.warning(request, _("Você já está participando deste torneio."))
        return redirect(reverse("tournaments"))

    player = TournamentPlayer.objects.get_or_create(
        player=request.user,
        display_name=request.user.username,
    )
    tournament.players.add(player)
    messages.success(request, _("Você entrou no torneio com sucesso!"))
    return redirect(reverse("tournaments"))


@login_required
def tournament_detail(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    return render(
        request, "matchmaking/tournament_detail.html", {"tournament": tournament}
    )
