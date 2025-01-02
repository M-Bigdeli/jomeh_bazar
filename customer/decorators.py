from django.shortcuts import redirect
from functools import wraps

def redirect_if_authenticated(redirect_url='customer:account'):
    """
    This decorator will redirect the user to the given redirect_url.
    :param redirect_url: The url to redirect to.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_url)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
