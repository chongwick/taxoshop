class Evil < Numeric
  def initialize(v); @v=v; end
  def val; @v; end
  def <=>(o); @v <=> (o.is_a?(Evil) ? o.val : o); end
  def to_int; 5; end
  def coerce(o); [o,@v]; end
end
5.clamp(Range.new(Evil.new(0), Evil.new(10))) rescue (puts "raised"); puts "b13 ok"
