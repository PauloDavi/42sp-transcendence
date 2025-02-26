from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from apps.users.models import User
from apps.users.forms import UserChangeForm


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm

    list_display = [
        "username",
        "email",
        "avatar",
        "is_active",
        "is_staff",
        "status_online",
        "wins",
        "losses",
    ]
    list_filter = ["is_active", "is_staff", "status_online"]
    search_fields = ["username", "email"]

    fieldsets = [
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
                ]
            },
        )
    ]
    readonly_fields = ["id", "status_online", "created_at", "updated_at"]

    list_per_page = 20

    def has_add_permission(self, request):
        return False


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
