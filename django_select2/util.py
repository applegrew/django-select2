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

