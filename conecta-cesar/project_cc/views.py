from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _


def csrf_failure(request, reason=""):
    """Replaces Django's default 403 page on CSRF failure with a redirect
    back to the same page and an error message, instead of a dead end."""
    messages.error(
        request, _("Sua sessão expirou ou o formulário é inválido. Tente novamente.")
    )
    return HttpResponseRedirect(request.path)
