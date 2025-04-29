from django.urls import path

from postcard.views import PostCardViewSet

urlpatterns = [
    path("", PostCardViewSet.as_view(), name="postcard_views")
]
