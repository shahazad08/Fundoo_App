from .models import Notes
from rest_framework import serializers

class CreateNoteSerializer(serializers.ModelSerializer):
    class Meta(object):
        models=Notes
        fields=('title', 'description', 'is_pinned', 'color','remainder')



class ReadNoteSerializer(serializers.ModelSerializer):
    class Meta(object):
        models=Notes
        fields = ('title', 'description', 'is_pinned', 'color', 'remainder')



class UpdateNoteSerializer(serializers.ModelSerializer):
    class Meta(object):
        models=Notes
        fields=('id', 'title', 'description', 'is_pinned', 'color', 'remainder')

class DeleteNoteSerializer(serializers.ModelSerializer):
    class Meta(object):
        models=Notes
        fields=('title','description','is_pinned','color','remainder')












