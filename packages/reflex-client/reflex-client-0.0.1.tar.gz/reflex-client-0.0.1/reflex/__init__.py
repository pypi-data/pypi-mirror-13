# -*- coding: utf-8 -*-


"""
Reflex image service client
~~~~~~~~~~~~~~

Reflex is an image manipulation tool aimed at web developers

:copyright: (c) 2016 by Phil Howell

"""

import hmac
import hashlib
import base64

from .clients import Client
from .mixins import TransformMixin


def transform(proxy_url, source_url, operations=None, key=False):
    if operations is None:
        operations = []
    elif isinstance(operations, basestring):
            operations = [operations]

    if key:
        operations.append("s%s" % base64.urlsafe_b64encode(hmac.new(key, msg=source_url, digestmod=hashlib.sha256).digest()))

    op_count = len(operations)
    for i, operation in enumerate(operations):
        if i != 0:
            proxy_url += ","
        proxy_url += "%s" % operation

        if i+1 == op_count:
            proxy_url += "/"

    proxy_url += source_url
    return proxy_url


def batch_transform(proxy_url, source_urls, *args, **kwargs):
    images = []

    for source_url in source_urls:
        transformed = transform(proxy_url, source_url, *args, **kwargs)
        images.append(transformed)

    return images
