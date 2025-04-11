from django.urls import path

from postcard.views import PostCardViewSet, tmp

urlpatterns = [
    path("", PostCardViewSet.as_view(), name="postcard_views"),
    path("check/", tmp, name="postcard_views"),
]
