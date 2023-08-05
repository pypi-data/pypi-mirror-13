# -*- coding: utf-8 -*-
import hmac
import hashlib
import base64

from .exceptions import BatchError


def transform(proxy_url, source_url, operations=None, key=None):
    if operations is None:
        operations = []
    elif isinstance(operations, basestring):
            operations = [operations]

    if key is not None:
        sig = sign_transform(source_url, key)
        operations.append("s%s" % sig)

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
    try:
        source_urls.__iter__
    except AttributeError:
        raise BatchError("You probably didn't mean to do that. Please only provide iterable `source_urls`")

    images = []

    for source_url in source_urls:
        transformed = transform(proxy_url, source_url, *args, **kwargs)
        images.append(transformed)

    return images


def sign_transform(source_url, key):
    sig = base64.urlsafe_b64encode(
        hmac.new(key, msg=source_url, digestmod=hashlib.sha256).digest()
    )
    return sig
