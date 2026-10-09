from django.shortcuts import render


class SuperuserAdminOnlyMiddleware:
    """Interdit /admin/ aux comptes qui ne sont pas superutilisateur."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/"):
            user = request.user
            if user.is_authenticated and not user.is_superuser:
                return render(request, "403.html", status=403)
        return self.get_response(request)
