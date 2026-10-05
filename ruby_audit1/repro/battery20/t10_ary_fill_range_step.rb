# Array#fill with ArithmeticSequence range endpoints (evil to_int)
class N < Numeric
  def initialize(v); @v=v; end
  def <=>(o); @v <=> (o.is_a?(N) ? o.instance_variable_get(:@v) : o); end
  def coerce(o); [N.new(o), self]; end
  def to_int; $a.clear; $a.replace([]); GC.start; @v; end
end
$a = (1..5000).to_a
$a.fill(0, (N.new(2900)..N.new(2950)))
puts "t10 ok"
