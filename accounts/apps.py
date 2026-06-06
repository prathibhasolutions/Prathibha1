from django.apps import AppConfig
from django.conf import settings


def sync_google_social_app():
    google_client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
    google_client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', '')

    if not google_client_id or not google_client_secret:
        return

    try:
        from django.contrib.sites.models import Site
        from django.db import OperationalError, ProgrammingError
        from allauth.socialaccount.models import SocialApp

        current_site = Site.objects.get_current()
        social_app, _ = SocialApp.objects.update_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': google_client_id,
                'secret': google_client_secret,
                'key': '',
            },
        )
        social_app.sites.set([current_site])
    except (OperationalError, ProgrammingError):
        return


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        sync_google_social_app()
