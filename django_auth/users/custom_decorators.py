from django.http import JsonResponse, HttpResponse
from .models import User
import jwt
def custom_login_required(function):
    def wrap(request, *args, **kwargs):
        print(request.META.get('HTTP_AUTHORIZATION'))
        token = request.META.get('HTTP_AUTHORIZATION')
        print(token)
        token_split = token.split(' ')
        token_get = token_split[1]
        print("My Token:", token_get)
        token_decode = jwt.decode(token_get, "secret_key", algorithms=['HS256'])
        eid = token_decode.get('email')     # Additional code of a decorator to get an email
        user_id = User.object.get(email=eid)
        # entry = User.object.get(pk=user_id.id)
        entry=user_id
        print("User",entry)
        request.user_id = user_id
        if entry:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap

