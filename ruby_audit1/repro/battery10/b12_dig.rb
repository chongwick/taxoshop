a=Array.new(100){ (1..100).to_a }; $a=a
n=Object.new; def n.to_int; $a.clear; 50; end
a.dig(n, 3) rescue (puts "raised"); puts "b12 ok"
