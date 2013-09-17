import datetime
import hashlib
import logging
import re
import threading
import types

from django.utils.encoding import force_unicode

logger = logging.getLogger(__name__)


class JSVar(unicode):
    """
    A JS variable.

    This is a simple unicode string. This class type acts as a marker that this string is a JS variable name,
    so it must not be quoted by :py:func:`.convert_py_to_js_data` while rendering the JS code.
    """
    pass


class JSFunction(JSVar):
    """
    A JS function name.

    From rendering point of view, rendering this is no different from :py:class:`JSVar`. After all, a JS varible
    can refer a function instance, primitive constant or any other object. They are still all varibles.

    .. tip:: Do use this marker for JS functions. This will make the code clearer, and the purpose more easier to
        understand.
    """
    pass


class JSFunctionInContext(JSVar):
    """
    A JS function name to run in context of some other Html DOM element.

    Like :py:class:`JSFunction`, this too flags the string as JS function, but with a special requirement. The JS function
    needs to be invoked in the context of a Html DOM, such that, ``this`` inside the function refers to that DOM instead of
    ``window``.

    .. tip:: JS functions of this type are warapped inside special another JS function -- ``django_select2.runInContextHelper``.
    """
    pass


def render_js_script(inner_code):
    """
    This wraps ``inner_code`` string inside the following code block::

        <script type="text/javascript">
            $(function () {
                // inner_code here
            });
        </script>

    :rtype: :py:obj:`unicode`
    """
    return u"""
    <script type="text/javascript">
        $(function () {
            %s
        });
    </script>""" % inner_code


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


def convert_to_js_str(val):
    val = force_unicode(val).replace('\'', '\\\'')
    return u"'%s'" % val

def convert_py_to_js_data(val, id_):
    """
    Converts Python data type to JS data type.

    Practically what this means is, convert ``False`` to ``false``, ``True`` to ``true`` and so on.
    It also takes care of the conversion of :py:class:`.JSVar`, :py:class:`.JSFunction`
    and :py:class:`.JSFunctionInContext`. It takes care of recursively converting lists and dictionaries
    too.

    :param val: The Python data to convert.
    :type val: Any

    :param id_: The DOM id of the element in which context :py:class:`.JSFunctionInContext` functions
        should run. (This is not needed if ``val`` contains no :py:class:`.JSFunctionInContext`)
    :type id_: :py:obj:`str`

    :rtype: :py:obj:`unicode`
    """
    if type(val) == types.BooleanType:
        return u'true' if val else u'false'
    elif type(val) in [types.IntType, types.LongType, types.FloatType]:
        return force_unicode(val)
    elif isinstance(val, JSFunctionInContext):
        return u"django_select2.runInContextHelper(%s, '%s')" % (val, id_)
    elif isinstance(val, JSVar):
        return val  # No quotes here
    elif isinstance(val, dict):
        return convert_dict_to_js_map(val, id_)
    elif isinstance(val, list):
        return convert_to_js_arr(val, id_)
    else:
        return convert_to_js_str(val)


def convert_dict_to_js_map(dct, id_):
    """
    Converts a Python dictionary to JS map.

    :param dct: The Python dictionary to convert.
    :type dct: :py:obj:`dict`

    :param id_: The DOM id of the element in which context :py:class:`.JSFunctionInContext` functions
        should run. (This is not needed if ``dct`` contains no :py:class:`.JSFunctionInContext`)
    :type id_: :py:obj:`str`

    :rtype: :py:obj:`unicode`
    """
    out = u'{'
    is_first = True
    for name in dct:
        if not is_first:
            out += u", "
        else:
            is_first = False

        out += u"%s: " % convert_to_js_str(name)
        out += convert_py_to_js_data(dct[name], id_)

    return out + u'}'


def convert_to_js_arr(lst, id_):
    """
    Converts a Python list (or any iterable) to JS array.

    :param lst: The Python iterable to convert.
    :type lst: :py:obj:`list` or Any iterable

    :param id_: The DOM id of the element in which context :py:class:`.JSFunctionInContext` functions
        should run. (This is not needed if ``lst`` contains no :py:class:`.JSFunctionInContext`)
    :type id_: :py:obj:`str`

    :rtype: :py:obj:`unicode`
    """
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
    """
    Converts a Python list (or any iterable) of strings to JS array.

    :py:func:`convert_to_js_arr` can always be used instead of this. However, since it
    knows that it only contains strings, it cuts down on unnecessary computations.

    :rtype: :py:obj:`unicode`
    """
    lst = [convert_to_js_str(l) for l in lst]
    return u"[%s]" % (",".join(lst))


### Auto view helper utils ###

from . import __ENABLE_MULTI_PROCESS_SUPPORT as ENABLE_MULTI_PROCESS_SUPPORT, \
    __MEMCACHE_HOST as MEMCACHE_HOST, __MEMCACHE_PORT as MEMCACHE_PORT, __MEMCACHE_TTL as MEMCACHE_TTL

from . import __GENERATE_RANDOM_ID as GENERATE_RANDOM_ID, __SECRET_SALT as SECRET_SALT

def synchronized(f):
    "Decorator to synchronize multiple calls to a functions."
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
    from memcache_wrapped_db_client import Client
    remote_server = Client(MEMCACHE_HOST, str(MEMCACHE_PORT), MEMCACHE_TTL)

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

    from fields import AutoViewFieldMixin
    if not isinstance(field, AutoViewFieldMixin):
        raise ValueError('Field must extend AutoViewFieldMixin')

    if key not in __field_store:
        # Generating id
        if GENERATE_RANDOM_ID:
            id_ = u"%d:%s" % (len(__id_store), unicode(datetime.datetime.now()))
        else:
            id_ = unicode(hashlib.sha1("%s:%s" % (key, SECRET_SALT)).hexdigest())

        __field_store[key] = id_
        __id_store[id_] = field

        if logger.isEnabledFor(logging.INFO):
            logger.info("Registering new field: %s; With actual id: %s", key, id_)

        if ENABLE_MULTI_PROCESS_SUPPORT:
            logger.info("Multi process support is enabled. Adding id-key mapping to remote server.")
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

def timer_start(name):
    import sys, time
    if sys.platform == "win32":
        # On Windows, the best timer is time.clock()
        default_timer = time.clock
        multiplier = 1.0
    else:
        # On most other platforms the best timer is time.time()
        default_timer = time.time
        multiplier = 1000.0

    return (name, default_timer, multiplier, default_timer())

def timer_end(t):
    (name, default_timer, multiplier, timeS) = t
    timeE = default_timer()
    logger.debug("Time taken by %s: %0.3f ms" % (name, (timeE - timeS) * multiplier))

def timer(f):
    def inner(*args, **kwargs):
        
        t = timer_start(f.func_name)
        ret = f(*args, **kwargs)
        timer_end(t)

        return ret
    return inner
