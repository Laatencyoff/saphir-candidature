import os
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from documents.models import Document

User = get_user_model()


class LocalStorageTestCase(TestCase):
    """Remplace le stockage R2 par un dossier temporaire local pendant les tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._tmp_dir = tempfile.mkdtemp(prefix="saphir-test-")
        cls._file_field = Document._meta.get_field("file")
        cls._original_storage = cls._file_field.storage
        cls._file_field.storage = FileSystemStorage(
            location=cls._tmp_dir, base_url="/test-storage/"
        )

    @classmethod
    def tearDownClass(cls):
        cls._file_field.storage = cls._original_storage
        shutil.rmtree(cls._tmp_dir, ignore_errors=True)
        super().tearDownClass()


class DocumentAccessTests(LocalStorageTestCase):
    def setUp(self):
        self.owner = User.objects.create_user("candidat", password="MotDePasseFort1")
        self.other = User.objects.create_user("autre", password="MotDePasseFort1")
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "MotDePasseFort1")
        self.document = Document.objects.create(
            title="Cahier des charges",
            file=SimpleUploadedFile("cdc.pdf", b"%PDF-1.4 test"),
        )
        self.document.allowed_users.add(self.owner)

    def test_anonymous_is_redirected(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_owner_is_redirected_to_storage_url(self):
        self.client.login(username="candidat", password="MotDePasseFort1")
        response = self.client.get(reverse("download_document", args=[self.document.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.document.file.url)
        self.assertTrue(response.url.startswith("/test-storage/"))

    def test_owner_can_view_inline(self):
        self.client.login(username="candidat", password="MotDePasseFort1")
        response = self.client.get(reverse("view_document", args=[self.document.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/test-storage/"))

    def test_unassigned_user_cannot_view_inline(self):
        self.client.login(username="autre", password="MotDePasseFort1")
        response = self.client.get(reverse("view_document", args=[self.document.pk]))
        self.assertEqual(response.status_code, 404)

    def test_preview_button_only_for_previewable_formats(self):
        self.client.login(username="candidat", password="MotDePasseFort1")
        self.assertTrue(self.document.can_preview)  # .pdf
        self.assertContains(self.client.get(reverse("dashboard")), "Consulter")
        archive = Document.objects.create(
            title="Archive", file=SimpleUploadedFile("dossier.zip", b"PK"), is_public_to_all_users=True
        )
        self.assertFalse(archive.can_preview)

    def test_unassigned_user_gets_404(self):
        self.client.login(username="autre", password="MotDePasseFort1")
        response = self.client.get(reverse("download_document", args=[self.document.pk]))
        self.assertEqual(response.status_code, 404)

    def test_public_document_visible_to_all_logged_in_users(self):
        self.document.is_public_to_all_users = True
        self.document.save()
        self.client.login(username="autre", password="MotDePasseFort1")
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Cahier des charges")

    def test_non_superuser_cannot_access_admin(self):
        self.client.login(username="candidat", password="MotDePasseFort1")
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 403)


class DocumentManagementTests(LocalStorageTestCase):
    def setUp(self):
        self.candidate = User.objects.create_user("candidat", password="MotDePasseFort1")
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "MotDePasseFort1")
        self.document = Document.objects.create(
            title="Annexe",
            file=SimpleUploadedFile("annexe.xlsx", b"PK demo"),
            is_public_to_all_users=True,
        )

    def test_candidate_cannot_open_create_form(self):
        self.client.login(username="candidat", password="MotDePasseFort1")
        response = self.client.get(reverse("document_create"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))

    def test_candidate_cannot_post_document(self):
        self.client.login(username="candidat", password="MotDePasseFort1")
        response = self.client.post(
            reverse("document_create"),
            {"title": "Pirate", "file": SimpleUploadedFile("x.pdf", b"x"), "is_public_to_all_users": "on"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Document.objects.filter(title="Pirate").exists())

    def test_candidate_cannot_delete_document(self):
        self.client.login(username="candidat", password="MotDePasseFort1")
        self.client.post(reverse("document_delete", args=[self.document.pk]))
        self.assertTrue(Document.objects.filter(pk=self.document.pk).exists())

    def test_admin_creates_document_with_specific_users(self):
        self.client.login(username="admin", password="MotDePasseFort1")
        response = self.client.post(
            reverse("document_create"),
            {
                "title": "Cahier des charges",
                "description": "Pièce principale",
                "file": SimpleUploadedFile("cdc.pdf", b"%PDF-1.4"),
                "allowed_users": [self.candidate.pk],
            },
        )
        self.assertRedirects(response, reverse("dashboard"))
        created = Document.objects.get(title="Cahier des charges")
        self.assertFalse(created.is_public_to_all_users)
        self.assertEqual(list(created.allowed_users.all()), [self.candidate])

    def test_create_requires_users_or_public(self):
        self.client.login(username="admin", password="MotDePasseFort1")
        response = self.client.post(
            reverse("document_create"),
            {"title": "Sans accès", "file": SimpleUploadedFile("x.pdf", b"x")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Document.objects.filter(title="Sans accès").exists())

    def test_admin_updates_access_without_new_file(self):
        self.client.login(username="admin", password="MotDePasseFort1")
        response = self.client.post(
            reverse("document_update", args=[self.document.pk]),
            {"title": "Annexe", "description": "", "allowed_users": [self.candidate.pk]},
        )
        self.assertRedirects(response, reverse("dashboard"))
        self.document.refresh_from_db()
        self.assertFalse(self.document.is_public_to_all_users)
        self.assertIn(self.candidate, self.document.allowed_users.all())
        self.assertTrue(self.document.file.name.endswith(".xlsx"))

    def test_admin_deletes_document_and_file(self):
        self.client.login(username="admin", password="MotDePasseFort1")
        path = self.document.file.path
        response = self.client.post(reverse("document_delete", args=[self.document.pk]))
        self.assertRedirects(response, reverse("dashboard"))
        self.assertFalse(Document.objects.filter(pk=self.document.pk).exists())
        self.assertFalse(os.path.exists(path))

    def test_dashboard_shows_admin_actions_only_to_superuser(self):
        self.client.login(username="admin", password="MotDePasseFort1")
        self.assertContains(self.client.get(reverse("dashboard")), "Ajouter un document")
        self.client.login(username="candidat", password="MotDePasseFort1")
        self.assertNotContains(self.client.get(reverse("dashboard")), "Ajouter un document")
