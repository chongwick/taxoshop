a=(1..3000).to_a; $a=a
class E; def initialize(v)=@v=v; def <=>(o); $a.clear; @v <=> (o.is_a?(E) ? o.instance_variable_get(:@v):o); end; end
b=(1..3000).map{|i| E.new(i)}
b.sort rescue (puts "raised"); puts "c10 ok"
