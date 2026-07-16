from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user_id",
        "phone",
        "first_name",
        "middle_name",
        "last_name",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "first_name",
        "last_name",
        "user_id",
        "phone",
    )
    ordering = ("-created_at",)

    readonly_fields = (
        "id",
        "user_id",
        "phone",
        "first_name",
        "middle_name",
        "last_name",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request) -> bool:
        return False
