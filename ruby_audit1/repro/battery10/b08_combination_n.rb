a=(1..3000).to_a; $a=a
n=Object.new; def n.to_int; $a.clear; 2; end
a.combination(n).to_a rescue (puts "raised"); puts "b08 ok"
