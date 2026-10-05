a=(1..3000).to_a; $a=a
e=Object.new; def e.to_ary; $a.clear; (1..5000).to_a; end
a.concat([9], e) rescue (puts "raised"); puts "w08 ok"
