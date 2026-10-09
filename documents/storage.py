from storages.backends.s3boto3 import S3Boto3Storage


class PrivateR2Storage(S3Boto3Storage):
    """Stockage privé sur Cloudflare R2 (API S3).

    Aucun objet n'est public : les accès passent par des URLs pré-signées
    temporaires (``AWS_QUERYSTRING_EXPIRE`` secondes), générées uniquement par la
    vue ``download_document`` après vérification des droits.
    """

    default_acl = None
    querystring_auth = True
    file_overwrite = False
    custom_domain = None  # garantit l'usage de l'endpoint R2 signé

    def inline_url(self, name):
        """URL pré-signée qui demande à R2 de servir le fichier en affichage
        inline (consultation dans le navigateur) au lieu du téléchargement
        imposé par le Content-Disposition enregistré à l'upload."""
        return self.url(name, parameters={"ResponseContentDisposition": "inline"})

    def get_object_parameters(self, name):
        # Force le téléchargement (plutôt que l'affichage inline) avec le nom
        # d'origine lorsque le navigateur suit l'URL pré-signée.
        params = super().get_object_parameters(name)
        filename = name.rsplit("/", 1)[-1]
        params.setdefault("ContentDisposition", f'attachment; filename="{filename}"')
        return params
