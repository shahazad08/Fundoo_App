from rest_framework.validators import UniqueValidator
from .models import User, CreateNotes,Labels
from rest_framework import serializers  # Serializers allow complex data such as query sets and model instances to be
# from rest_framework.pagination import PaginationSerializer
from django.core.paginator import Paginator
from rest_framework import pagination
# converted to native Python data types that can then be easily rendered into JSON, XML or other content types
# ModelSerializer: It is a class which provides a useful shortcut for creating serializers
# that deal with model instances and query sets.

class UserSerializer(serializers.ModelSerializer):  # Created the User Serializer for all the fields in a model
    date_joined = serializers.ReadOnlyField()  # date joined should be in a read_only modes
    password = serializers.CharField(style={'input_type': 'password'})  # password should be properly validated
    # email = serializers.EmailField(validators=[UniqueValidator(queryset=User.object.all())])
    email = serializers.RegexField(regex=r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$",
                                   required=True)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)

    class Meta:  # We have  use of Meta class is simply to provide metadata to the ModelForm class.
        model = User  # Shows that the User fields contain the model class
        fields = ('id', 'email', 'first_name', 'last_name', 'date_joined', 'password')

class LoginSerializer(serializers.ModelSerializer):  # Created the user serializer for a Login
    password = serializers.CharField(style={'input_type': 'password'})
    email = serializers.RegexField(regex=r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$",
                                   required=True)
    class Meta:
        model = User  # Contains the fields of email and a password
        fields = ['email', 'password']

class NoteSerializer(serializers.ModelSerializer):
    title= serializers.RegexField(regex=r"^[a-zA-Z0-9.' ']+$",required=True) # Title can be a indicates number,name,spaces
    color=serializers.RegexField(regex=r"^[-\w\s]+[-\w\s]+(?:,[-\w\s]*)*$",required=True)

    class Meta:
        model = CreateNotes
        # fields = '__all__'
        fields = ('title', 'description', 'color','label','collaborate','user','remainder')

class ReadNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateNotes
        fields = '__all__'

class PageNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateNotes
        fields = ('title', 'description')

class LabelSerializer(serializers.ModelSerializer):

    label_name= serializers.RegexField(regex=r"^[a-zA-Z0-9.' ']+$",required=True) # Title can be a indicates number,name,spaces
    class Meta:
        model = Labels
        fields = '__all__'
