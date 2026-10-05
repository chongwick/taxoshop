a=(1..3000).to_a; $a=a
n=Object.new; def n.to_int; $a.clear; 2000; end
a[2, n] = [7,7,7] rescue (puts "raised"); puts "b10 ok"
