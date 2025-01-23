import asyncio

from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.views import APIView

from classes import KP_Movie, MovieHandler, Note, Tools
from classes.app_user import AppUserHandler
from lists.models import Film, Director, Genre, Actor, Writer, FilmGenreRelations, Sticker, AppUser
from lists.serializers import FilmSerializer, FilmSmallSerializer, GenreSerializer, UserSerializer, StickerSerializer


class MoviesView(APIView):
    def get(self, request, kp_id=''):
        if kp_id:
            return Response(MovieHandler.get_movie(kp_id=kp_id))

        response_format = request.query_params.get('format')
        is_archive = 'archive' in request.path

        if response_format == 'json':
            return Response(MovieHandler.get_all_movies(is_archive=is_archive))

        return render(
            request,
            'movies.html',
            context={
                'movies': MovieHandler.get_all_movies(all_info=False, is_archive=is_archive),
                'users': AppUserHandler.get_all_users(),
                'is_archive': is_archive,
                'random': Tools.get_random_images(),
            }
        )

    def patch(self, request):
        kp_id = request.data['kp_id']
        is_archive = request.data['is_archive']

        success = MovieHandler.change_movie_status(kp_id, is_archive)

        return Response(
            data={
                'success': str(success),
                'error': '',
                'id': kp_id,
            }
        )

    def delete(self, request):
        kp_id = request.data.get('kp_id')

        if not kp_id:
            return Response(
                data={
                    'success': False,
                    'error': 'Lost kp_id',
                    'id': False,
                }
            )

        movie_is_deleted = MovieHandler.remove_movie(kp_id)

        return Response(
            data={
                'success': str(movie_is_deleted),
                'error': '',
                'id': kp_id,
            }
        )


class MovieRatingView(APIView):
    def delete(self, request):
        success = Note.remove_note(request.data['user'], request.data['film'])

        return Response(
            data={
                'success': bool(success),
                'error': str(success),
            }
        )

    def post(self, request):
        success = Note.create_note(request.data)

        return Response(
            data={
                'success': success,
                'error': '',
            }
        )

    def put(self, request):
        self.post(request)


class MovieAdditionView(APIView):
    def get(self, request):
        return render(
            request,
            'add_movie.html',
            context={
                'random': Tools.get_random_images(),
                'users': AppUserHandler.get_all_users(),
            }
        )

    def post(self, request):
        kp_id = ''.join(char for char in list(request.data.get('kp_id', '')) if char.isdigit())

        movie_id, success = MovieHandler.download(kp_id)

        return Response(
            data={
                'success': success,
                'error': '',
                'id': movie_id,
            }
        )


@api_view(['GET'])
def view_movies(request):
    response_format = request.query_params.get('format')
    is_archive = 'archive' in request.path

    mv = MovieHandler()

    if response_format == 'json':
        movies = mv.get_all_movies(is_archive=is_archive)
        return Response(movies)

    users = AppUser.objects.all()
    us_sr = UserSerializer(users, many=True)

    movies = mv.get_all_movies(all_info=False, is_archive=is_archive)

    random_images = Tools.get_random_images()

    return render(request, 'movies.html',
                  context={'movies': movies,
                           'users': us_sr.data,
                           'is_archive': is_archive,
                           'random': random_images})


@api_view(['GET'])
def view_movie_by_id(request, kp_id):
    mv = MovieHandler()
    movie = mv.get_movie(kp_id=kp_id)

    return Response(movie)


# todo error handler view
@api_view(['GET', 'POST'])
def add_movie(request):
    if request.method == 'GET':
        users = AppUser.objects.all()
        us_sr = UserSerializer(users, many=True)

        random_images = Tools.get_random_images()
        return render(request, 'add_movie.html', context={'random': random_images, 'users': us_sr.data, })

    kp_id = ''.join(char for char in list(request.data.get('kp_id', '')) if char.isdigit())

    mv = MovieHandler()
    movie_id, success = mv.download(kp_id)

    return Response(data={'success': success, 'error': '', 'id': movie_id})


@api_view(['PATCH'])
def change_archive_status(request):
    kp_id = request.data['kp_id']
    is_archive = request.data['is_archive']

    movie = MovieHandler()
    movie_is_changed = movie.change_movie_status(kp_id, is_archive)

    return Response(data={'success': str(movie_is_changed), 'error': '', 'id': kp_id})


@api_view(['DELETE'])
def remove_movie(request):
    kp_id = request.data.get('kp_id')

    if not kp_id:
        return Response(data={'success': False, 'error': 'Lost kp_id', 'id': False})

    movie = MovieHandler()
    movie_is_deleted = movie.remove_movie(kp_id)

    return Response(data={'success': str(movie_is_deleted), 'error': '', 'id': kp_id})


@api_view(['POST', 'PUT', 'DELETE'])
def rate_movie(request):
    if request.method == 'DELETE':
        user = request.dat['user']
        film = request.data['film']

        res = Note.remove_note(user, film)

        return Response(data={'success': bool(res), 'error': str(res)})

    note_created = Note.create_note(request.data)

    return Response(data={'success': note_created, 'error': ''})
