# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from django.apps import apps

from django.utils import six
from django.utils.translation import ugettext_lazy as _

from rest_framework.serializers import Serializer, ListSerializer, ModelField


class SourceSerializer(Serializer):

    def to_representation(self, instance):
        return instance['_source']


class RoutedDocTypeMixin(object):

    def get_routing_key(self):
        return self.context.get("routing_key", None)


class DocTypeSerializer(RoutedDocTypeMixin, Serializer):

    def to_representation(self, instance):
        data = super(DocTypeSerializer, self).to_representation(instance)
        data.update(instance.to_dict())
        return data


class DocTypeListSerializer(ListSerializer):

    def to_representation(self, instance):
        return instance.to_dict()


class AggregationsSerializer(Serializer):

    pass


class TermsAggregationField(Serializer):

    def to_representation(self, instance):
        return [{"name": d['key'], "count": d['doc_count']} for d in instance['buckets']]


class DateHistogramAggregationField(Serializer):

    def to_bucket_representation(self, bucket):
        return {"date": bucket['key_as_string'], "count": bucket['doc_count']}

    def to_representation(self, instance):
        return (self.to_bucket_representation(bucket) for bucket in instance['buckets'])


class GeoHashAggregationField(Serializer):

    def to_representation(self, instance):
        return (self.to_bucket_representation(bucket) for bucket in instance['buckets'])


class StatsAggregationField(Serializer):

    def to_representation(self, instance):
        return instance.to_dict()


class GeoBoundsAggregationField(Serializer):

    def to_representation(self, instance):
        bounds = getattr(instance, 'bounds', None)
        if bounds:
            return [bounds['top_left']['lon'], bounds['top_left']['lat']] + [bounds['bottom_right']['lon'], bounds['bottom_right']['lat']]
        return None
