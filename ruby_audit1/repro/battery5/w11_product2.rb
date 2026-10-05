a=(1..500).to_a; $a=a
e=Object.new; def e.to_ary; $a.clear; [1,2,3]; end
a.product([1,2], e) rescue (puts "raised"); puts "w11 ok"
