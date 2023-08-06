# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

import inflection
from rest_framework import filters


class FilterOptionsMixin(object):

    view_options_defaults = {}

    @property
    def view_options_property(self):
        return "{}_options".format(inflection.underscore(self.__class__.__name__))

    def get_options(self, view):
        if not hasattr(self, '_options'):
            self._options = {}
            self._options.update(self.view_options_defaults)
            self._options.update(getattr(view, self.view_options_property, {}))
        return self._options

    def get_option(self, view, option, default=None):
        return self.get_options(view).get(option, default)


class MixedFilterBackend(filters.BaseFilterBackend):
    """
    Composed filters that add criteria based on whether a request is internal or external, from a user or a client

    Every access to a resource goes through this process:

            - if internal client: filter_internal_queryset
            - if external client: filter_external_queryset
            - if acting as user (App access): check user_permissions_set
            - if acting as client (API access): filter_client_queryset
                - if internal client: filter_internal_client_queryset
                - if external client: filter_external_client_queryset

    It's important to note that:

        * No filtering is done by default
        * Any of the methods can be overridden to provide specific behaviour

    """
    def filter_queryset(self, request, queryset, view):
        if hasattr(request, 'client') and request.client.is_internal:
            queryset = self.filter_internal_queryset(request, queryset, view)
        else:
            queryset = self.filter_external_queryset(request, queryset, view)

        if request.user.is_authenticated():
            return self.filter_user_queryset(request, queryset, view)
        else:
            return self.filter_client_queryset(request, queryset, view)

    def filter_internal_queryset(self, request, queryset, view):
        return queryset

    def filter_external_queryset(self, request, queryset, view):
        return queryset

    def filter_user_queryset(self, request, queryset, view):
        return queryset

    def filter_client_queryset(self, request, queryset, view):
        if request.client.is_internal:
            return self.filter_internal_client_queryset(request, queryset, view)
        else:
            return self.filter_external_client_queryset(request, queryset, view)

    def filter_internal_client_queryset(self, request, queryset, view):
        return queryset

    def filter_external_client_queryset(self, request, queryset, view):
        return queryset
