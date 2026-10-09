from pathlib import Path

from django.conf import settings
from django.db import models

from documents.storage import PrivateR2Storage


class Document(models.Model):
    title = models.CharField("titre", max_length=255)
    description = models.TextField("description", blank=True)
    file = models.FileField(
        "fichier",
        storage=PrivateR2Storage(),
        upload_to="documents/%Y/%m/",
    )
    created_at = models.DateTimeField("date d'ajout", auto_now_add=True)
    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="utilisateurs autorisés",
        related_name="accessible_documents",
        blank=True,
        help_text="Laissez vide si le document est destiné à tous les utilisateurs connectés.",
    )
    is_public_to_all_users = models.BooleanField(
        "accessible à tous les utilisateurs connectés",
        default=False,
        help_text="Si coché, tout utilisateur authentifié peut télécharger ce document.",
    )

    class Meta:
        verbose_name = "document"
        verbose_name_plural = "documents"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    # Formats qu'un navigateur sait afficher directement (bouton « Consulter »).
    PREVIEWABLE_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "gif", "webp", "svg", "txt"}

    @property
    def file_extension(self) -> str:
        suffix = Path(self.file.name).suffix.lower().lstrip(".")
        return suffix or "—"

    @property
    def can_preview(self) -> bool:
        return self.file_extension in self.PREVIEWABLE_EXTENSIONS

    def user_can_access(self, user) -> bool:
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if self.is_public_to_all_users:
            return True
        return self.allowed_users.filter(pk=user.pk).exists()
