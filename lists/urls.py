from django.urls import path

from lists.views import view_movies, add_movie, view_movie_by_id, remove_movie, \
    change_archive_status, rate_movie, MoviesView, MovieRatingView, MovieAdditionView

urlpatterns = [

    path('', MoviesView.as_view(), name='view_movies'),
    path('archive', MoviesView.as_view(), name='view_movies'),
    path('<int:kp_id>', MoviesView.as_view(), name='view_movie_by_id'),

    path('add', MovieAdditionView.as_view(), name='add_movie'),
    path('remove', MoviesView.as_view(), name='remove_movie'),
    path('change_archive', MoviesView.as_view(), name='change_archive_status'),

    path('rate', MovieRatingView.as_view(), name='rate_movie'),

]
