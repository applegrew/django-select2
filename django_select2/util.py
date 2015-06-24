# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

import datetime
import hashlib
import logging
import re
import threading

from django.utils.six import binary_type, text_type

from . import __ENABLE_MULTI_PROCESS_SUPPORT as ENABLE_MULTI_PROCESS_SUPPORT
from . import __GENERATE_RANDOM_ID as GENERATE_RANDOM_ID
from . import __MEMCACHE_HOST as MEMCACHE_HOST
from . import __MEMCACHE_PORT as MEMCACHE_PORT
from . import __MEMCACHE_TTL as MEMCACHE_TTL
from . import __SECRET_SALT as SECRET_SALT

logger = logging.getLogger(__name__)


def extract_some_key_val(dct, keys):
    """
    Gets a sub-set of a :py:obj:`dict`.

    :param dct: Source dictionary.
    :type dct: :py:obj:`dict`

    :param keys: List of subset keys, which to extract from ``dct``.
    :type keys: :py:obj:`list` or any iterable.

    :rtype: :py:obj:`dict`
    """
    edct = {}
    for k in keys:
        v = dct.get(k, None)
        if v is not None:
            edct[k] = v
    return edct


# ## Auto view helper utils ##


def synchronized(f):
    """Decorator to synchronize multiple calls to a functions."""
    f.__lock__ = threading.Lock()

    def synced_f(*args, **kwargs):
        with f.__lock__:
            return f(*args, **kwargs)

    synced_f.__doc__ = f.__doc__
    return synced_f

# Generated Id to field instance mapping.
__id_store = {}
# Field's key to generated Id mapping.
__field_store = {}

ID_PATTERN = r"[0-9_a-zA-Z.:+\- ]+"


def is_valid_id(val):
    """
    Checks if ``val`` is a valid generated Id.

    :param val: The value to check.
    :type val: :py:obj:`str`

    :rtype: :py:obj:`bool`
    """
    regex = "^%s$" % ID_PATTERN
    if re.match(regex, val) is None:
        return False
    else:
        return True


if ENABLE_MULTI_PROCESS_SUPPORT:
    from .memcache_wrapped_db_client import Client

    remote_server = Client(MEMCACHE_HOST, binary_type(MEMCACHE_PORT), MEMCACHE_TTL)


@synchronized
def register_field(key, field):
    """
    Registers an Auto field for use with :py:class:`.views.AutoResponseView`.

    :param key: The key to use while registering this field.
    :type key: :py:obj:`unicode`

    :param field: The field to register.
    :type field: :py:class:`AutoViewFieldMixin`

    :return: The generated Id for this field. If given ``key`` was already registered then the
        Id generated that time, would be returned.
    :rtype: :py:obj:`unicode`
    """
    global __id_store, __field_store

    from .fields import AutoViewFieldMixin

    if not isinstance(field, AutoViewFieldMixin):
        raise ValueError('Field must extend AutoViewFieldMixin')

    if key not in __field_store:
        # Generating id
        if GENERATE_RANDOM_ID:
            id_ = "%d:%s" % (len(__id_store), text_type(datetime.datetime.now()))
        else:
            id_ = text_type(hashlib.sha1(":".join((key, SECRET_SALT)).encode('utf-8')).hexdigest())

        __field_store[key] = id_
        __id_store[id_] = field

        if logger.isEnabledFor(logging.INFO):
            logger.info("Registering new field: %s; With actual id: %s", key, id_)

        if ENABLE_MULTI_PROCESS_SUPPORT:
            logger.info(
                "Multi process support is enabled. Adding id-key mapping to remote server.")
            remote_server.set(id_, key)
    else:
        id_ = __field_store[key]
        if logger.isEnabledFor(logging.INFO):
            logger.info("Field already registered: %s; With actual id: %s", key, id_)
    return id_


def get_field(id_):
    """
    Returns an Auto field instance registered with the given Id.

    :param id_: The generated Id the field is registered with.
    :type id_: :py:obj:`unicode`

    :rtype: :py:class:`AutoViewFieldMixin` or None
    """
    field = __id_store.get(id_, None)
    if field is None and ENABLE_MULTI_PROCESS_SUPPORT:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Id "%s" not found in this process. Looking up in remote server.', id_)
        key = remote_server.get(id_)
        if key is not None:
            id_in_current_instance = __field_store[key]
            if id_in_current_instance:
                field = __id_store.get(id_in_current_instance, None)
                if field:
                    __id_store[id_] = field
            else:
                logger.error('Unknown id "%s".', id_in_current_instance)
        else:
            logger.error('Unknown id "%s".', id_)
    return field
