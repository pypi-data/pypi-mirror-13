# -*- coding: utf-8 -*-
from .api import transform, batch_transform


class Client(object):

    def __init__(self, proxy_url, key=None):
        self.proxy_url = proxy_url
        self.key = key

    def _build_transform(self, *args, **kwargs):
        if self.key is not None and "key" not in kwargs:
            kwargs["key"] = self.key
        return (args, kwargs)

    def transform(self, source_url, *args, **kwargs):
        args, kwargs = self._build_transform(*args, **kwargs)
        return transform(self.proxy_url, source_url, *args, **kwargs)

    def batch_transform(self, source_urls, *args, **kwargs):
        args, kwargs = self._build_transform(*args, **kwargs)
        return batch_transform(self.proxy_url, source_urls, *args, **kwargs)
