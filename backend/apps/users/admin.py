from typing import ClassVar

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.http import HttpRequest

from apps.users.forms import UserChangeForm
from apps.users.models import User


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm

    list_display: ClassVar[list[str]] = [
        "username",
        "email",
        "avatar",
        "is_active",
        "is_staff",
        "status_online",
        "wins",
        "losses",
    ]
    list_filter: ClassVar[list[str]] = ["is_active", "is_staff", "status_online"]
    search_fields: ClassVar[list[str]] = ["username", "email"]

    fieldsets: ClassVar[list[tuple]] = [
        (
            None,
            {
                "fields": [
                    "id",
                    "username",
                    "email",
                    "avatar",
                    "is_active",
                    "is_staff",
                    "status_online",
                    "wins",
                    "losses",
                    "created_at",
                    "updated_at",
                ],
            },
        ),
    ]
    readonly_fields: ClassVar[list[str]] = ["id", "status_online", "created_at", "updated_at"]

    list_per_page = 20

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
