# from rest_framework.validators import UniqueValidator
from users import models
from users.models import User, CreateNotes
from rest_framework import serializers  # Serializers allow complex data such as query sets and model instances to be
# from rest_framework.pagination import PaginationSerializer
from django.core.paginator import Paginator
from rest_framework import pagination


class PageNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateNotes
        fields = ('title', 'description')









