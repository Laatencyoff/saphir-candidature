from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from documents.forms import DocumentForm
from documents.models import Document


def _is_superuser(user):
    return user.is_active and user.is_superuser


superuser_required = user_passes_test(_is_superuser, login_url="dashboard", redirect_field_name=None)


class SaphirLoginView(LoginView):
    template_name = "login.html"
    redirect_authenticated_user = True


class SaphirLogoutView(LogoutView):
    next_page = "login"


@login_required
def dashboard(request):
    if request.user.is_superuser:
        documents = Document.objects.prefetch_related("allowed_users").all()
    else:
        documents = (
            Document.objects.filter(
                Q(is_public_to_all_users=True) | Q(allowed_users=request.user)
            )
            .distinct()
        )
    return render(request, "dashboard.html", {"documents": documents})


@login_required
def download_document(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if not document.user_can_access(request.user):
        raise Http404("Document introuvable.")

    # URL pré-signée R2, valable AWS_QUERYSTRING_EXPIRE secondes (5 min).
    return redirect(document.file.url)


@login_required
def view_document(request, pk):
    """Consultation du document dans le navigateur (sans téléchargement forcé)."""
    document = get_object_or_404(Document, pk=pk)
    if not document.user_can_access(request.user):
        raise Http404("Document introuvable.")

    storage = document.file.storage
    if hasattr(storage, "inline_url"):
        url = storage.inline_url(document.file.name)
    else:  # stockage de test local : pas de paramètres de réponse S3
        url = storage.url(document.file.name)
    return redirect(url)


@login_required
@superuser_required
def document_create(request):
    form = DocumentForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        document = form.save()
        messages.success(request, f"Le document « {document.title} » a été ajouté.")
        return redirect("dashboard")
    return render(request, "document_form.html", {"form": form, "document": None})


@login_required
@superuser_required
def document_update(request, pk):
    document = get_object_or_404(Document, pk=pk)
    form = DocumentForm(request.POST or None, request.FILES or None, instance=document)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Le document « {document.title} » a été mis à jour.")
        return redirect("dashboard")
    return render(request, "document_form.html", {"form": form, "document": document})


@login_required
@superuser_required
@require_POST
def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk)
    title = document.title
    document.file.delete(save=False)
    document.delete()
    messages.success(request, f"Le document « {title} » a été supprimé.")
    return redirect("dashboard")
