import types
import logging

from django.utils.html import escape
from django.utils.encoding import force_unicode

logger = logging.getLogger(__name__)

def render_js_script(inner_code):
    return u"""
    <script>
        $(function () {
            %s
        });
    </script>""" % inner_code

class JSVar(unicode):
    "Denotes a JS variable name, so it must not be quoted while rendering."
    pass

class JSFunction(JSVar):
    """
    Flags that the string is the name of a JS function. Used by Select2Mixin.render_options()
    to make sure that this string is not quoted like other strings.
    """
    pass

class JSFunctionInContext(JSVar):
    """
    Like JSFunction, this too flags the string as JS function, but with a special requirement.
    The JS function needs to be invoked in the context of the current Select2 Html DOM,
    such that 'this' inside the function refers to the source Select2 DOM.
    """
    pass

def extract_some_key_val(dct, keys):
    edct = {}
    for k in keys:
        v = dct.get(k, None)
        if v is not None:
            edct[k] = v
    return edct

def convert_py_to_js_data(val, id_):
    if type(val) == types.BooleanType:
        return u'true' if val else u'false'
    elif type(val) in [types.IntType, types.LongType, types.FloatType]:
        return force_unicode(val)
    elif isinstance(val, JSFunctionInContext):
        return u"django_select2.runInContextHelper(%s, '%s')" % (val, id_)
    elif isinstance(val, JSVar):
        return val # No quotes here
    elif isinstance(val, dict):
        return convert_dict_to_js_map(val, id_)
    elif isinstance(val, list):
        return convert_to_js_arr(val, id_)
    else:
        return u"'%s'" % force_unicode(val)

def convert_dict_to_js_map(dct, id_):
    out = u'{'
    is_first = True
    for name in dct:
        if not is_first:
            out += u", "
        else:
            is_first = False

        out += u"'%s': " % name
        out += convert_py_to_js_data(dct[name], id_)

    return out + u'}'

def convert_to_js_arr(lst, id_):
    out = u'['
    is_first = True
    for val in lst:
        if not is_first:
            out += u", "
        else:
            is_first = False

        out += convert_py_to_js_data(val, id_)

    return out + u']'

def convert_to_js_string_arr(lst):
    lst = [u'"%s"' % force_unicode(l) for l in lst]
    return u"[%s]" % (",".join(lst))

### Auto view helper utils ###

import re
import threading
import datetime

def synchronized(f):
    f.__lock__ = threading.Lock()

    def synced_f(*args, **kwargs):
        with f.__lock__:
            return f(*args, **kwargs)

    return synced_f


__id_store = {}
__field_store = {}

ID_PATTERN = r"[0-9_a-zA-Z.:+\- ]+"

def is_valid_id(val):
    regex = "^%s$" % ID_PATTERN
    if re.match(regex, val) is None:
        return False
    else:
        return True

@synchronized
def register_field(name, field):
    global __id_store, __field_store

    if name not in __field_store:
        # Generating id
        id_ = u"%d:%s" % (len(__id_store), unicode(datetime.datetime.now()))

        __field_store[name] = id_
        __id_store[id_] = field

        if logger.isEnabledFor(logging.INFO):
            logger.info("Registering new field: %s; With actual id: %s", name, id_)
    else:
        id_ = __field_store[name]
        if logger.isEnabledFor(logging.INFO):
            logger.info("Field already registered: %s; With actual id: %s", name, id_)
    return id_

def get_field(id_):
    return __id_store.get(id_, None)

