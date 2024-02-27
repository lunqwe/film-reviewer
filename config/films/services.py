import requests
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from .models import Director, Actor, Movie
from .services import *

class DatabasePlaceholder():
    def __init__(self, titles_to_search) -> None:
        self.titles_to_search = titles_to_search

    def open_url(self, url: str):
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f'Error opening url: {url}.')
            return None
        
    def get_movie_details(self, name: str):
        url = f'http://www.omdbapi.com/?t={name}&apikey=c2d42119'
        url_data = self.open_url(url)
        if url_data and "Error" not in url_data:
            return url_data
        else:
            print(f"Error receiving data from API for movie: {name}.")
            return None

    def search_movies(self, name_for_search: str):
        name_for_search = name_for_search.replace(' ', "+")
        url = f'http://www.omdbapi.com/?s={name_for_search}&apikey=c2d42119'
        url_data = self.open_url(url)
        if url_data and "Search" in url_data:
            names_list = [data["Title"] for data in url_data["Search"]]
            print(names_list)
            return names_list
        else:
            print(f"Error receiving data for {name_for_search}.")
            return None

    def run_placeholder(self):
    # Проходимся по каждому заголовку, который нужно найти
        for title in self.titles_to_search:
            found_movies = self.search_movies(title)
            if found_movies:
                # Проходимся по каждому найденному фильму
                for movie_title in found_movies:
                    movie_details = self.get_movie_details(movie_title)
                    if movie_details:
                        try:
                            # Извлекаем нужные данные из деталей фильма
                            title = movie_details['Title']
                            year = movie_details['Year']
                            
                            # Создаем список актеров фильма, обрабатывая каждое имя актера
                            actors = [Actor.objects.get_or_create(name=actor)[0] for actor in movie_details["Actors"].split(', ')]
                            
                            # Получаем или создаем режиссера фильма
                            director, _ = Director.objects.get_or_create(name=movie_details['Director'])
                            
                            # Создаем объект фильма и сохраняем его в базе данных
                            movie = Movie.objects.create(director=director, title=title, year_released=year)
                            # Устанавливаем отношения между фильмом и актерами
                            movie.actors.set(actors)
                        except Exception as e:
                            print(f'Error while saving data to database.\nDetails: {e}')
                            


