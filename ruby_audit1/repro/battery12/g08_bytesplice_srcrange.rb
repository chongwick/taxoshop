$v = "b"*4000
src = Object.new
# str_range for the value operand; its to_int clears the value string
class Evil < Numeric
  def initialize(v); @v = v; end
  def val; @v; end
  def <=>(o); @v <=> (o.is_a?(Evil) ? o.val : o); end
  def to_int; $s.clear; @v; end
  def to_i; @v; end
  def coerce(o); [o, @v]; end
end
$s = "b"*4000; $s2 = $v
val = "b"*4000
r2 = Range.new(0, 10)
$s.bytesplice(0, 10, val, 0, 5) rescue (puts "raised")
puts "g08 ok"
