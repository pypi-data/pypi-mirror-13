# -*- coding: utf-8 -*-
#
#  DuedilApiClient v3 Pro
#  @copyright 2014 Christian Ledermann
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
#

from __future__ import unicode_literals

import sys
import six
from collections import Mapping
from abc import ABCMeta

from ..api import LiteClient, ProClient  # , InternationalClient


class Resource(Mapping):
    attribute_names = None
    locale = 'uk'
    id = None
    path = None
    client_class = LiteClient
    loaded = False

    def __init__(self, id, api_key=None, locale='uk', load=False, client=None, **kwargs):
        if not self.attribute_names:
            raise NotImplementedError(
                "Resources must include a list of allowed attributes")

        self.id = id
        assert(locale in ['uk', 'roi'])
        self.locale = locale
        if client:
            self.client = client
        else:
            self.client = self.client_class(api_key, sandbox=kwargs.pop('sandbox', False))

        if load:
            self.load()

        if kwargs:
            self._set_attributes(**kwargs)

    def _set_attributes(self, missing=False, **kwargs):
        for k, v in kwargs.items():
            if k in self.attribute_names:
                self.__setattr__(k, v)

        if missing is True:
            for allowed in self.attribute_names:
                if allowed not in kwargs:
                    self.__setattr__(allowed, None)

    def load(self):
        self._result = self.client.get(self.endpoint)
        self.loaded = True
        self._set_attributes(**self._result)

    def __getattr__(self, name):
        """
        lazily return attributes, only contact duedil if necessary
        """
        try:
            return super(Resource, self).__getattribute__(name)
        except AttributeError:
            if name in self.attribute_names:
                if not self.loaded:
                    self.load()
                return super(Resource, self).__getattribute__(name)
            else:
                raise

    @property
    def endpoint(self):
        if not self.path:
            raise ValueError(
                "{model} does not have a path to load specified".format(
                    model=self.__class__.__name__))
        endpoint = '{locale}/{path}'.format(locale=self.locale,
                                            path=self.path)
        if self.id:
            endpoint += '/{id}'.format(id=self.id)
        return endpoint

    def __len__(self):
        return len(self.attribute_names)

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __iter__(self):
        for prop in self.attribute_names + ['id']:
            if hasattr(self, prop):
                yield prop
            else:
                setattr(self, prop, None)
                yield prop

    def __contains__(self, key):
        if key in self._results.keys():
            return True
        if key in self._results.values():
            return True
        return False

    def __missing__(self, key):
        raise KeyError('%s in not a valid attribute' % key)

    def __str__(self):
        return '{} ({})'.format(self.__class__.__name__, self.id)

    def __eq__(self, other):
        return self.id == other.id


class ProResource(Resource):
    client_class = ProClient
    full_endpoint = False

    def load(self):
        """
        get results from duedil
        """
        self._result = self.client.get(self.endpoint)
        self.loaded = True
        self._set_attributes(**self._result['response'])


# Here be metaclass dragons that don't make complete sense as to why we have them


def resource_property(endpoint):
    def wrap(getter_fn):
        def inner(self, *args, **kwargs):
            return getter_fn(self, endpoint, *args, **kwargs)
        return inner
    return wrap


class SearchableResourceMeta(type):
    term_filters = None
    range_filters = None
    search_path = None

    def search(klass, order_by=None, limit=None, offset=None, **kwargs):
        data = klass.client._build_search_string(klass.term_filters,
                                                 klass.range_filters,
                                                 order_by=order_by, limit=limit,
                                                 offset=offset, **kwargs)
        results_raw = klass.client.get(klass.search_path, data=data)
        results = []
        for r in results_raw['response']['data']:
            results.append(
                klass(**r)
            )
        return results


class RelatedResourceMeta(ABCMeta):

    def __init__(klass, _name, _bases, ns):
        related_resources = ns.get('related_resources') or {}
        for ep in related_resources.keys():

            @resource_property(ep)
            def getter(self, endpoint):
                resource = self.related_resources[endpoint]

                if isinstance(resource, six.string_types):
                    module, resource = resource.rsplit('.', 1)
                    resource = getattr(sys.modules['duedil.resources.%s' % module], resource)

                return self.load_related(endpoint, resource, self.full_endpoint)

            attr_name = ep.replace('-', '_')
            setattr(klass, attr_name,
                    property(getter, None, None, attr_name))


class SearchableRelatedResourceMeta(SearchableResourceMeta, RelatedResourceMeta):
    pass


class RelatedResourceMixin(six.with_metaclass(RelatedResourceMeta, object)):
    related_resources = None

    def _get(self, resource, full_endpoint=False):
        if not full_endpoint:
            uri = '{endpoint}/{resource}'.format(endpoint=self.endpoint,
                                                 resource=resource)
        else:
            uri = self.endpoint
        return self.client.get(uri)

# need to deal with pagination...
    def load_related(self, key, klass=None, full_endpoint=False):
        internal_key = '_' + key.replace('-', '_')

        related = getattr(self, internal_key, None)

        if related is None:
            result = self._get(key, full_endpoint)
            if result:
                response = result['response']
                related = None
                if 'data' in response and isinstance(response['data'], (list, tuple)):
                    related = []
                    for r in result['response']['data']:
                        r['locale'] = r.get('locale', self.locale)
                        related.append(
                            klass(client=self.client, id=r.pop('id'), **r) if klass else None
                        )
                elif result:
                    locale = response.get('locale')
                    # HACK: for locale switching when traversing companies...
                    # XXX: this will need to be revisited!!!
                    if locale is None and 'company_url' in response:
                        path_components = response['company_url'][len(self.client.base_url):].split('/')
                        if 'uk' in path_components:
                            locale = 'uk'
                        elif 'roi' in path_components:
                            locale = 'roi'
                        else:
                            locale = 'uk'
                    else:
                        locale = self.locale
                    response['locale'] = locale
                    if klass:
                        related = klass(client=self.client, id=response.pop('id'), **response)
                setattr(self, internal_key, related)
        return related

    def __len__(self):
        return len(self.attribute_names + self.related_resources.keys())
