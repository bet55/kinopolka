from django.urls import path

from lists.views import MovieAddingViewSet, MovieRatingViewSet, MoviesViewSet


urlpatterns = [
    path("", MoviesViewSet.as_view(), name="view_movies"),
    path("archive/", MoviesViewSet.as_view(), name="view_archive_movies"),
    path("<int:kp_id>/", MoviesViewSet.as_view(), name="view_movie_by_id"),
    path("add/", MovieAddingViewSet.as_view(), name="add_movie"),
    path("remove/", MoviesViewSet.as_view(), name="remove_movie"),
    path("change_archive/", MoviesViewSet.as_view(), name="change_archive_status"),
    path("rate/", MovieRatingViewSet.as_view(), name="rate_movie"),
]
