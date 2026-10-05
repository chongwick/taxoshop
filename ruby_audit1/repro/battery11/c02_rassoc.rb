a=Array.new(3000){|i| [i,i]}; $a=a
e=Object.new; def e.to_ary; $a.clear; [1,2]; end
a[1500]=e
a.rassoc(2) rescue (puts "raised"); puts "c02 ok"
