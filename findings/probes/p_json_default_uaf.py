# Candidate: use-after-free in _json C encoder (encoder_listencode_obj).
#
# In the default (GIL) build, _encoder_iterate_fast_seq_lock_held borrows list
# items without INCREF (the Py_INCREF is #ifdef Py_GIL_DISABLED only). With
# check_circular=False the `markers` dict is None, so it does not hold a strong
# reference to the item either. A user `default()` callback can therefore drop
# the list's last reference to the item; after default() returns, the item is
# freed. On the error path encoder_listencode_obj still touches the freed item
# via _PyErr_FormatNote("... %T object", obj).
import json


class A:
    pass


class B:
    pass


lst = [A()]  # the only strong reference to the A() instance lives in this list


def default(o):
    if isinstance(o, A):
        lst.clear()       # drop the list's (last) reference to the A instance
        return B()        # B is also unknown -> encoded via default again
    raise TypeError("cannot encode B")  # make encoding of B fail (rv != 0)


try:
    json.dumps(lst, default=default, check_circular=False)
except Exception as exc:
    print("exception:", type(exc).__name__, exc)

print("OK p_json_default_uaf")
