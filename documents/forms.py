from django import forms
from django.contrib.auth import get_user_model

from documents.models import Document

User = get_user_model()

INPUT_CLASSES = (
    "w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900 outline-none "
    "ring-saphir-500 focus:border-saphir-600 focus:ring-2"
)


class DocumentForm(forms.ModelForm):
    allowed_users = forms.ModelMultipleChoiceField(
        label="Utilisateurs autorisés",
        queryset=User.objects.filter(is_active=True, is_superuser=False).order_by("username"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Ignoré si le document est accessible à tous les utilisateurs connectés.",
    )

    class Meta:
        model = Document
        fields = ["title", "description", "file", "is_public_to_all_users", "allowed_users"]
        widgets = {
            "title": forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "Ex. Règlement de consultation"}),
            "description": forms.Textarea(attrs={"class": INPUT_CLASSES, "rows": 3}),
            "file": forms.FileInput(
                attrs={
                    "class": "block w-full text-sm text-slate-700 file:mr-4 file:rounded-md file:border-0 "
                    "file:bg-saphir-100 file:px-3 file:py-2 file:text-sm file:font-medium file:text-saphir-800 "
                    "hover:file:bg-saphir-200"
                }
            ),
            "is_public_to_all_users": forms.CheckboxInput(
                attrs={"class": "h-4 w-4 rounded border-slate-300 text-saphir-700 focus:ring-saphir-500"}
            ),
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("is_public_to_all_users") and not cleaned.get("allowed_users"):
            self.add_error(
                "allowed_users",
                "Sélectionnez au moins un utilisateur ou cochez « accessible à tous ».",
            )
        return cleaned
