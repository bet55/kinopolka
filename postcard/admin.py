from django.contrib import admin

from postcard.models import Postcard


@admin.register(Postcard)
class PostcardAdmin(admin.ModelAdmin):
    list_display = ["title", "meeting_date", "is_active", "created_at"]
    list_editable = ["is_active"]
    filter_horizontal = ["movies"]
