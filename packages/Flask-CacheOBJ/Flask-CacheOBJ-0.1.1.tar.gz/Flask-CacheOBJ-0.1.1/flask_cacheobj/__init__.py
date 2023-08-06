# -*- coding: utf-8 -*-
"""
flask_cacheobj
~~~~~~~~~~~~~~

Flask-CacheOBJ Extension

:copyright: (c) 2016 Liwushuo Inc.
:license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import

from .api import FlaskCacheOBJ
from .msgpackable import Msgpackable
from .cache import (
    delete_cache,

    cache_obj,

    cache_hash,
    hash_del,

    cache_list,
    list_add,
    list_rem,
    list_len,

    exists,

    set_add,
    set_rem,
    set_len,

    cache_counter,
    inc_counter,
    dec_counter,
    get_counter,
    set_counter,
)

__version__ = '0.1.1'
