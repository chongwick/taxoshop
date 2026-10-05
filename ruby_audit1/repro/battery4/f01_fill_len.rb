a=(1..3000).to_a; $a=a
e=Object.new; def e.to_int; 5000; end
a.fill(7, 0, e) rescue (puts "raised"); puts "f01 ok"
