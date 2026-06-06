from .views import is_technician


def service_role_flags(request):
    return {
        'is_technician_user': is_technician(request.user),
    }