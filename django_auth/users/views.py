import json
import jwt
from django.views.decorators.http import require_POST
from rest_framework.filters import OrderingFilter
from django.shortcuts import render
from django.template import loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
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
from rest_framework import serializers, status
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
from .models import User, CreateNotes, Labels, MapLabel
from django.conf import settings
from rest_framework import generics  # For a List API use a generics
from .paginate import PostLimitOffsetPagination, PostPageNumberPagination  # Creating our own no. of records in a Pages
from rest_framework.filters import SearchFilter  # it allows users to filter down a queryset based on a model's
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



# /***********************************************************************************************
def exit(request):  # For a Logout
    # logout(request)
    return render(request, "home.html")


class createnotes(APIView):
    # '''
    #     This Moudule is to create a note of a specific users
    # '''
    # @api_view(['POST'])
    # @require_POST
    # @require_http_methods(["POST"])
    @method_decorator(custom_login_required)  # Decorator is called with respective to token user
    def post(self, request):

        '''
             parameters:
               title: title,
               # description: description,
               # color: color,
               # required: true
               # type: string
               # paramType: form
               # paramType: form
               # required: true
               # type: string
               # :param request:
               # :return:


               in: path
               name: id
               type: integer
               required: true
               description: The user ID.


           '''
        res = {}
        if request.method == 'POST':
            auth_user = request.user_id.id  # get the id of a specific user through token
            try:
                title = request.POST.get('title')  # get the title
                description = request.POST.get('description')  # get the description
                color = request.POST.get('color')  # get the color
                label = request.POST.get('label')  # get the label
                remainder = request.POST.get('remainder')  # get the raminder
                notes = CreateNotes(title=title, description=description, color=color, label=label, user_id=auth_user,                                remainder=remainder)  # assigned in the notes
                if title != "" and description != "":  # if not null
                    notes.save()  # add in a db
                    res['message'] = 'Notes are added in a database'
                    res['success'] = True
                    res['data'] = notes.id
                    return JsonResponse(res, status=200)
                else:  # else Unsuccess
                    res['message'] = 'Unssucesss'
                    res['success'] = False
                    return JsonResponse(res, status=404)
            except Exception as e:
                res['message'] = 'Something bad happend'
                return JsonResponse(res, status=404)
        else:
            res['success'] = False
            res['message'] = 'Request unhandled'
            return JsonResponse(res, status=404)


class getnote(APIView):
    '''
            This Moudule is to Read a notes of a specific user
        '''

    @method_decorator(custom_login_required)  # Decorator is called through a token
    def post(self, request):
        res = {}
        a_user = request.user_id.id  # get the id though a token
        print("Users",a_user)
        try:
            read_notes = CreateNotes.objects.filter(user=a_user).values()  # display the notes of a particular user
            print("****", read_notes)
            values = CreateNotes.collaborate.through.objects.filter(
                user_id=a_user).values()  # display the users which are collaborated with the users
            print("Values", values)
            collab = []  # blank collaborator array
            for i in values:  # assigned the values in i which are collaborated with the  particular user
                collab.append(i['createnotes_id'])  # append with respect to the note id
            collab_notes = CreateNotes.objects.filter(id__in=collab).values().order_by(
                '-created_time')  # id__in indicates to take all the values
            # print("collab Notes -------------", collab_notes)
            merged = read_notes | collab_notes  # as to merging the 2 query sets into one
            print("***", merged)
            l = []  # Converting the query sets to a json format
            for i in merged:
                l.append(i)

            token = redis_information.get_token(self, 'token')  # Redis Cache GET
            print('Token from a redis cache------------------', token)
            return JsonResponse(l, safe=False)
        except Exception as e:  # Excaption is Handled
            res['message'] = "User Not Exist"
            res['sucess'] = False
            return JsonResponse(res, status=404)


class deletenote(APIView):
    """
    This module is to delete a note of a specific user
    """
    @method_decorator(custom_login_required)  # Get the decorator of a specific user
    def delete(self, request):
        auth_user = request.user_id.id
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            id = request.POST.get('id', None)  # Request the id to be deleted, user can also kept it None
            if id is None:  # If id is None
                raise Exception('Id is required')  # Raise the Exception
            else:
                note = CreateNotes.objects.get(pk=id,
                                               user=auth_user)  # get requested id from a Note, and a particular user
                if note.trash:  # If note.trash is True
                    res['data'] = note.id
                    res['message'] = 'Notes is in Trash'  # Means Note is in a Trash
                    res['success'] = True
                    return JsonResponse(res, status=status.HTTP_201_CREATED)  # Display the data
                else:  # if trash is false, change to true
                    note.trash = True
                    note.save()  # save in a db
                    res['data'] = note.id
                    res['message'] = 'Note has been moved to trash'
                    res['success'] = True
                    return JsonResponse(res, status=status.HTTP_201_CREATED)  # Display the data
        except Exception as e:
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'  # Exception is handled
            res['success'] = False
            return JsonResponse(res, status=404)


class delete_from_trash(APIView):
    '''
       This module is to delete a note of a specific user
       '''

    @method_decorator(custom_login_required)
    def post(self, request):
        auth_user = request.user_id.id
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            id = request.POST.get('id', None)  # Get the id form a user
            if id is None:  # if id is None
                raise Exception('Id is required')  # Raise the
            else:
                note = CreateNotes.objects.get(pk=id, user=auth_user)  # get requested id from a Note
                if note.trash:  # if is_deleted is true
                    note.delete()  # delete it
                    res['message'] = 'Note has been deleted from trash'
                    res['success'] = True
                    return JsonResponse(res, status=status.HTTP_201_CREATED)
                else:
                    raise Exception()
        except Exception as e:
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            res['success'] = False
            return JsonResponse(res, status=404)


class restorenote(APIView):
    """
          This module is to restore a note of a specific user
          """
    @method_decorator(custom_login_required)
    def post(self, request):
        auth_user = request.user_id.id
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            id = request.POST.get('id', None)  # Get a Note if from a User
            if id is None:  # If Id is None
                raise Exception('Id is required')
            else:
                note = CreateNotes.objects.get(pk=id, user=auth_user)  # Get a requested Note
                if note.trash:  # If note.trash is true, change it to false
                    note.trash = False
                    note.save()  # save in a db
                    res['message'] = "Selected Note has been Restored"
                    res['success'] = True
                    res['data'] = note.id
                    return JsonResponse(res, status=204)
                else:
                    raise Exception()
        except Exception as e:  # Handle the Excaption
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)


 # Get a decorator

class updatenote(APIView):

    @method_decorator(custom_login_required)
    def put(self,request):
        auth_user = request.user_id.id  # Get a user
        print('User', auth_user)
        # auth_user=authorize(request)
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            id = request.POST.get('id', None)  # Accept a Id to be accepted
            if id is None:  # If id is None
                raise Exception('Id is required')  # Raise the exception
            else:
                notes = CreateNotes.objects.get(pk=id, user=auth_user)  # Update the particular note from a user
                title = request.POST.get('title')  # Updates the tile or any user fields
                des = request.POST.get('description')
                color = request.POST.get('color')
                remainder = request.POST.get('remainder')
                notes.title = title  # Assign the updated fields to a requsted note
                notes.description = des
                notes.color = color
                notes.remainder = remainder
                notes.save()  # save in a db
                res['message'] = "Update Successfully"
                res['success'] = True
                return JsonResponse(res, status=204)
        except Exception as e:  # Handle the exception
            print(e)
            res['message'] = 'Note doesnt exists'
            res['sucess'] = 'False'
            return JsonResponse(res, status=404)




class archivenote(APIView):  # Delete a Note
    """
    This module is to archive a note of a specific user
    """

    @method_decorator(custom_login_required)  # Get a decorator
    def post(self, request):
        auth_user = request.user_id.id  # Request for a specific user
        res = {}
        # If any fault Exception, shows the message
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            id = request.POST.get('id', None)
            if id is None:
                raise Exception('id is required')
            else:
                note = CreateNotes.objects.get(pk=id, user=auth_user)  # get particular note from a id
                if note.is_archived==False:  # if archived is false, change it to true, as to move in a archived
                    note.is_archived = True
                    note.save()  # save in a db
                    res['message'] = "Selected Note has been moved to Archive"
                    res['success'] = True
                    res['data'] = note.id
                    return JsonResponse(res, status=200)  # return result
                else:
                    raise Exception()

        except Exception as e:  # catch the exception as if the note exists
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)


class notarchivenote(APIView):  # Delete a Note
    """
    This module is to archive a note of a specific user
    """

    @method_decorator(custom_login_required)  # Get a decorator
    def post(self, request):

        auth_user = request.user_id.id  # Request for a specific user
        print('User',auth_user)
        res = {}
        # If any fault Exception, shows the message
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            """
                         :param request:
                         :return:
                         """
            id = request.POST.get('id', None)
            if id is None:
                raise Exception('id is required')
            else:
                note = CreateNotes.objects.get(pk=id, user=auth_user)  # get particular note from a id
                if note.is_archived:  # if archived is false, change it to true, as to move in a archived
                    note.is_archived = False
                    note.save()  # save in a db
                    res['message'] = "Selected Note has been moved to Dashboard"
                    res['success'] = True
                    res['data'] = note.id
                    return JsonResponse(res, status=200)  # return result
                else:
                    raise Exception()

        except Exception as e:  # catch the exception as if the note exists
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)


class colornote(APIView):  # Delete a Note
    """
     This module is set a color to a note of a specific user
    """

    @method_decorator(custom_login_required)  # Get a decorator
    def post(self, request):
        auth_user = request.user_id.id # Get a specific user
        res = {}
        res['message'] = 'Something bad happened'  # If any fault Exception, shows the message
        res['success'] = False
        try:
            id = request.POST.get('id', None)  # set a id of a note
            if id is None:  # if id is None
                raise Exception('Id is required')  # raise a exception
            else:
                note = CreateNotes.objects.get(pk=id, user=auth_user)  # get a selected note from a user
                note.color = request.POST.get('color')  # request the color from notes model, for change
                lenth=len(note.color)
                if lenth<=6:
                    note.save()  # save to db
                    res['message'] = "Color has been Changed."  # message for change color
                    res['success'] = True
                    res['data'] = note.id
                    return JsonResponse(res, status=204)  # return result
                else:
                    res['message'] = "Color should not be more than 5 letters."  # message for change color
                    res['success'] = False
                    res['data'] = note.id
                    return JsonResponse(res, status=204)  # return result

        except Exception as e:
            res['message'] = 'Note doesnt exists'  # Handles Exception message if note doesnot exists
            return JsonResponse(res, status=404)


class ispinned(APIView):
    """
     This module is set a pinned to a note of a specific user
    """

    @method_decorator(custom_login_required)  # Get a decorator
    def post(self, request):
        auth_user = request.user_id.id # get a specific user
        res = {}
        res['message'] = 'Something bad happened'  # If any fault Exception, shows the message
        res['success'] = False
        try:
            id = request.POST.get('id', None)  # get a id of a user
            if id is None:  # If id is None
                raise Exception('Id is required')  # Raise a Exception
            else:
                note = CreateNotes.objects.get(pk=id, user=auth_user)  # get a requested pk
                if note.is_pinned == False:  # if not pinned
                    note.is_pinned = True  # change it to pin
                    note.save()  # save in a db
                    res['message'] = "Notes has been Pinned to Top."  # message in a SMD format
                    res['success'] = True
                    res['data'] = note.id
                    return JsonResponse(res, status=200)
                else:
                    raise Exception()
        except Exception as e:  # catch exception if note doesnt exists
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)


class unpinned(APIView):
    """
     This module is set a pinned to a note of a specific user
    """

    @method_decorator(custom_login_required)  # Get a decorator
    def post(self, request):
        auth_user = request.user_id.id  # get a specific user
        res = {}
        res['message'] = 'Something bad happened'  # If any fault Exception, shows the message
        res['success'] = False
        try:
            id = request.POST.get('id', None)  # get a id of a user
            if id is None:  # If id is None
                raise Exception('Id is required')  # Raise a Exception
            else:
                note = CreateNotes.objects.get(pk=id, user=auth_user)  # get a requested pk
                if note.is_pinned:  # if not pinned
                    note.is_pinned = False  # change it to pin
                    note.save()  # save in a db
                    res['message'] = "Notes has been Move to Unpinned" # message in a SMD format
                    res['success'] = True
                    res['data'] = note.id
                    return JsonResponse(res, status=200)
                else:
                    raise Exception()
        except Exception as e:  # catch exception if note doesnt exists
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)

class copynote(APIView):
    """
        This module is set a copy of a note of a specific user
    """
    @method_decorator(custom_login_required)  # Get a decorator
    def post(self, request):
        auth_user = request.user_id.id  # get note with given id
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            id = request.POST.get('id', None)  # Get a note id of a specific user
            if id is None:  # If id is None
                raise Exception('Id is required')  # Raise a exception if id not present
            else:
                note = CreateNotes.objects.get(pk=id, user=auth_user)  # Accept a note pk
                note.id = None  # create pk as a none
                note.save()  # save in a db
                res['message'] = "Note is Coped "  # Note is copied
                res['success'] = True
                res['data'] = note.id
                return JsonResponse(res, status=204)
        except Exception as e:
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)


class create_label(APIView):
    @method_decorator(custom_login_required)  # Get a decorator
    def post(self,request):
        """
                 This module is create a Label of a specific user
        """
        a_user = request.user_id.id
        res = {}
        res['message'] = 'Something bad happend'
        res['success'] = True
        try:
            label_name = request.POST.get('label_name', None)
            labels = Labels(label_name=label_name, user_id=a_user)
            if label_name != "":
                labels.save()
                res['data'] = labels.id
                res['message'] = 'Labels are added in a database'
                res['success'] = True
                return JsonResponse(res, status=200)
            else:
                res['message'] = 'Unssucess'
                res['success'] = False  # in response return data in json format
                return JsonResponse(res, status=400)
        except Exception as e:
            res['message'] = 'Unssucess'
            res['success'] = False  # in response return data in json format
            return JsonResponse(res, status=404)


class deletelabel(APIView):
    @method_decorator(custom_login_required)  # Get a decorator
    def delete(self,request):  # Delete a Note
        """
                  This module is delete a Label of a specific user
          """
        a_user = request.user_id.id
        print('User', a_user)
        res = {}
        print('test user', request.user_id)
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            id=request.POST.get('id',None)
            if id is None:  # if label pk
                raise Exception('Id is required')
            else:
                label = Labels.objects.get(id=id, user=a_user)  # get requested id from a Labels
                res['data'] = label.id  # Display the id that is to be delete
                label.delete()  # delete the label
                res['message'] = "Label has been deleted"
                res['success'] = True
                return JsonResponse(res, status=200)  # Display the data
        except Exception as e:
            res['message'] = 'Label doesnt exists'  # Handle the exception when label not exists
            return JsonResponse(res, status=404)


class updatelabel(APIView):
    """
        This module is update a Label of a specific user
       """
    @method_decorator(custom_login_required)
    def put(self, request):
        auth_user = request.user_id.id
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            id = request.POST.get('id', None)
            if id is None:
                raise Exception('Id is required')
            else:
                labels = Labels.objects.get(pk=id, user_id=auth_user)
                print("label", labels)
                label_name = request.POST.get('label_name')
                labels.label_name = label_name
                print('Titles', labels.label_name)
                res['message'] = "Update Successfully"
                res['success'] = True
                labels.save()
                return JsonResponse(res, status=204)
        except Exception as e:
            print(e)
            res['message'] = 'Label doesnt exists'
            return JsonResponse(res, status=404)


class addLabelOnNote(APIView):
    """
        This module is to add a label to a particular note of a specific user
     """
    @method_decorator(custom_login_required) # Get a decorator
    def post(self, request, pk):    # request a particular note of a specific user
        auth_user = request.user_id.id # get a requested if from a token
        res = {}
        res['message'] = 'Something bad happened' # raise a exception when some unhandled exception occurs
        res['success'] = False
        try:
            if pk: # if note pk
                note = CreateNotes.objects.get(pk=pk, user=auth_user)  # reterieve the pk of a particular note
                # according to a specific user
                id = request.POST.get('id')  # retrieve the id of a particular label
                label = Labels.objects.get(id=id, user_id=auth_user) # get a label of a particular user id
                maplabel = MapLabel.objects.filter(note_id=note, label_id=label)  # filter the note and label
                if len(maplabel) == 0:  # if maplabel field is empty
                    obj = MapLabel(note_id=note, label_id=label)  # assigned the notes and a label using model by
                    # creating the oject
                    obj.save()  # save the object
                    res['data'] = note.id  # message of passing data in a SMD format
                    res['message'] = 'Labels are added to a particular note'
                    res['success'] = True
                    return JsonResponse(res, status=status.HTTP_201_CREATED)
                else:
                    res['message'] = ' Labels Allready added'  # Something wrong
                    res['success'] = False
                    return JsonResponse(res, status=status.HTTP_201_CREATED)
            else:
                res['message'] = ' Note Doesnt Exists'  # Something wrong
                res['success'] = False
                return JsonResponse(res, status=status.HTTP_404_CREATED)
        except CreateNotes.DoesNotExist: # Handles Exception when notes are not present
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)
        except Exception as e:
            print(e)
            return JsonResponse(res, status=404)


class getLabelOnNotes(APIView):
    """
           This module is to get a label to a particular note
       """
    @method_decorator(custom_login_required)
    def post(self, request):
        auth_user = request.user.id
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            label_id = request.POST.get('label_id')
            label = MapLabel.objects.filter(label_id=label_id).values() # Filter down a queryset based on a model's=
            print("Labelss", label)
            l = []  # Converting the query sets to a json format
            for i in label:
                l.append(i)
            return JsonResponse(l, safe=False)
        except Exception as e:
            print(e)

class removeLabelonNote(APIView):
    """
        This module is to add a label to a particular note of a specific user
    """
    @method_decorator(custom_login_required) # Get a decorator
    def post(self, request, pk):  # request a particular note of a specific user
        auth_user = request.user_id.id # get a id of from a header token
        res = {}
        res['message'] = 'Something bad happened'  # raise a exception when unhandled occurs
        res['success'] = False
        try:
            if pk: # if  requested pk
                note = CreateNotes.objects.get(pk=pk, user=auth_user)  # retrieve the pk of a particular note
                id = request.POST.get('id')  # retrieve the id of a particular label
                label = Labels.objects.get(id=id, user_id=auth_user) # retrieve the label of a particular user
                maplabel = MapLabel.objects.filter(note_id=note, label_id=label)  # filter the note and label
                maplabel.delete() # delete a requested note
                res['message'] = 'Labels are remove to a requested note'
                res['success'] = True
                return JsonResponse(res, status=status.HTTP_201_CREATED)
        except CreateNotes.DoesNotExist: # Handled the exception
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)
        except Exception as e:
            print(e)
            return JsonResponse(res, status=404)


class remainder(APIView): # get the remainder

    @method_decorator(custom_login_required)
    def get(self,request):
        auth_user = request.user_id.id
        res = {}
        remainder_fields = CreateNotes.objects.filter(remainder__isnull=False, user=auth_user).values()  # check the remainder field
        # is not null
        try:
            if remainder_fields: # if remainder
                remainder = []
                for i in remainder_fields: # convert the  query set to a Json format
                    remainder.append(i)
                return JsonResponse(remainder, safe=False)
            else: # No remainder
                res['message'] = "No remainder set"
                res['success'] = 'False'
                return JsonResponse(res, safe=False)
        except Exception as e:
            res['message'] = " Note Doesnt Exists"
            res['success'] = 'False'
            return JsonResponse(res, safe=False)



class createcollaborator(APIView):
    """
        This module is to create a collaborator to a particular note of a specific user
    """
    @method_decorator(custom_login_required)
    def post(self, request):  # get the require pk
        a_user = request.user_id.id
        print("User",a_user)
        print(a_user)
        res = {}
        res['message'] = 'Something bad happend'
        res['success'] = False
        try:
            id = request.POST.get('id', None) # get the id of a specific user
            if id is None:  # if id is None
                raise Exception('id required')   # raise the exception
            else: # if not same delete it
                note = CreateNotes.objects.get(pk=id, user=a_user)  # get the required id of a note
                note_user = note.user.id  # Get the Note User ID
                note_id = note.id
                collaborate = request.POST.get('collaborate')  # Accept a id of a new user
                user = User.object.get(id=collaborate)  # get the details of a user through id
                values = CreateNotes.collaborate.through.objects.filter(user_id=a_user).values()  # display the users which are collaborated with the users
            if note_user == user.id:  # If note user_id and collaborate user is same
                res['message'] = 'Cannot Collaborate to the same User'
                res['success'] = False
                return JsonResponse(res, status=404)
            elif CreateNotes.collaborate.through.objects.filter(user_id=user.id,
                                                                createnotes_id=note.id):  # Checking of a same user id and create note id for as if its exist user or not
                res['message'] = 'User Allready Exists'
                res['success'] = False
                return JsonResponse(res, status=404)
            else:
                print("user", user.id)
                note.collaborate.add(user)  # adds the user to the note
                note.save()  # save the note
                res['message'] = 'Success'
                res['success'] = True
                res['data'] = note.id
                return JsonResponse(res, status=200)
        except Exception as e:
            res['message'] = 'Note doesnt exists'
            print(e)
            return JsonResponse(res, status=404)

class deletecollaborator(APIView):
    """
        This module is to delete a collaborator to a particular note of a specific user
     """
    @method_decorator(custom_login_required) # get the decorator from a token
    def post(self, request):
        auth_user = request.user_id.id # get the requested id
        res = {}
        res['message'] = 'Something bad happend' # raise the exception if bad happens
        res['success'] = False
        try:
            id = request.POST.get('id', None)   # get the requested id of a specific user
            if id is None:  # if id is none
                raise Exception('id is required')
            else:
                note = CreateNotes.objects.get(pk=id, user=auth_user) # note id with a specific user
                auth_user = note.user.id  # Use vairable b as a Note User
                collaborate = request.POST.get('collaborate')  # Accept a id of a new user
                print(collaborate)
                user = User.object.get(id=collaborate)  # get the details of a users from a User table
                if auth_user == user.id: # check for a collaborator when id is same
                    res['message'] = 'Cannot Collaborate to the same User'
                    res['success'] = False
                    return JsonResponse(res, status=404) # return status
                else:   # if not same delete it
                    res['message'] = 'Deleted'  # message in a SMD format
                    res['success'] = True
                    res['data'] = note.id
                    note.collaborate.remove(user)  # remove the user
                    note.save() # save in db
                    return JsonResponse(res, status=200)
        except Exception as e:  # if user not exists
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)

# ***************************************************************************************************

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
        # res['success'] = False
        print(e)
        return HttpResponse(res, status=404)


def table(request):  # Display the contents of the tables using a Jinga Template
    notes = CreateNotes.objects.all().order_by('-created_time')  # Sort the Notes according to the time
    return render(request, 'notes/index.html', {'notes': notes})


class PostListAPIView(generics.ListAPIView):  # Viweing the ListAPI Views that
    serializer_class = PageNoteSerializer  # Assigning a Notes serializers fields in a Serializer class
    filter_backends = [SearchFilter, OrderingFilter]
    # search_fields=['title','description']
    pagination_class = PostPageNumberPagination  # Create our own limit of records in a pages

    def get_queryset(self, *args, **kwargs):  # Method for a itrerating of pages
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            query_list = CreateNotes.objects.filter().order_by(
                '-created_time')  # Filter down a queryset based on a model's
            # fields, displaying the form to let them do this.
            return query_list
        except Exception as e:
            res['message'] = 'Empty'
            res['success'] = False
            return JsonResponse(res, status=404)

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
    print("IDDDDDDDD",user)
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

# class dummy_site(APIView):
#     title=POST.get('title')
#     def post(self,request,title):
#         res={}
#         res['message']="Swagger API"
#         return JsonResponse(res,status=200)




