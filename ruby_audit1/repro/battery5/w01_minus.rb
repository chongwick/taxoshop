a=(1..3000).to_a; $a=a
e=Object.new; def e.to_ary; $a.clear; [1,2,3]; end
(a - e) rescue (puts "raised"); puts "w01 ok"
