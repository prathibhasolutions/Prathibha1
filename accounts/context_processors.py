from django.conf import settings


def oauth_flags(request):
    return {
        'google_oauth_ready': bool(
            getattr(settings, 'GOOGLE_CLIENT_ID', '')
            and getattr(settings, 'GOOGLE_CLIENT_SECRET', '')
        )
    }