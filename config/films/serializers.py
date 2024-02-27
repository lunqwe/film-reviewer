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
        fields = ['name']

class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['name']

class GetDataSerializer(serializers.ModelSerializer):
    director = DirectorSerializer()
    actors = ActorSerializer(many=True)

    class Meta:
        model = Movie
        fields = ['id', 'title', 'year_released', 'director', 'actors']

class ManageDataSerializer(serializers.ModelSerializer):
    director = DirectorSerializer()
    actors = ActorSerializer(many=True)

    class Meta:
        model = Movie
        fields = ['id', 'title', 'year_released', 'director', 'actors']

    def create(self, validated_data):
        director_data = validated_data.pop('director')
        director, _ = Director.objects.get_or_create(**director_data)
        print(director)
        actors_data = validated_data.pop('actors')
        actors = [Actor.objects.get_or_create(**actor_data)[0] for actor_data in actors_data]
        print(actors)
        movie = Movie.objects.create(director=director, **validated_data)
        movie.actors.set(actors)
        return movie
    
    def update(self, movie, validated_data):
        director_data = validated_data.pop('director')
        director, _ = Director.objects.get_or_create(**director_data)
        print(director)
        actors_data = validated_data.pop('actors')
        actors = [Actor.objects.get_or_create(**actor_data)[0] for actor_data in actors_data]
        print(actors)
        movie.director = director
        movie.title = validated_data.get('title')
        movie.year = validated_data.get('year')
        movie.actors.set(actors)
        return movie


    
class DeleteDataSerializer(serializers.Serializer):
    obj_id = serializers.IntegerField()



    