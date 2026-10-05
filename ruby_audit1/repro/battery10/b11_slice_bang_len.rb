a=(1..3000).to_a; $a=a
n=Object.new; def n.to_int; $a.clear; 2000; end
a.slice!(2, n) rescue (puts "raised"); puts "b11 ok"
