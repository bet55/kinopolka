from django.urls import path

from postcard.views import PostCardViewSet, InvitationViewSet

urlpatterns = [
    path("", PostCardViewSet.as_view(), name="postcard_views"),
    path("invitation/", InvitationViewSet.as_view(), name="postcard_views"),
]
