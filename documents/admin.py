from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from documents.models import Document

admin.site.site_header = "Candidature Marché Administration"
admin.site.site_title = "Candidature Marché"
admin.site.index_title = "Gestion de la plateforme"


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "file_extension",
        "created_at",
        "is_public_to_all_users",
        "allowed_users_count",
    )
    list_filter = ("is_public_to_all_users", "created_at")
    search_fields = ("title", "description")
    filter_horizontal = ("allowed_users",)
    readonly_fields = ("created_at",)
    fieldsets = (
        (
            None,
            {
                "fields": ("title", "description", "file", "created_at"),
            },
        ),
        (
            "Droits d'accès",
            {
                "fields": ("is_public_to_all_users", "allowed_users"),
                "description": (
                    "Cochez « accessible à tous » ou sélectionnez des utilisateurs précis. "
                    "Les fichiers ne sont jamais exposés publiquement."
                ),
            },
        ),
    )

    @admin.display(description="Utilisateurs attribués")
    def allowed_users_count(self, obj):
        return obj.allowed_users.count()


class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_active", "is_superuser")


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
