class C < Numeric
  def initialize(v); @v=v; end
  def v; @v; end
  def <=>(o); @v <=> (o.is_a?(C) ? o.v : o); end
  def to_int; 5; end
  def coerce(o); [o,@v]; end
end
5.clamp(C.new(0), C.new(10)) rescue (puts "raised"); puts "k07 ok"
