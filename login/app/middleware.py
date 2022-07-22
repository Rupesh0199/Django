from django.http import HttpResponse
from .models import Security
from functools import wraps

def secureRequestmenu(func):

    @wraps(func)
    def authenticate(request, *args, **kwargs):
        
        if "uid" in request.session:

            users = Security.objects.raw(f"SELECT * FROM security WHERE auth_key = '{request.session['uid']}'")

            if not users:
                return HttpResponse("Unauthorized Access!!")

            else:

                for i in users:

                    if i.role_type == 1:
                        return func(request, *args, **kwargs)
                    else:
                        return HttpResponse("Unauthorized Access!!")
        else:
            return HttpResponse("Unauthorized Access!!")

    return authenticate

def secureRequest(func):

    @wraps(func)
    def authenticate(request, *args, **kwargs):
        
        if 'uid' in request.session:

            users = Security.objects.raw(f"SELECT * FROM security WHERE auth_key = '{request.session['uid']}'")

            if not users:

                return HttpResponse("Unauthorized Access!!")
            else:
                return func(request, *args, **kwargs)

        else:
            return HttpResponse("Unauthorized Access!!")
            
    return authenticate