from functools import wraps
from django.http import HttpResponseForbidden
from .models import Role

def role_required(*roles):
    def deco(view):
        @wraps(view)
        def inner(request,*a,**kw):
            p=getattr(request.user,'profile',None)
            if not p or p.role not in roles:
                return HttpResponseForbidden("Brak uprawnień.")
            return view(request,*a,**kw)
        return inner
    return deco
