from django.db import models
from fav.models import Favorite
from django.contrib.contenttypes.fields import GenericRelation


class Article(models.Model):
    title = models.CharField(max_length=256)
    description = models.CharField(max_length=256)
    favorites = GenericRelation(Favorite)
