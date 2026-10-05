class Evil < Numeric
  def initialize(v); @v = v; end
  def val; @v; end
  def <=>(o); @v <=> (o.is_a?(Evil) ? o.val : o); end
  def to_int; $a.clear; @v; end
  def to_i; @v; end
  def coerce(o); [o, @v]; end
end
$a = (1..3000).to_a
$a[Range.new(Evil.new(2900), Evil.new(2950))] = [7]
puts "q03 ok"
