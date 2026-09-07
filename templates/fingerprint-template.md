## Clustering Fingerprint

**Execution context:**
Native code passes a pointer and element count to a helper that processes one or more elements.

**Trigger abstraction:**
The caller provides the address of a single scalar object while selecting a processing path that advertises multiple available elements.

**Violated invariant:**
If a callee is told that `N` elements are available through a pointer, the pointed-to storage must contain at least `N` accessible elements.

**Root-cause mechanism:**
Caller/callee contract mismatch between the actual extent of pointer-backed storage and the logical element count passed to the callee.

**Failure propagation:**
The callee trusts the supplied element count, indexes a second element, and accesses memory beyond the caller-provided scalar object.

**Failure mode:**
Out-of-bounds read from stack storage.

**Fix pattern:**
Ensure the advertised element count cannot exceed the actual extent of the supplied storage, or provide a correctly sized buffer when multi-element processing is required.

**Search pattern:**
Look for call sites that pass the address of a scalar or short local buffer together with a length/count that can exceed the backing object's actual extent, particularly where the callee indexes the pointer according to that count.

**Pattern tags:**

* `contract-mismatch`
* `pointer-length-mismatch`
* `buffer-extent-mismatch`
* `scalar-as-buffer`
* `out-of-bounds-read`

