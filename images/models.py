from django.conf import settings
from django.db import models, connection

from practice_2.settings import LOCAL


def get_upload_to(instance, filename):
    return f'images/{connection.schema_name}/{filename}'


class Image(models.Model):
    image = models.ImageField(upload_to=get_upload_to, null=False, blank=False)

    class Meta:
        db_table = "images"

    def __str__(self):
        return self.image.name

    @property
    def url(self):
        if LOCAL:
            return f'http://{connection.schema_name}.{settings.BASE_HOST}{self.image.url}'
        else:
            return f'https://{connection.schema_name}.{settings.BASE_HOST}/api{self.image.url}'
