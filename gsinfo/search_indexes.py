# encoding=UTF-8
from haystack import indexes
from models import *


class gsDingIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    #detailedName = indexes.CharField(model_attr='detailedName')
    def get_model(self):
        return gsDing

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

class gsBiZhangIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return gsBiZhang

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

class gsYinYuanIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return gsYinYuan

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

class gsGongYiPinIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return gsGongYiPin

    def index_queryset(self, using=None):
        return self.get_model().objects.all()