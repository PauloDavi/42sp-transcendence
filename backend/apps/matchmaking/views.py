from uuid import UUID

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods, require_POST

from apps.matchmaking.forms import CreateTournament, JoinTournament
from apps.matchmaking.models import Match, Tournament, TournamentPlayer
from apps.users.models import User

# Configurações do torneio
MIN_TOURNAMENT_PLAYERS = 3


@login_required
def create_match(request: HttpRequest, opponent_id: UUID) -> HttpResponse:
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

    channel_layer = get_channel_layer()
    result = async_to_sync(channel_layer.group_send)(
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

    if result is not None:
        messages.error(request, _("Falha ao enviar o convite"))
        return redirect(next_url)

    match.save()
    return redirect(reverse("match_game", kwargs={"match_id": match.id}))


@login_required
@require_http_methods(["DELETE"])
def match_refuse(request: HttpRequest, match_id: UUID) -> HttpResponse:
    match = get_object_or_404(Match, id=match_id)

    if request.user not in {match.user1, match.user2}:
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


def match_game(request: HttpRequest, match_id: UUID) -> HttpResponse:
    match = get_object_or_404(Match, id=match_id)

    if match.finished_date_played:
        messages.error(request, _("Match already finished"))
        return redirect("/")

    if request.user not in {match.user1, match.user2}:
        messages.error(request, _("You are not part of this match"))
        return redirect("/")

    return render(
        request,
        "matchmaking/pong.html",
        {"match": match, "is_player1": match.user1 == request.user},
    )


@login_required
@require_POST
def create_tournament(request: HttpRequest) -> HttpResponse:
    tournament = Tournament(
        name=request.POST["name"],
        created_by=request.user,
    )
    tournament.save()

    messages.success(request, _("Tournament created successfully"))
    return redirect(reverse("tournament_detail", kwargs={"tournament_id": tournament.id}))


@login_required
def tournaments(request: HttpRequest) -> HttpResponse:
    join_form = JoinTournament()
    form = CreateTournament()
    active_tournament = Tournament.objects.filter(players__player=request.user, finished_at__isnull=True).first()

    if request.method == "POST":
        if active_tournament:
            messages.error(request, _("Você já está participando de um torneio ativo"))
            return redirect(reverse("tournaments"))

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
        {
            "tournaments": tournaments,
            "form": form,
            "join_form": join_form,
            "active_tournament": active_tournament,
            "MIN_TOURNAMENT_PLAYERS": MIN_TOURNAMENT_PLAYERS,
        },
    )


@login_required
def delete_tournament(request: HttpRequest, tournament_id: UUID) -> HttpResponse:
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
def join_tournament(request: HttpRequest, tournament_id: UUID) -> HttpResponse:
    active_tournament = Tournament.objects.filter(players__player=request.user, finished_at__isnull=True).first()

    if active_tournament:
        messages.error(
            request, _("Você não pode entrar em um novo torneio enquanto estiver participando de outro torneio ativo")
        )
        return redirect(reverse("tournaments"))

    tournament = get_object_or_404(Tournament, id=tournament_id)

    if tournament.players.filter(player=request.user).exists():
        messages.warning(request, _("Você já está participando deste torneio."))
        return redirect(reverse("tournaments"))

    player = TournamentPlayer.objects.get_or_create(
        player=request.user,
        display_name=request.user.username,
    )[0]

    tournament.players.add(player)
    messages.success(request, _("Você entrou no torneio com sucesso!"))
    return redirect(reverse("tournaments"))


@login_required
def tournament_detail(request: HttpRequest, tournament_id: UUID) -> HttpResponse:
    tournament = get_object_or_404(Tournament, id=tournament_id)
    return render(request, "matchmaking/tournament_detail.html", {"tournament": tournament})


@login_required
def leave_tournament(request: HttpRequest, tournament_id: UUID) -> HttpResponse:
    tournament = get_object_or_404(Tournament, id=tournament_id)

    if tournament.started_at:
        messages.error(request, _("Não é possível sair de um torneio que já começou"))
        return redirect(reverse("tournaments"))

    tournament_player = tournament.players.filter(player=request.user).first()
    if tournament_player:
        tournament_player.delete()
        messages.success(request, _("Você saiu do torneio com sucesso"))
    else:
        messages.error(request, _("Você não está neste torneio"))

    return redirect(reverse("tournaments"))


@login_required
def start_tournament(request: HttpRequest, tournament_id: UUID) -> HttpResponse:
    tournament = get_object_or_404(Tournament, id=tournament_id)

    if tournament.created_by != request.user:
        messages.error(request, _("Apenas o criador pode iniciar o torneio"))
        return redirect(reverse("tournaments"))

    if tournament.started_at:
        messages.error(request, _("Este torneio já foi iniciado"))
        return redirect(reverse("tournaments"))

    if tournament.players.count() < MIN_TOURNAMENT_PLAYERS:
        messages.error(request, _("São necessários pelo menos 3 jogadores para iniciar o torneio"))
        return redirect(reverse("tournaments"))

    tournament.started_at = now()
    tournament.save(update_fields=["started_at"])

    messages.success(request, _("Torneio iniciado com sucesso!"))
    return redirect(reverse("tournaments"))
