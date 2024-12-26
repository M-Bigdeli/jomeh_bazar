from django.shortcuts import redirect
from functools import wraps

def redirect_if_authenticated(redirect_url='customer:account'):
    """

    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_url)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
