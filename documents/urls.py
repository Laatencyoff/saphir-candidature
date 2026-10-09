from django.urls import path

from documents import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("connexion/", views.SaphirLoginView.as_view(), name="login"),
    path("deconnexion/", views.SaphirLogoutView.as_view(), name="logout"),
    path("documents/ajouter/", views.document_create, name="document_create"),
    path("documents/<int:pk>/modifier/", views.document_update, name="document_update"),
    path("documents/<int:pk>/supprimer/", views.document_delete, name="document_delete"),
    path("documents/<int:pk>/telecharger/", views.download_document, name="download_document"),
]
