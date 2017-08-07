# encoding=UTF-8
from django import forms
from haystack.forms import SearchForm,ModelSearchForm


class advanceSearch(ModelSearchForm):
    detailedName = forms.CharField(required=False,label=(u'名称'))


    def search(self):
        # First we need to store SearchQuerySet recieved after / from any other processing that's going on
        sqs = super(advanceSearch, self).search()

        if not self.is_valid():
            return self.no_query_found()

        # check to see if any date filters used, if so apply filter
        if self.cleaned_data['detailedName']:
            sqs = sqs.filter(detailedName=self.cleaned_data['detailedName'])
        # gt / gte / lt / lte——对应于 >, >=, <, <=
        return sqs
