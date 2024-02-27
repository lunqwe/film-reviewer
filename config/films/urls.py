from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name='home-page'),
    path('catalog/', views.catalog, name="catalog"),
    path('db_placeholder/', views.DatabasePlaceholderView.as_view(), name='db_placeholder'),
    path('get-films/', views.GetDataView.as_view(), name='get-data'),
    path('create/', views.CreateMovieView.as_view(), name='create'),
    path('update/<int:pk>', views.UpdateMovieView.as_view(), name='update'),
    path('delete/<int:pk>', views.DeleteMovieView.as_view(), name='delete')
]
