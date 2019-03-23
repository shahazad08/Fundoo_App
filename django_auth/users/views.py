import json
import jwt
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.template import loader
from django.http import JsonResponse
from django.contrib import messages
from django.urls import resolve
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from requests import auth
from rest_framework_jwt.settings import api_settings
from django.http import JsonResponse
from .serializers import UserSerializer, LoginSerializer, LabelSerializer
from rest_framework.renderers import TemplateHTMLRenderer
from .models import User
from django.http import HttpResponse
from django.shortcuts import render
# from rest_framework import serializers, status
from rest_framework.generics import CreateAPIView  # Used for a create-only endpoints, provides a post method handler
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from rest_framework.views import APIView  # Taking the views of REST framework Request & Response
from django.contrib.auth import logout
from .tokens import account_activation_token
from django.urls import reverse
from .forms import SignupForm
from .serializers import NoteSerializer, ReadNoteSerializer, PageNoteSerializer
from rest_framework.decorators import api_view
# from .models import User, CreateNotes, Labels, MapLabel
from django.conf import settings
from rest_framework import generics  # For a List API use a generics
# from .paginate import PostLimitOffsetPagination, PostPageNumberPagination  # Creating our own no. of records in a Pages
# from rest_framework.filters import SearchFilter  # it allows users to filter down a queryset based on a model's
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.core.cache.backends.base import DEFAULT_TIMEOUT  # Setting a time for a cache to store
from .custom_decorators import custom_login_required
from django.utils.decorators import method_decorator
from .services import redis_information, upload_image,delete_from_s3
from self import self
import imghdr
from PIL import Image
from django.views.decorators.http import require_http_methods


def home(request):
    return render(request, "home.html", {})  # home page

def log_me(request):
    return render(request, 'user_login.html', {})

def signup(request):
    if request.method == 'POST':  # IF method id POST
        form = SignupForm(request.POST)  # SignUp Form
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()  # Save in a DB
            current_site = get_current_site(request)  # get the current site by comparing the domain with the host
            # name from the request.get_host() method.
            message = render_to_string('activate.html', {  # Pass the link information to the message variable
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            mail_subject = 'Activate your blog account.'
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return JsonResponse('Please confirm your email address to complete the registration', safe=False)
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

class Registerapi(CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        res = {"message": "something bad happened",
               "data": {},
               "success": False}
        print(request.data)
        email = request.data['email']
        print(email)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        # date_joined=request.data['date_joined']
        password = request.POST.get('password')

        if email and password is not "":

            user_already = User.object.filter(email=email)

            if user_already:
                res['message'] = "User Allready Exists"
                res['success'] = True
                return JsonResponse(res)
            else:
                user = User.object.create_user(email=email, first_name=first_name, last_name=last_name,
                                               password=password)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                message = render_to_string('activate.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                    'token': account_activation_token.make_token(user),
                })
                mail_subject = 'Activate your account...'
                to_email = email
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                send_email.send()
                res['message'] = "registered Successfully...Please activate your Account"
                res['success'] = True
                return JsonResponse(res)
        else:
            return JsonResponse(res)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))  # UserId for a decoding
        user = User.object.get(pk=uid)
        if user is not None and account_activation_token.check_token(user, token):  # if its a valid token
            user.is_active = True  # User is Active
            user.save()
            return render(request, 'user_login.html')
        else:
            return HttpResponse('Activation link is invalid!')
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None



@api_view(['POST'])
@require_POST
def logins(request):
    res = {}
    res['message'] = 'Something bad happend'
    res['success'] = False

    print('**********************************loginsssss***************************')
    try:
        email = request.POST.get('email')  # Get Email
        password = request.POST.get('password')  # Get Password
        if email is None:
            raise Exception("Email is required")
        if password is None:
            raise Exception("Password is required")
        user = authenticate(email=email, password=password)
        print("User Name", user)
        if user:  # If it is a User
            if user.is_active:  # If a User is active
                login(request, user)  # Login maintains a request and a user
                try:
                    payload = {
                        # 'id': User.id,
                        'email': email,
                        'password': password,
                    }
                    token_encode = jwt.encode(payload, "secret_key", algorithm='HS256').decode('utf-8')
                    res['message'] = "Login Sucessfull"
                    res['success'] = True
                    res['data'] = token_encode

                    redis_information.set_token(self, 'token', res['data'])
                    return render(request, 'profile.html')  # After Sucessfull returns to the profile page
                except Exception as e:  # Invalid
                    result = {'error1': 'please provide an valid email and a password'}
                    return JsonResponse(result)
            else:
                res['message'] = "User is Inactive"
                return JsonResponse(res)
        else:
            res['message'] = 'Username or Password is not correct'  # Invalid login details
            messages.error(request, 'Invalid login details')
            return JsonResponse(res)
    except Exception as e:
        print(e)

def exit(request):  # For a Logout
    # logout(request)
    return render(request, "home.html")


class Login(APIView):
    def post(self, request):
        res = {}
        res['message'] = 'Something bad happend'
        res['success'] = False

        print('**********************************API Login***************************')
        try:
            email = request.POST.get('email')  # Get Email
            password = request.POST.get('password')  # Get Password
            if email is None:
                raise Exception("Email is required")
            if password is None:
                raise Exception("Password is required")
            user = authenticate(email=email, password=password)
            print("User Name", user)
            if user:  # If it is a User
                if user.is_active:  # If a User is active
                    try:  # The claims in a JWT are encoded as a JSON object that is digitally signed using
                        # JSON Web Signature (JWS) and/or encrypted using JSON Web Encryption (JWE)
                        payload = {
                            # 'id': User.id,
                            'email': email,
                            'password': password,
                        }
                        token_encode = jwt.encode(payload, "secret_key", algorithm='HS256').decode('utf-8')
                        res['message'] = "Login Sucessfull"
                        res['success'] = True
                        res['data'] = token_encode

                        redis_information.set_token(self, 'token', res['data'])
                        return JsonResponse(res, status=status.HTTP_201_CREATED)
                    except Exception as e:  # Invalid
                        result = {'error1': 'please provide an valid email and a password'}
                        return JsonResponse(result, safe=False)
                else:
                    res['message'] = "User is Inactive"
                    return JsonResponse(res, safe=False)
            else:
                res['message'] = 'Username or Password is not correct'  # Invalid login details
                messages.error(request, 'Invalid login details')
                return JsonResponse(res)
        except Exception as e:
            print(e)

def upload_profilenew(request):
    res={}
    token = redis_information.get_token(self, 'token')  # Redis Cache GET
    token_decode = jwt.decode(token, "secret_key", algorithms=['HS256'])
    eid = token_decode.get('email')  # Additional code of a decorator to get an email
    user = User.object.get(email=eid)
    # user = User.object.get(id=user_id.id)
    # user=user_id.id
    print ('user-----------', user)
    try:
        file = request.FILES['pic']  # Uploading a Pic
        tag_file = request.POST.get('email')
        print('keysysy',tag_file)
        valid_image = imghdr.what(file)
        print("vi", valid_image)
        if str(user)==tag_file:
            if valid_image:
                upload_image(file, tag_file, valid_image)
                user.image = str(file)
                print("Fileeeeeee", valid_image)
                print("Imagee", user.image)
                user.save()
                print('saved')
                print("Image Extension", valid_image)
                res['message'] = "Sucessfully Uploaded the Image"
                res['Sucess'] = True
                return JsonResponse(res, status=200)
            else:
                res['message'] = "Invalid Image"
                res['Sucess'] = False
                return JsonResponse(res, status=404)
        else:
            res['message'] = "Invalid"
            res['Sucess'] = False
            return JsonResponse(res, status=404)
    except Exception as e:
        print(e)
        return HttpResponse(e)

def delete_profile(request):
    """This method is used to delete any object from s3 bucket """
    token = redis_information.get_token(self, 'token')  # Redis Cache GET
    token_decode = jwt.decode(token, "secret_key", algorithms=['HS256'])
    eid = token_decode.get('email')  # Additional code of a decorator to get an email of a user
    user = User.object.get(email=eid)
    # user = User.object.get(id=user_id.id)
    print('user-----------', user)
    tag_file = request.POST.get('email')
    res={}
    try:
        print('keys_to_delete', tag_file)
        print("Usr******",type(user))
        print("TF----",type(tag_file))
        print('Users',user)
        if str(user)==tag_file:
            delete_from_s3(tag_file)
            user.image=" "
            user.save()
            print("Delete It")
            res['message'] = "Succesfully Deleted"
            res['Sucess'] = True
            return JsonResponse(res, status=200)
        else:
            res['message'] = "Not Deleted"
            res['Sucess'] = False
            return JsonResponse(res, status=404)
    except Exception as e:
        return HttpResponse('Invalid')


def showarchive(request):  # Archive Show
    res = {}
    notes = CreateNotes.objects.all().order_by('-created_time')  # Sort the Notes according to the time
    try:
        if notes:
            return render(request, 'notes/index1.html', {'notes': notes})
    except notes.DoesNotExist:
        res['message'] = "No Notes in Archive"
        # res['success']=False
    except Exception as e:
        print(e)
        return HttpResponse(res, status=404)

def trash(request):
    res = {}
    notes = CreateNotes.objects.all().order_by('-created_time')
    try:
        if notes is not None:
            return render(request, 'notes/trash.html', {'notes': notes})
        else:
            return HttpResponse("Trash is Empty")
    except Exception as e:
        res['message'] = "No Notes in Trash"
        # res['success']=False
        print(e)
        return HttpResponse(res, status=404)

def showpinned(request):
    res = {}
    notes = CreateNotes.objects.all().order_by('-created_time')
    try:
        if notes:
            return render(request, 'notes/pinned.html', {'notes': notes})
    except Exception as e:
        res['message'] = "No Pinned Notes"
        # res['success'] = False
        print(e)
        return HttpResponse(res, status=404)

def showlabels(request):
    res = {}
    labels = Labels.objects.all().order_by('-created_time')
    try:
        if labels:
            return render(request, 'notes/showlabels.html', {'labels': labels})
    except Exception as e:
        res['message'] = "No Labels Notes"
        print(e)
        return HttpResponse(res, status=404)


def table(request):  # Display the contents of the tables using a Jinga Template
    notes = CreateNotes.objects.all().order_by('-created_time')  # Sort the Notes according to the time
    return render(request, 'notes/index.html', {'notes': notes})


