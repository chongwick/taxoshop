# Finding 01 — Use-after-free in `_json` C encoder (`encoder_listencode_obj`)

- **Component:** `Modules/_json.c` (C accelerator for the `json` module, encoder path)
- **Bug class:** heap-use-after-free (read)
- **Detection:** AddressSanitizer, on CPython `f5394c257ce` (3.15.0a1), default GIL build
- **Macro taxonomy:** [Re-entrant callbacks and protocol methods](../taxos/macro_taxo/reentrant_callbacks.md)
  (also touches [Lifetime and teardown ordering](../taxos/macro_taxo/lifetime_and_teardown.md): a borrowed
  reference is used across a Python callback that drops the owner's last strong reference).
- **Novelty:** distinct from the only json micro-taxonomy on record
  ([#143544](../taxos/micro_taxo/gh_143544.md)), which is a *decoder* bug in
  `raise_errmsg` via a re-entrant `JSONDecodeError` hook. This finding is in the
  *encoder* and involves a borrowed list element across the `default()` callback.

## Root cause

When the C encoder serializes a `list`/`tuple`, `_encoder_iterate_fast_seq_lock_held()`
borrows each element from the underlying sequence:

```c
PyObject *obj = PySequence_Fast_GET_ITEM(s_fast, i);
#ifdef Py_GIL_DISABLED
    Py_INCREF(obj);            // <-- only the free-threaded build takes a strong ref
#endif
...
if (encoder_listencode_obj(s, writer, obj, indent_level, indent_cache)) {
```
(`Modules/_json.c:1915-1935`)

In a **default (GIL) build** `obj` is a plain borrowed reference into the list.

For an object of unknown type, `encoder_listencode_obj()` reaches the `default`
branch (`Modules/_json.c:1627-1675`). When `check_circular=False`, `s->markers`
is `Py_None`, so the object is **not** inserted into the markers dict and no
strong reference is taken there either. The encoder then calls the user hook:

```c
newobj = PyObject_CallOneArg(s->defaultfn, obj);   // user code runs here
...
rv = encoder_listencode_obj(s, writer, newobj, ...);
Py_DECREF(newobj);
if (rv) {
    _PyErr_FormatNote("when serializing %T object", obj);   // <-- obj may be dead
```
(`Modules/_json.c:1647-1663`)

If `default(obj)` removes `obj` from the list (dropping the list's last strong
reference), `obj` is freed as soon as the `default` frame is torn down. If the
subsequent encoding of `newobj` then fails (`rv != 0`), `_PyErr_FormatNote(...,
"%T", obj)` dereferences `Py_TYPE(obj)` on the freed object → use-after-free.

`markers` normally masks the bug because `PyDict_SetItem(s->markers, ident, obj)`
keeps `obj` alive; passing `check_circular=False` (a public, documented
`json.dumps` option) removes that accidental protection.

## Trigger (matches the reentrant-callback macro pattern)

1. Native encoder holds a **borrowed** raw reference to a list element (`obj`).
2. It calls a **Python callback** (`default(obj)`) — the re-entrancy boundary.
3. The callback mutates the owner (`list.clear()`), dropping `obj`'s last ref.
4. The callback returns a value whose encoding **fails**, so control reaches the
   error-note path.
5. The original C frame resumes and touches the freed `obj` via `%T`.

## Reproducer

`findings/repros/json_default_uaf.py`:

```python
import json

class A: pass
class B: pass

lst = [A()]                      # only strong reference to the A() instance

def default(o):
    if isinstance(o, A):
        lst.clear()              # drop the list's last reference to A
        return B()               # B is unknown -> encoded via default again
    raise TypeError("cannot encode B")   # make encoding of B fail (rv != 0)

json.dumps(lst, default=default, check_circular=False)
```

## Sanitizer evidence

Full log: `findings/logs/json_default_uaf.asan.txt`

```
==272==ERROR: AddressSanitizer: heap-use-after-free on address 0x51300002baa8 ...
READ of size 8 at 0x51300002baa8 thread T0
    #0 _Py_TYPE Include/object.h:277
    #1 unicode_fromformat_arg Objects/unicodeobject.c:3076        (%T handling)
    #2 unicode_from_format Objects/unicodeobject.c:3165
    #3 PyUnicode_FromFormatV Objects/unicodeobject.c:3199
    #4 _PyErr_FormatNote Python/errors.c:1259
    #5 encoder_listencode_obj Modules/_json.c:1663
    #6 _encoder_iterate_fast_seq_lock_held Modules/_json.c:1929
    #7 encoder_listencode_list Modules/_json.c:1991
    #8 encoder_listencode_obj Modules/_json.c:1617
    #9 encoder_call Modules/_json.c:1483
...
freed by thread T0 here:
    #1 subtype_dealloc Objects/typeobject.c:2853
    #3 Py_DECREF_MORTAL / PyStackRef_XCLOSE
    #5 _PyFrame_ClearLocals Python/frame.c:101    (the default() frame teardown)
```

## Sibling loops (same root cause)

The identical "borrowed item, INCREF only under `Py_GIL_DISABLED`" pattern appears
in all three encoder iteration helpers, so a complete fix must cover each:

- `_encoder_iterate_fast_seq_lock_held` (list/tuple) — `Modules/_json.c:1915`
  → freed access at `:1663` via `%T` (Finding-01 primary repro).
- `_encoder_iterate_mapping_lock_held` (non-dict mappings via `items()`) —
  `Modules/_json.c:1755`.
- `_encoder_iterate_dict_lock_held` (dict) — `Modules/_json.c:1796`
  → freed access at `:1741` via `%R` on the freed **key**.

Confirmed dict variant: `findings/repros/json_dict_default_uaf.py`, log
`findings/logs/json_dict_default_uaf.asan.txt`:

```
==316==ERROR: AddressSanitizer: heap-use-after-free ...
READ of size 8 ...
    #1 PyObject_Repr Objects/object.c:761
    #5 _PyErr_FormatNote Python/errors.c:1259
    #6 encoder_encode_key_value Modules/_json.c:1741
    #7 _encoder_iterate_dict_lock_held Modules/_json.c:1801
    #8 encoder_listencode_dict Modules/_json.c:1880
```
Here the freed object is the dict **key** string (its only referent was the dict,
which `default()` clears); `keystr`'s temporary reference is released before the
value is encoded.

## Suggested fix

Take a strong reference to the item for the duration of the encode in the GIL
build too (move the `Py_INCREF(obj)/Py_DECREF(obj)` out of the
`#ifdef Py_GIL_DISABLED`), or avoid touching `obj` on the error-note path (format
the note before the callback, or capture the type name earlier). The minimal fix
is to hold `obj` across `encoder_listencode_obj`'s `default` branch.

## Notes / limitations

- Requires `check_circular=False`. With the default `check_circular=True`, the
  markers dict keeps `obj` alive and the bug does not manifest.
- The freed access is currently a read (`%T`), on the error path; it is still a
  memory-safety defect and is trivially reachable from pure Python.
