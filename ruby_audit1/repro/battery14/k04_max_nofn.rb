class E
  def initialize(v); @v=v; end
  def v; @v; end
  def <=>(o); $a.clear if $a && !$d; $d=true; @v <=> (o.is_a?(E) ? o.v : o); end
end
b = (1..3000).map{|i| E.new(i)}; $a=b
b.max rescue (puts "raised"); puts "k04 ok"
