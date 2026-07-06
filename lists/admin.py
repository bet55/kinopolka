from django.contrib import admin
from django.utils.html import format_html

from lists.models import Actor, Director, Genre, Movie, Note, User, Writer
from mixins import GlobalDataMixin


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "first_name", "avatar_preview", "avatar"]
    list_editable = ["avatar"]  # путь можно менять прямо в списке
    # Без password/date_joined/прав: у участников клуба пароль пустой,
    # и форма с обязательным паролем не давала бы сохранить аватарку
    fields = ["username", "first_name", "last_name", "email", "avatar"]

    @admin.display(description="Превью")
    def avatar_preview(self, user):
        return format_html(
            '<img src="{}" style="height: 2em; width: 2em; object-fit: cover; border-radius: 50%;">',
            user.avatar,
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Пользователи кэшируются для всех страниц (GlobalDataMixin) —
        # сбрасываем, чтобы правка аватарки была видна сразу, а не через 15 минут
        GlobalDataMixin.cache.delete_cache(GlobalDataMixin.CACHE_USERS_KEY)


admin.site.register(Actor)
admin.site.register(Director)
admin.site.register(Writer)
admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(Note)
