class Evil < Numeric
  def initialize(v); @v = v; end
  def val; @v; end
  def <=>(o); @v <=> (o.is_a?(Evil) ? o.val : o); end
  def to_int; $s.clear; @v; end
  def to_i; @v; end
  def coerce(o); [o, @v]; end
end
$s = "a"*4000
$s[Range.new(Evil.new(3900), Evil.new(3950))] rescue (puts "raised")
puts "g06 ok"
