# Variant of Finding-01 in the dict path of the _json encoder.
# key/value are borrowed from PyDict_Next (INCREF only under Py_GIL_DISABLED).
# default(value) deletes the key from the dict, freeing the key object; the
# error-note path then touches the freed key via %R at Modules/_json.c:1741.
import json


# Uniquely allocated, non-interned string key; the dict is its only referent.
key = "".join(["json_uaf_key_", str(id(object())), "_end"])


class Unknown:
    pass


d = {key: Unknown()}
del key  # now only d holds the key string


def default(o):
    # encoder has already emitted the key and released `keystr`; the raw `key`
    # pointer is now held only by `d`. Clearing d frees the key string.
    d.clear()
    raise TypeError("cannot encode value")  # force error path (rv != 0)


try:
    json.dumps(d, default=default, check_circular=False, sort_keys=False)
except Exception as exc:
    print("exception:", type(exc).__name__, exc)

print("OK p_json_dict_default_uaf")
