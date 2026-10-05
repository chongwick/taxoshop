a=(1..3000).to_a; $a=a
e=Object.new; def e.to_int; $a.clear; 2000; end
a.insert(e, *(1..100).to_a) rescue (puts "raised"); puts "w10 ok"
