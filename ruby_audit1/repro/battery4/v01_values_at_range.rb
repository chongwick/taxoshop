a=(1..3000).to_a; $a=a
e=Object.new; def e.to_int; $a.clear; 2900; end
a.values_at(0..e) rescue (puts "raised"); puts "v01 ok"
