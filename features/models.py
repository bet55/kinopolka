import os

from django.db import models


class Photo(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, default="", verbose_name="Описание")
    image = models.ImageField(upload_to="media/photos/", verbose_name="Изображение")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return self.name

    def delete(self, *args, **kwargs) -> None:
        # Убираем файл из media вместе с записью
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super().delete(*args, **kwargs)
