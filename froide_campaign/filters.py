import operator
from functools import reduce

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from rest_framework import filters


class StatusFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if request.GET.get('status'):
            status = request.GET.get('status')
            if status == 'normal':
                return queryset.filter(foirequests__isnull=True)
            if status == 'pending':
                return queryset.filter(foirequests__isnull=False).exclude(
                    foirequests__status='resolved')
            if status == 'successful':
                successful = ['successful', 'partially_successful']
                return queryset.filter(foirequests__status='resolved',
                                       foirequests__resolution__in=successful)
            if status == 'refused':
                return queryset.filter(foirequests__status='resolved',
                                       foirequests__resolution='refused')
        return queryset


class TagFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if request.GET.get('tag'):
            tag = request.GET.get('tag')
            return queryset.filter(tags__contains=tag)
        return queryset


class CategoryFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if request.GET.get('category'):
            category = request.GET.get('category')
            return queryset.filter(categories__id=category)
        return queryset


class FeaturedFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if request.GET.get('featured'):
            featured = request.GET.get('featured')
            try:
                return queryset.filter(featured=featured)
            except ValidationError:
                pass
        return queryset


class CustomSearchFilter(filters.SearchFilter):

    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.query_params.get(self.search_param, '')
        params = params.replace('\x00', '')  # strip null characters
        params = params.replace(',', ' ')
        params = params.replace('-', ' ')
        return params.split()

    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = [
            self.construct_search(str(search_field))
            for search_field in search_fields
        ]

        base = queryset
        language = request.GET.get('language', settings.LANGUAGE_CODE)
        conditions = []
        for search_term in search_terms:
            queries = [
                models.Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups
            ]
            conditions.append(reduce(operator.or_, queries))

        queryset = queryset.filter(
            models.Q(translations__language_code=language) & reduce(operator.or_, conditions))

        if self.must_call_distinct(queryset, search_fields):
            queryset = distinct(queryset, base)
        return queryset