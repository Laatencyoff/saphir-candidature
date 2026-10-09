# Saphir candidature

Portail sécurisé de partage et de téléchargement de documents pour un appel à candidatures.

Les fichiers sont stockés dans un bucket **privé Cloudflare R2** (API S3) et ne sont jamais servis publiquement : la vue de téléchargement vérifie les droits de l’utilisateur puis redirige vers une **URL pré-signée valable 5 minutes**.

## Installation

```powershell
cd C:\Users\lucas\OneDrive\Documents\projets\saphir-candidature
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env   # puis renseigner les valeurs
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- Connexion candidats : http://127.0.0.1:8000/
- Administration (comptes utilisateurs) : http://127.0.0.1:8000/admin/

## Configuration Cloudflare R2

1. Dans le dashboard Cloudflare, **R2 > Create bucket** (ex. `saphir-candidature`). Ne pas activer l’accès public.
2. **R2 > Manage R2 API Tokens > Create API token**, permission *Object Read & Write*, limité à ce bucket.
3. Renseigner dans `.env` :

| Variable | Valeur |
|---|---|
| `R2_ACCESS_KEY_ID` | Access Key ID du jeton |
| `R2_SECRET_ACCESS_KEY` | Secret Access Key du jeton |
| `R2_BUCKET_NAME` | Nom du bucket |
| `R2_ENDPOINT_URL` | `https://<ACCOUNT_ID>.r2.cloudflarestorage.com` |

Réglages appliqués (`saphir/settings.py`) : signature `s3v4`, région `auto`, `AWS_DEFAULT_ACL = None`, `AWS_QUERYSTRING_AUTH = True`, `AWS_QUERYSTRING_EXPIRE = 300`.

## Utilisation

- `/admin/` sert uniquement à créer et gérer les comptes utilisateurs (réservé au superutilisateur).
- Depuis le tableau de bord (`/`), le superutilisateur ajoute, modifie et supprime les documents, et définit leurs droits d’accès (utilisateurs précis ou « accessible à tous les utilisateurs connectés »).
- Les candidats ne voient que les documents qui leur sont attribués.

## Tests

```powershell
python manage.py test documents
```

Les tests remplacent le stockage R2 par un dossier temporaire local : aucune connexion réseau n’est nécessaire.
