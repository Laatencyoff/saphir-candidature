# Saphir candidature

Portail sécurisé de partage et de téléchargement de documents pour un appel à candidatures.

Les fichiers sont stockés hors du web public (`private_media/`) et ne sont servis que par une vue Django authentifiée.

## Démarrage

```powershell
cd C:\Users\lucas\OneDrive\Documents\projets\saphir-candidature
.\.venv\Scripts\Activate.ps1
python manage.py createsuperuser
python manage.py runserver
```

- Connexion candidats : http://127.0.0.1:8000/
- Administration : http://127.0.0.1:8000/admin/

## Utilisation

- `/admin/` sert uniquement à créer et gérer les comptes utilisateurs (réservé au superutilisateur).
- Depuis le tableau de bord (`/`), le superutilisateur ajoute, modifie et supprime les documents, et définit leurs droits d’accès (utilisateurs précis ou « accessible à tous les utilisateurs connectés »).
- Les candidats ne voient que les documents qui leur sont attribués.
