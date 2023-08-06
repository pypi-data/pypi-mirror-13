# -*- coding: utf-8 -*-
#
#  DuedilApiClient v3 Pro + Credit
#  @copyright 2014 Christian Ledermann
#  @copyright 2015 Andrew Miller
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
#

import hashlib
from dogpile.cache import make_region
import json

# from dogpile.cache.proxy import ProxyBackend
# from requests import Response
# from urlparse import urlsplit
#
# class HttpProxy(ProxyBackend):
#     def set(self, key, value):
#         # value should be a http response object
#         assert isinstance(value, Response)
#         value = value.json()
#         params = value.url
#         self.proxied.set(key, value)


def kwargs_key_generator(namespace, fn, **kw):
    fname = fn.__name__
    def generate_key(*args, **kwargs):
        args_str = "_".join(str(s) for s in args)
        kwargs_str = json.dumps(kwargs)
        key = '{}_{}:{}_{}'.format(namespace, fname, args_str, kwargs_str)
        hashkey = hashlib.md5(key.encode('utf-8'))
        return hashkey.hexdigest()
    return generate_key

dp_region = make_region(name='duedilv3', function_key_generator = kwargs_key_generator)


def configure_cache(backend='dogpile.cache.pylibmc', expiration_time=86400, **kwargs):
    if not kwargs:
        kwargs = {
            'url': ["127.0.0.1"],
        }
    return dp_region.configure(
        backend,
        expiration_time = expiration_time, # 1 day
        arguments = kwargs
    )
