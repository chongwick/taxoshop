class E
  def initialize(v); @v=v; end
  def v; @v; end
  def <=>(o); $a.clear if $a && !$d; $d=true; @v <=> (o.is_a?(E) ? o.v : o); end
end
$a = (1..3000).map{|i| E.new(i)}
b=$a; $a=b
b.max(5) rescue (puts "raised"); puts "k01 ok"
