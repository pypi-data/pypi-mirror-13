# -*- coding: utf-8 -*-

from flask import current_app

class CacheProxy(object):

    def __getattr__(self, attr):
        if not hasattr(current_app, 'extensions') or \
           'cache' not in current_app.extensions:
            raise Exception('Cache has not been initialized')
        return getattr(current_app.extensions['cache'].mc, attr)

mc = CacheProxy()
