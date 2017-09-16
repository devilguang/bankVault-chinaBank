# encoding=UTF-8
from haystack import indexes
from models import *


# class gsDingIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True, use_template=True)
#     #detailedName = indexes.CharField(model_attr='detailedName')
#     def get_model(self):
#         return gsDing
#
#     def index_queryset(self, using=None):
#         return self.get_model().objects.all()
