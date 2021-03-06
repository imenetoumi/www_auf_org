# -*- coding: utf-8 -*-
import datetime

from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from django import forms

from haystack.forms import SearchForm
from haystack.query import SearchQuerySet


from aldryn_common.paginator import DiggPaginator

from .conf import settings


class AldrynFacetedSearchForm(SearchForm):
    selected_facets = forms.CharField(required=False, widget=forms.HiddenInput)
    courant = forms.BooleanField(required=False, widget=forms.HiddenInput)
    cloture = forms.BooleanField(required=False, widget=forms.HiddenInput)

    def search(self):
        sqs = SearchQuerySet()
        sqs = sqs.facet('bureaux').facet(
            'section').facet('annee').facet('partenaire')

        if self.q:
            sqs = sqs.filter(content=sqs.query.clean(self.q))

        if self.courant:
            sqs = sqs.filter(date_fin__gte=datetime.date.today())
        if self.cloture:
            sqs = sqs.filter(date_fin__lt=datetime.date.today())

        self.selected_facets = list(
            set(self.selected_facets.split('&') + self.selected_facets_get))

        for facet in self.selected_facets:
            if "__" not in facet:
                continue

            field, value = facet.split("__", 1)

            if value:
                sqs = sqs.narrow(u'%s:"%s"' % (field, sqs.query.clean(value)))

        return sqs


class AldrynSearchView(FormMixin, ListView):
    form_class = AldrynFacetedSearchForm

    paginate_by = settings.ALDRYN_SEARCH_PAGINATION
    paginator_class = DiggPaginator

    template_name = 'aldryn_search/search_results.html'

    def get(self, request, *args, **kwargs):
        self.form = AldrynFacetedSearchForm(self.request.GET)
        self.form.q = self.request.GET.get('q', '')
        self.form.courant = self.request.GET.get('courant', '')
        self.form.cloture = self.request.GET.get('cloture', '')
        self.form.selected_facets = self.request.GET.get('selected_facets', '')
        self.form.selected_facets_get = self.request.GET.getlist(
            'selected_facets', [])
        return super(AldrynSearchView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = self.form.search()
        if not self.request.user.is_authenticated():
            self.queryset = self.queryset.exclude(login_required=True)
        self.facet_counts = self.queryset.facet_counts()
        return self.queryset.order_by('-date_pub')

    def get_context_data(self, **kwargs):
        context = super(AldrynSearchView, self).get_context_data(**kwargs)

        context['form'] = self.form
        context['facets'] = self.facet_counts
        context['selected_facets'] = self.request.GET.getlist(
            'selected_facets', [])
        if self.object_list.query.backend.include_spelling:
            context['suggestion'] = self.form.get_suggestion()
        return context
