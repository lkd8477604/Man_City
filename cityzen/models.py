from django.db import models
from mongoengine import *
# Create your models here.
class n_163(Document):
    title = StringField(max_length=100)
    url = StringField(max_length=64)
    pub_date = StringField(max_length=32)
    meta={
        'collection': '163'
    }
class sina(Document):
    title = StringField(max_length=100)
    url = StringField(max_length=64)
    pub_date = StringField(max_length=32)
    meta={'collection':'sina'}

class qq(Document):
    title = StringField(max_length=100)
    url = StringField(max_length=64)
    pub_date = StringField(max_length=32)
    meta={'collection':'qq'}