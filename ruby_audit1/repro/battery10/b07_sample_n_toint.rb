a=(1..3000).to_a; $a=a
n=Object.new; def n.to_int; $a.clear; 100; end
a.sample(n) rescue (puts "raised"); puts "b07 ok"
