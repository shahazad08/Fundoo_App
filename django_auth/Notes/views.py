from users import models
from users import views
from users.models import User,CreateNotes,Labels,MapLabel
import json
from rest_framework.filters import OrderingFilter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.core.paginator import Paginator
from rest_framework.generics import CreateAPIView  # Used for a create-only endpoints, provides a post method handler
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from rest_framework.views import APIView  # Taking the views of REST framework Request & Response
from .serializers import PageNoteSerializer
from rest_framework.decorators import api_view
from django.conf import settings
from rest_framework import generics  # For a List API use a generics
from .paginate import PostLimitOffsetPagination, PostPageNumberPagination  # Creating our own no. of records in a Pages
from rest_framework.filters import SearchFilter  # it allows users to filter down a queryset based on a model's
from users.custom_decorators import custom_login_required
from django.utils.decorators import method_decorator


class create(APIView):
    @method_decorator(custom_login_required)  # Decorator is called with respective to token user
    def post(self, request):

        '''
            description: This API deletes/uninstalls a device.
parameters:
  - name: title
    type: string
    required: true
    location: form
  - name: description
    type: string
    required: true
    location: form
  - name: color
    type: string
    required: true
    location: form
"""
...

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

class get(APIView):
    '''
            This Moudule is to Read a notes of a specific user
        '''

    @method_decorator(custom_login_required)  # Decorator is called through a token
    def get(self, request):
        res = {}
        a_user = request.user_id.id  # get the id though a token
        print("Users",a_user)
        try:
            print("----------")
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


class delete(APIView):
    '''
       This module is to delete a note of a specific user
       '''

    @method_decorator(custom_login_required)
    def delete(self, request):
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

class restore(APIView):
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


class update(APIView):

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
                description = request.POST.get('description')
                color = request.POST.get('color')
                remainder = request.POST.get('remainder')
                notes.title = title  # Assign the updated fields to a requsted note
                notes.description = description
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

class archive(APIView):  # Delete a Note
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


class isarchive(APIView):  # Delete a Note
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



class color(APIView):  # Delete a Note
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


class pinned(APIView):
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


class ispinned(APIView):
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


class copy(APIView):
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


class collaborator(APIView):
    """
        This module is to create a collaborator to a particular note of a specific user
    """
    @method_decorator(custom_login_required)
    def post(self, request):  # get the require pk
        a_user = request.user_id.id

        
        res = {}
        res['message'] = 'Something bad happend'
        res['success'] = False
        try:
            id = request.POST.get('id', None) # get the id of a specific note
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
    def delete(self, request):
        auth_user = request.user_id.id # get the requested id
        res = {}
        res['message'] = 'Something bad happend' # raise the exception if bad happens
        res['success'] = False
        try:
            id = request.POST.get('id', None)   # get the requested id of a specific note
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
