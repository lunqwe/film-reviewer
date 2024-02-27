from django.http import HttpResponse
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import serializers, status
from django.views.decorators.csrf import csrf_exempt
from common.services import get_response, error_detail
from .models import Movie, Director, Actor
from .paginators import ManageDataPagination
from .filters import MovieFilter
from .services import DatabasePlaceholder
from .serializers import DatabasePlaceholderSerializer, ManageDataSerializer, GetDataSerializer, DeleteDataSerializer



def index(request):
    return render(request, 'index.html')

def catalog(request):
    return render(request, 'catalog.html')


class DatabasePlaceholderView(generics.CreateAPIView):
    serializer_class = DatabasePlaceholderSerializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        try: 
            serializer.is_valid(raise_exception=True)
            placeholder = DatabasePlaceholder(request.data['titles_to_search'])
            placeholder.run_placeholder()

            return get_response("success", "Database placeholded successfully!", status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return error_detail(e)
        

class GetDataView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = GetDataSerializer
    pagination_class = ManageDataPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = MovieFilter

class CreateMovieView(generics.CreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = ManageDataSerializer

class UpdateMovieView(generics.RetrieveUpdateAPIView):
    queryset = Movie.objects.all()
    serializer_class = ManageDataSerializer


class DeleteMovieView(generics.DestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = ManageDataSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        print(instance)
        return get_response('success', 'Movie deleted successfully!', status=status.HTTP_200_OK) # кастомная функция возврата респонса

# class DeleteMovieView(generics.CreateAPIView):
#     serializer_class = ManageDataSerializer

#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         try: 
#             serializer.is_valid(raise_exception=True)
#             item_to_delete = Movie.objects.get(id=request.data['id']).delete()

#         except serializers.ValidationError as e:
#             return error_detail(e)


""" 
Так же, можно использовать этот вариант

class DeleteMovieView(generics.DestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = ManageDataSerializer
    
"""


