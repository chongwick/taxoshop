# FINDING-001 — _elementtree shared-Element data race / UAF on `extra->children` (free-threaded)

- **Family:** workflow-0081 (concurrent unsynchronized access to shared mutable storage).
- **Status:** CONFIRMED (TSan, free-threaded build) **but DUP** of closed **python/cpython#157088**
  ("Element.append() can use freed child storage during concurrent clear()", CLOSED
  `not_planned`). **NOT reported as new** — see meta-note below.

## Root cause
`xml.etree.ElementTree.Element` (C `_elementtree`) stores children in `self->extra`
(`ElementObjectExtra`: `children` heap array, `length`, `allocated`). The module declares
`{Py_mod_gil, Py_MOD_GIL_NOT_USED}` (`_elementtree.c:4732`) — advertising free-threading
safety — yet contains **zero** critical sections. Concurrent access to one Element races:

- **Writer:** `SubElement`/`append` → `element_add_subelement` (`_elementtree.c:552`) writes
  `self->extra->children[length]` and increments `length`; grows via `element_resize` →
  `PyMem_Realloc(self->extra->children, …)`, which **frees/moves** the old array.
- **Readers:** `element_getitem` (`:1591`/`:1599`, `children[index]`), `element_length`
  (`:1705`, `length`), iteration, `find*`.

No common lock ⇒ (a) torn read of `length`, (b) read of `children[index]` racing the
element store, and (c) read of a `children` array that a concurrent `element_resize` has
freed ⇒ heap use-after-free. The prior fixes gh-126033 (`remove`), gh-126037 (`find*`),
gh-143200 (`__{set,get}item__`) address *single-thread reentrancy* / specific methods; they
add no locking and do not cover the append-vs-read realloc race.

## Reproducers (no ctypes)
- `repro/tsan/t_elementtree.py` — SubElement vs len/list/find (16 races).
- `repro/tsan/t_elementtree_getitem_uaf.py` — SubElement (realloc) vs `root[i]`.

## Sanitizer output (logs `logs/elementtree.tsan.txt`, `logs/elementtree_getitem.tsan.txt`)
```
WARNING: ThreadSanitizer: data race
  Write of size 8 by thread T2:
    #0 element_add_subelement Modules/_elementtree.c:552
    #1 subelement Modules/_elementtree.c:653
  Previous read of size 8 by thread T1:
    #0 element_getitem Modules/_elementtree.c:1591
    #1 element_subscr Modules/_elementtree.c:1918
SUMMARY: ThreadSanitizer: data race Modules/_elementtree.c:552 in element_add_subelement
```

## Duplicate analysis / why NOT filed
- **#157088 (CLOSED, not_planned)** already reports the same `extra`/`children` root cause
  (append vs concurrent mutation). It was closed by a maintainer who told the reporter their
  batch of free-threaded C-extension crash reports was "coming off as spam; please consolidate
  into a single issue" (see #157124). So this whole class of "share a stdlib C object across
  threads → crash" is known and deprioritized; this append-vs-getitem/len variant adds nothing
  filable. Recorded here as a confirmed sanitizer result only.
</content>
