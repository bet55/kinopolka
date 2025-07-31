from django.urls import path

from postcard.views import InvitationViewSet, PostcardsArchiveViewSet, PostcardViewSet

urlpatterns = [
    path("", PostcardViewSet.as_view(), name="postcard_views"),
    path("invitation/", InvitationViewSet.as_view(), name="postcard_views"),
    path("archive/", PostcardsArchiveViewSet.as_view(), name="postcards_archive_views"),
]
