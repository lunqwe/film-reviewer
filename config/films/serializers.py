from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from .models import Movie, Director, Actor


class DatabasePlaceholderSerializer(serializers.Serializer):
    titles_to_search = serializers.JSONField(default=list)

    def validate(self, validated_data):
        if 'titles_to_search' in validated_data.keys():
            return True
        else:
            raise serializers.ValidationError("titles_to_search required")

class DirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = ["id", 'name']

class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ["id", 'name']

class GetDataSerializer(serializers.ModelSerializer):
    director = DirectorSerializer()
    actors = ActorSerializer(many=True)

    class Meta:
        model = Movie
        fields = ['id', 'title', 'year_released', 'director', 'actors']

class ManageDataSerializer(serializers.ModelSerializer):
    director = serializers.PrimaryKeyRelatedField(queryset=Director.objects.all())
    actors = serializers.PrimaryKeyRelatedField(many=True, queryset=Actor.objects.all())

    class Meta:
        model = Movie
        fields = ['id', 'title', 'year_released', 'director', 'actors']
    
class DeleteDataSerializer(serializers.Serializer):
    obj_id = serializers.IntegerField()



    