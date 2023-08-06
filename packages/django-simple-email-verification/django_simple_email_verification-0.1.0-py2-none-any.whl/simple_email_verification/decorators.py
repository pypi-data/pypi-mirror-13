from django.shortcuts import render, redirect
from .views import send_token_view
from .models import VerifiedEmail
from .forms import VerifiedEmailForm
from simple_email_verification import get_settings

settings = get_settings()


def require_verification_token(view_func):
    def verify(request, *args, **kwargs):
        response = send_token_view(request)
        token = request.GET.get(settings.get('GET_TOKEN_PARAM_NAME'), None)
        if token:
            try:
                v = VerifiedEmail.objects.get(verification_token=token.encode('ascii'))
            except VerifiedEmail.DoesNotExist:
                pass
            else:
                v.update_last_verified()
                request.session[settings.get('SESSION_TOKEN_PARAM_NAME')] = token
                response = redirect(request.path_info, context=request)
        else:
            token = request.session.get(settings.get('SESSION_TOKEN_PARAM_NAME'))
            if token:
                try:
                    VerifiedEmail.objects.get(verification_token=token)
                    return view_func(request, *args, **kwargs)
                except VerifiedEmail.DoesNotExist:
                    pass
        if response:
            return response
        else:
            verification_form = VerifiedEmailForm()
            return render(request, settings.get('VERIFICATION_FORM_TEMPLATE'), {'form': verification_form.as_p()})

    return verify
