class Evil < Numeric
  def initialize(v)=@v=v
  def val=@v
  def <=>(o); @v <=> (o.is_a?(Evil) ? o.val : o); end
  def to_int; $a.concat((1..100000).to_a); @v; end
  def to_i=@v
  def coerce(o)=[o,@v]
end
$a=(1..3000).to_a
$a.values_at(Range.new(Evil.new(10),Evil.new(2999))) rescue (puts "raised"); puts "c12 ok"
