from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.views.static import serve
from django.contrib import admin
from django.urls import include, path, re_path


urlpatterns = i18n_patterns(
    re_path(r"^rosetta/", include("rosetta.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
    path("", include("apps.users.urls")),
    path("matchmaking/", include("apps.matchmaking.urls")),
    path("chat/", include("apps.chat.urls")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
) + [
    path("accounts/", include("apps.users.providers.fortytwo.urls")),
]
