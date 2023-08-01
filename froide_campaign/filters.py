import operator
from functools import reduce

from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db import models

from rest_framework import filters
from rest_framework.compat import distinct

from .models import InformationObject


class StatusFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.GET.get("status"):
            status = request.GET.get("status")
            if status == "normal":
                return queryset.filter(foirequests__isnull=True)
            if status == "pending":
                return queryset.filter(foirequests__isnull=False).exclude(
                    foirequests__status="resolved"
                )
            if status == "successful":
                successful = ["successful", "partially_successful"]
                return queryset.filter(
                    foirequests__status="resolved",
                    foirequests__resolution__in=successful,
                )
            if status == "refused":
                return queryset.filter(
                    foirequests__status="resolved", foirequests__resolution="refused"
                )
        return queryset


class CategoryFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.GET.get("category"):
            category = request.GET.get("category")
            try:
                return queryset.filter(categories__id=category)
            except ValueError:
                pass
        return queryset


class FeaturedFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.GET.get("featured"):
            try:
                featured = bool(int(request.GET.get("featured")))
                return queryset.filter(featured=featured)
            except ValueError:
                pass
        return queryset


class InformationObjectRequestedFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.GET.get("requested") is not None:
            try:
                is_requested = bool(request.GET["requested"])
                queryset = queryset.filter(foirequests__isnull=not is_requested)
            except ValueError:
                pass
        return queryset


class InformationObjectSearchVectorFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        q = request.GET.get("q")
        if q:
            return InformationObject.objects.search(queryset, q)
        return queryset


class CustomSearchFilter(filters.SearchFilter):
    search_param = "q"

    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.query_params.get(self.search_param, "")
        params = params.replace("\x00", "")  # strip null characters
        params = params.replace(",", " ")
        params = params.replace("-", " ")
        return params.split()

    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        return InformationObject.objects.search(queryset, " ".join(search_terms))

    def _orm_filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = [
            self.construct_search(str(search_field)) for search_field in search_fields
        ]

        base = queryset
        language = request.GET.get("language", settings.LANGUAGE_CODE)
        conditions = []
        for search_term in search_terms:
            queries = [
                models.Q(**{orm_lookup: search_term}) for orm_lookup in orm_lookups
            ]
            conditions.append(reduce(operator.or_, queries))

        queryset = queryset.filter(
            models.Q(translations__language_code=language)
            & reduce(operator.or_, conditions)
        )

        if self.must_call_distinct(queryset, search_fields):
            queryset = distinct(queryset, base)
        return queryset


class RandomOrderFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.GET.get("order"):
            order = request.GET.get("order")
            if order == "random":
                return queryset.order_by("?")

        return queryset


def get_lat_lng(request):
    try:
        lat = float(request.GET.get("lat"))
    except (ValueError, TypeError):
        raise ValueError
    try:
        lng = float(request.GET.get("lng"))
    except (ValueError, TypeError):
        raise ValueError
    return lat, lng


class GeoDistanceFilter(filters.BaseFilterBackend):
    DEFAULT_RADIUS = 1000
    ORDER_ZOOM_LEVEL = 8

    def filter_queryset(self, request, queryset, view):
        # TODO: geocode
        # location / coordinates
        # if location is not None:
        #     location_search = True
        #     point, formatted_address = geocode(location, address=False)

        coordinates = self.get_coordinates(request)
        if coordinates is None:
            return queryset

        radius = self.DEFAULT_RADIUS
        try:
            radius = int(request.GET.get("radius"))
        except (ValueError, TypeError):
            return queryset

        queryset = self.filter_geo(
            queryset,
            coordinates=coordinates,
            radius=radius,
        )
        queryset = self.order_by_distance(request, queryset, coordinates=coordinates)
        return queryset

    def get_coordinates(self, request):
        try:
            lat, lng = get_lat_lng(request)
            return Point(lng, lat, srid=4326)
        except ValueError:
            return

    def order_by_distance(self, request, queryset, coordinates=None):
        if coordinates is None:
            coordinates = self.get_coordinates(request)
            if coordinates is None:
                return queryset
        zoom = None
        try:
            zoom = int(request.GET.get("zoom"))
        except (ValueError, TypeError):
            return queryset

        has_q = bool(request.GET.get("q"))
        order_distance = zoom is None or zoom >= self.ORDER_ZOOM_LEVEL
        if not has_q and order_distance:
            queryset = queryset.annotate(
                distance=Distance("geo", coordinates)
            ).order_by("distance")
        return queryset

    def filter_geo(self, qs, coordinates=None, radius=None, **kwargs):
        if coordinates is None:
            return qs

        if radius is None:
            radius = self.DEFAULT_RADIUS
        radius = int(radius * 0.9)

        qs = (
            qs.filter(geo__isnull=False)
            .filter(geo__dwithin=(coordinates, radius))
            .filter(geo__distance_lte=(coordinates, D(m=radius)))
        )

        return qs
