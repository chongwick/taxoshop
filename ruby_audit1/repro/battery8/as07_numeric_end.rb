class Evil < Numeric
  def initialize(v); @v=v; end
  def val; @v; end
  def <=>(o); @v <=> (o.is_a?(Evil) ? o.val : o); end
  def to_int; $cleared=true; $a.clear; @v; end
  def to_i; @v; end
  def coerce(o); [o, @v]; end
end
$a = (1..3000).to_a
r = Range.new(Evil.new(2900), Evil.new(2950))
p $a[r]
STDERR.puts "cleared=#{$cleared} a.len=#{$a.length}"
