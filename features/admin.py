from django.contrib import admin

from features.models import Photo


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "uploaded_at"]
