from django.shortcuts import render
import json
from users import models
from users import views
from users.models import User,CreateNotes,Labels,MapLabel
from rest_framework.generics import CreateAPIView  # Used for a create-only endpoints, provides a post method handler
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from rest_framework.views import APIView  # Taking the views of REST framework Request & Response
from rest_framework.decorators import api_view
from django.conf import settings
from rest_framework import generics  # For a List API use a generics
from users.custom_decorators import custom_login_required
# from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.http import JsonResponse


class create(APIView):
    @method_decorator(custom_login_required)  # Get a decorator
    def post(self,request):
        print("*********")
        """
                 This module is create a Label of a specific user
        """
        a_user = request.user_id.id
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
                print("Savvvvvv")
                res['message'] = 'Unssucess'
                res['success'] = False  # in response return data in json format
                return JsonResponse(res, status=400)
        except Exception as e:
            res['message'] = 'Unssucess'
            res['success'] = False  # in response return data in json format
            return JsonResponse(res, status=404)

class delete(APIView):
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

class update(APIView):
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


class add(APIView):
    """
        This module is to add a label to a particular note of a specific user
     """
    @method_decorator(custom_login_required) # Get a decorator
    def post(self, request):    # request a particular note of a specific user
        auth_user = request.user_id.id # get a requested if from a token
        res = {}
        res['message'] = 'Something bad happened' # raise a exception when some unhandled exception occurs
        res['success'] = False
        try:
            pk=request.POST.get('pk',None)
            if pk is None: # if note pk
                raise Exception('Id is required')
            else:
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
        except CreateNotes.DoesNotExist: # Handles Exception when notes are not present
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)
        except Exception as e:
            print(e)
            return JsonResponse(res, status=404)

class deletelabel(APIView):
    """
        This module is to add a label to a particular note of a specific user
    """
    @method_decorator(custom_login_required) # Get a decorator
    def delete(self, request):  # request a particular note of a specific user
        auth_user = request.user_id.id # get a id of from a header token
        res = {}
        res['message'] = 'Something bad happened'  # raise a exception when unhandled occurs
        res['success'] = False
        try:
            pk=request.POST.get('pk', None)
            if pk is None: # if  requested pk
                raise Exception('Id is required')
            else:
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

class getLabelOnNotes(APIView):
    """
               This module is to get a label to a particular note
       """
    # @method_decorator(custom_login_required)
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