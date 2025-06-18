from django.urls import path

from lists.views import Movies, MovieRating, MovieAdding

urlpatterns = [
    path("", Movies.as_view(), name="view_movies"),
    path("archive/", Movies.as_view(), name="view_archive_movies"),
    path("<int:kp_id>/", Movies.as_view(), name="view_movie_by_id"),
    path("add/", MovieAdding.as_view(), name="add_movie"),
    path("remove/", Movies.as_view(), name="remove_movie"),
    path("change_archive/", Movies.as_view(), name="change_archive_status"),
    path("rate/", MovieRating.as_view(), name="rate_movie"),
]
