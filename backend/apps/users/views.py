from uuid import UUID

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from apps.matchmaking.models import Match
from apps.users.forms import UserCreationForm, UserEditProfileForm, UserLoginForm
from apps.users.models import Friendship, FriendshipStatus, User


@login_required
def home(request: HttpRequest) -> HttpResponse:
    return render(request, "users/home.html")


def login(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("home")

    form = UserLoginForm()
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            password = form.cleaned_data["password"]

            user = auth.authenticate(
                request,
                username=name,
                password=password,
            )

            if user is not None:
                auth.login(request, user)
                messages.success(request, _("Login realizado com sucesso"))
                return redirect("home")

            messages.error(request, _("Usuário ou senha inválidos"))
            return redirect("login")

    return render(request, "users/login.html", {"form": form})


def logout(request: HttpRequest) -> HttpResponse:
    messages.success(request, _("Usuário deslogado com sucesso"))
    auth.logout(request)
    return redirect("login")


def register(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("home")

    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth.login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, _("Usuário criado com sucesso"))
            return redirect("home")

    return render(request, "users/register.html", {"form": form})


@login_required
def update_user(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = UserEditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save(request=request)
            messages.success(request, _("Seu perfil foi atualizado com sucesso!"))
            return redirect("profile")
    else:
        form = UserEditProfileForm(instance=request.user)

    return render(request, "users/update_user.html", {"form": form})


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    friends = Friendship.objects.filter(Q(user1=request.user) | Q(user2=request.user))

    friends = [
        {
            "id": friend.user1.id if friend.user1 != request.user else friend.user2.id,
            "username": friend.user1.username if friend.user1 != request.user else friend.user2.username,
            "avatar": friend.user1.avatar.url if friend.user1 != request.user else friend.user2.avatar.url,
            "is_request": friend.requestd_by == request.user,
            "status_online": friend.user1.status_online if friend.user1 != request.user else friend.user2.status_online,
            "status": friend.status,
        }
        for friend in friends
    ]

    matches = Match.objects.filter(Q(user1=request.user) | Q(user2=request.user)).order_by("-started_date_played")

    match_filter = request.GET.get("match_filter", "")
    if match_filter == "wins":
        matches = matches.filter(winner=request.user).order_by("-started_date_played")
    elif match_filter == "losses":
        matches = matches.exclude(winner=request.user).order_by("-started_date_played")

    matches = [
        {
            "id": match.id,
            "opponent": match.user1 if match.user1 != request.user else match.user2,
            "points": match.score_user1 if match.user1 == request.user else match.score_user2,
            "opponent_points": match.score_user1 if match.user1 != request.user else match.score_user2,
            "started_date_played": match.started_date_played,
            "finished_date_played": match.finished_date_played,
        }
        for match in matches
    ]

    paginator = Paginator(matches, 5)
    page_number = request.GET.get("page")
    matches = paginator.get_page(page_number)

    return render(request, "users/profile.html", {"friends": friends, "matches": matches})


@login_required
def add_friend(request: HttpRequest) -> HttpResponse:
    friend_id = request.POST.get("friend_id")
    friend = User.objects.get(id=friend_id)

    if friend == request.user:
        messages.error(request, _("Você não pode adicionar a si mesmo como amigo!"))
        return redirect("profile")

    if friend is None:
        messages.error(request, _("Usuário não encontrado!"))
        return redirect("profile")

    Friendship(
        user1=request.user,
        user2=friend,
        requestd_by=request.user,
    ).save()
    messages.success(request, _("Solicitação de amizade enviada com sucesso!"))
    return redirect("profile")


@login_required
def remove_friend(request: HttpRequest, friend_id: UUID) -> HttpResponse:
    friend = User.objects.get(id=friend_id)
    if friend is None:
        messages.error(request, _("Usuário não encontrado!"))
        return redirect("profile")

    friendship = Friendship.objects.filter(
        Q(user1=request.user, user2=friend) | Q(user1=friend, user2=request.user),
    ).first()

    if friendship is None:
        messages.error(request, _("Amigo não encontrado!"))
        return redirect("profile")

    friendship.delete()
    messages.success(request, _("Amigo removido com sucesso!"))
    return redirect("profile")


@login_required
def search_user(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    if query:
        friendships = Friendship.objects.filter(Q(user1=request.user) | Q(user2=request.user))
        already_friends = [
            friend.user1.id if friend.user1 != request.user else friend.user2.id for friend in friendships
        ]

        users = (
            User.objects.filter(Q(email__icontains=query) | Q(username__icontains=query))
            .exclude(id=request.user.id)
            .exclude(id__in=already_friends)
            .distinct()[:10]
        )

        users_data = [
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "avatar": user.avatar.url,
            }
            for user in users
        ]
        return JsonResponse(users_data, safe=False)

    return JsonResponse([], safe=False)


@login_required
def accept_friend(request: HttpRequest, friend_id: UUID) -> HttpResponse:
    friend = User.objects.get(id=friend_id)
    if friend is None:
        messages.error(request, _("Usuário não encontrado!"))
        return redirect("profile")

    friendship = Friendship.objects.filter(
        Q(user1=request.user, user2=friend) | Q(user1=friend, user2=request.user),
    ).first()

    if friendship is None:
        messages.error(request, _("Amigo não encontrado!"))
        return redirect("profile")

    friendship.status = FriendshipStatus.ACCEPTED
    friendship.save(update_fields=["status"])
    messages.success(request, _("Amigo aceito com sucesso!"))
    return redirect("profile")


@login_required
def reject_friend(request: HttpRequest, friend_id: UUID) -> HttpResponse:
    friend = User.objects.get(id=friend_id)
    if friend is None:
        messages.error(request, _("Usuário não encontrado!"))
        return redirect("profile")

    friendship = Friendship.objects.filter(
        Q(user1=request.user, user2=friend) | Q(user1=friend, user2=request.user),
    ).first()

    if friendship is None:
        messages.error(request, _("Amigo não encontrado!"))
        return redirect("profile")

    friendship.status = FriendshipStatus.REJECTED
    friendship.save(update_fields=["status"])
    messages.success(request, _("Amigo rejeitado com sucesso!"))
    return redirect("profile")


@login_required
def friend_profile(request: HttpRequest, friend_id: UUID) -> HttpResponse:
    friend = get_object_or_404(User, id=friend_id)

    return render(request, "users/friend.html", {"friend": friend})
