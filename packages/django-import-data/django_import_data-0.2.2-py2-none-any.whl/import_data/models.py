from __future__ import unicode_literals

from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey('Author', null=True)
    categories = models.ManyToManyField('Category')
    
class Category(models.Model):
    title = models.CharField(max_length=255)
    
class Author(models.Model):
    title = models.CharField(max_length=255)
