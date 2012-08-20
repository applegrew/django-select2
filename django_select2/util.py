def convert_to_js_string_arr(lst):
    lst = ['"%s"' % l for l in lst]
    return u"[%s]" % (",".join(lst))

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
        id_ = "%d:%s" % (len(__id_store), str(datetime.datetime.now()))

        __field_store[name] = id_
        __id_store[id_] = field
    else:
        id_ = __field_store[name]
    return id_

def get_field(id_):
    return __id_store.get(id_, None)

