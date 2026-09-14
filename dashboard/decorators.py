from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from functools import wraps




def admin_required(view_func):
    """Require user to be authenticated, active, and a superuser."""
    @wraps(view_func)
    @login_required(login_url='dashboard:login')
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('dashboard:login')
        return view_func(request, *args, **kwargs)
    return _wrapped
