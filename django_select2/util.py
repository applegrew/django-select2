# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


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
